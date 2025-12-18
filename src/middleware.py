"""
Middleware de Rate Limiting y Control de Acceso
Controla límites de búsqueda, créditos API y estado de suscripciones
"""
from functools import wraps
from typing import Callable
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from models import User, SubscriptionTier, SubscriptionStatus
from src.dependencies import get_db_session, get_current_user
from src.payments import StripeManager


# ==================== RATE LIMITING DECORATORS ====================

def check_daily_search_limit(func: Callable):
    """
    Decorator para verificar límite diario de búsquedas
    
    Aplica solo a usuarios FREE - otros tiers tienen búsquedas ilimitadas
    Resetea el contador automáticamente cada 24 horas
    
    Uso:
        @router.get("/jobs/search")
        @check_daily_search_limit
        def search_jobs(current_user: User = Depends(get_current_user)):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extraer current_user de los kwargs
        current_user: User = kwargs.get('current_user')
        db: Session = kwargs.get('db')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Sesión de base de datos no disponible"
            )
        
        # Usuarios PREMIUM y HR_PRO tienen búsquedas ilimitadas
        if current_user.subscription_tier != SubscriptionTier.FREE:
            return await func(*args, **kwargs)
        
        # Verificar límite diario para FREE users
        stripe_manager = StripeManager(db)
        can_search = stripe_manager.check_daily_search_limit(current_user)
        
        if not can_search:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Límite de búsquedas diarias alcanzado",
                    "message": f"Has alcanzado el límite de {current_user.daily_search_limit} búsquedas diarias del tier FREE",
                    "current_searches": current_user.daily_searches,
                    "limit": current_user.daily_search_limit,
                    "reset_at": (current_user.last_search_reset + timedelta(days=1)).isoformat(),
                    "upgrade_url": "/pricing",
                    "upgrade_tier": "CANDIDATO_PREMIUM"
                }
            )
        
        # Incrementar contador de búsquedas
        stripe_manager.increment_daily_searches(current_user)
        db.commit()
        
        # Ejecutar función original
        return await func(*args, **kwargs)
    
    return wrapper


def check_api_credits(credits_required: int = 1):
    """
    Decorator para verificar y descontar créditos API
    
    Solo aplica a usuarios HR_PRO_PLAN
    Descuenta créditos automáticamente si hay suficientes
    
    Uso:
        @router.get("/api/v1/dataset/export")
        @check_api_credits(credits_required=10)
        def export_dataset(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            db: Session = kwargs.get('db')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Sesión de base de datos no disponible"
                )
            
            # Solo usuarios HR_PRO pueden usar la API
            if current_user.subscription_tier != SubscriptionTier.HR_PRO_PLAN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "API access no disponible",
                        "message": "Necesitas el tier HR_PRO_PLAN para acceder a la API",
                        "current_tier": current_user.subscription_tier.value,
                        "required_tier": "HR_PRO_PLAN",
                        "upgrade_url": "/pricing"
                    }
                )
            
            # Verificar que tenga créditos suficientes
            if current_user.api_credits < credits_required:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "Créditos insuficientes",
                        "message": f"Esta operación requiere {credits_required} créditos",
                        "current_credits": current_user.api_credits,
                        "required_credits": credits_required,
                        "missing_credits": credits_required - current_user.api_credits,
                        "buy_credits_url": "/billing/checkout/credits"
                    }
                )
            
            # Descontar créditos
            stripe_manager = StripeManager(db)
            success = stripe_manager.deduct_credits(
                user=current_user,
                credits=credits_required,
                description=f"API call: {func.__name__}"
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="No se pudieron descontar los créditos"
                )
            
            db.commit()
            
            # Agregar info de créditos a la respuesta
            response = await func(*args, **kwargs)
            
            # Si la respuesta es un dict, agregar info de créditos
            if isinstance(response, dict):
                response['_credits_info'] = {
                    'credits_used': credits_required,
                    'credits_remaining': current_user.api_credits
                }
            
            return response
        
        return wrapper
    return decorator


def check_subscription_active(func: Callable):
    """
    Decorator para verificar que la suscripción esté activa
    
    Bloquea acceso si:
    - Suscripción está en estado PAST_DUE (pago fallido)
    - Suscripción está CANCELED
    - Suscripción está INCOMPLETE
    
    Uso:
        @router.get("/intelligence/insights")
        @check_subscription_active
        def get_insights(current_user: User = Depends(get_current_user)):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user: User = kwargs.get('current_user')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        # Verificar estado de suscripción
        if current_user.subscription_status == SubscriptionStatus.PAST_DUE:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Pago pendiente",
                    "message": "Tu suscripción tiene un pago pendiente. Por favor actualiza tu método de pago.",
                    "status": "PAST_DUE",
                    "update_payment_url": "/billing/update-payment"
                }
            )
        
        if current_user.subscription_status == SubscriptionStatus.CANCELED:
            # Verificar si aún está en período de gracia
            if current_user.subscription_end_date and current_user.subscription_end_date > datetime.utcnow():
                # Todavía tiene acceso hasta el final del período
                return await func(*args, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Suscripción cancelada",
                    "message": "Tu suscripción ha sido cancelada. Renueva para continuar usando esta función.",
                    "status": "CANCELED",
                    "renew_url": "/pricing"
                }
            )
        
        if current_user.subscription_status == SubscriptionStatus.INCOMPLETE:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Suscripción incompleta",
                    "message": "Tu suscripción no se pudo completar. Por favor contacta soporte.",
                    "status": "INCOMPLETE",
                    "support_url": "/support"
                }
            )
        
        # Suscripción activa o en trial - permitir acceso
        return await func(*args, **kwargs)
    
    return wrapper


def require_tier(min_tier: SubscriptionTier):
    """
    Decorator para requerir un tier mínimo de suscripción
    
    Bloquea acceso si el usuario no tiene al menos el tier especificado
    
    Jerarquía de tiers:
    - FREE < CANDIDATO_PREMIUM < HR_PRO_PLAN
    
    Uso:
        @router.get("/red-flags")
        @require_tier(SubscriptionTier.CANDIDATO_PREMIUM)
        def get_red_flags(current_user: User = Depends(get_current_user)):
            ...
    """
    tier_hierarchy = {
        SubscriptionTier.FREE: 0,
        SubscriptionTier.CANDIDATO_PREMIUM: 1,
        SubscriptionTier.HR_PRO_PLAN: 2
    }
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
            required_tier_level = tier_hierarchy.get(min_tier, 0)
            
            if user_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Tier insuficiente",
                        "message": f"Esta función requiere al menos {min_tier.value}",
                        "current_tier": current_user.subscription_tier.value,
                        "required_tier": min_tier.value,
                        "upgrade_url": "/pricing"
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ==================== FUNCIONES AUXILIARES ====================

def calculate_credit_cost(operation: str, record_count: int = 1) -> int:
    """
    Calcula el costo en créditos según la operación
    
    Pricing:
    - 1 crédito por registro individual
    - 10 créditos por dataset completo (JSON/CSV export)
    - 5 créditos por análisis IA de candidato
    - 20 créditos por report de market intelligence
    """
    costs = {
        "job_record": 1,
        "dataset_export": 10,
        "ai_analysis": 5,
        "market_report": 20,
        "bulk_export": lambda count: max(10, count // 10)  # 10 créditos por cada 10 registros
    }
    
    if operation == "bulk_export":
        return costs[operation](record_count)
    
    return costs.get(operation, 1) * record_count


def get_rate_limit_info(user: User) -> dict:
    """
    Retorna información completa sobre los límites del usuario
    
    Útil para mostrar en frontend
    """
    info = {
        "tier": user.subscription_tier.value,
        "status": user.subscription_status.value,
        "features": {}
    }
    
    # Búsquedas diarias
    if user.subscription_tier == SubscriptionTier.FREE:
        info["features"]["daily_searches"] = {
            "limit": user.daily_search_limit,
            "used": user.daily_searches,
            "remaining": max(0, user.daily_search_limit - user.daily_searches),
            "reset_at": (user.last_search_reset + timedelta(days=1)).isoformat() if user.last_search_reset else None
        }
    else:
        info["features"]["daily_searches"] = {
            "limit": "unlimited",
            "used": user.daily_searches,
            "remaining": "unlimited"
        }
    
    # Créditos API
    if user.subscription_tier == SubscriptionTier.HR_PRO_PLAN:
        info["features"]["api_credits"] = {
            "balance": user.api_credits,
            "used": user.api_credits_used,
            "can_use_api": user.api_credits > 0
        }
    else:
        info["features"]["api_credits"] = {
            "balance": 0,
            "available": False,
            "message": "Upgrade a HR_PRO_PLAN para acceder a la API"
        }
    
    # Features por tier
    if user.subscription_tier == SubscriptionTier.FREE:
        info["features"]["available"] = [
            "Búsquedas básicas (5/día)",
            "Visualización de trabajos",
            "Filtros básicos"
        ]
        info["features"]["blocked"] = [
            "Alertas en tiempo real",
            "Red Flags IA",
            "Filtros avanzados",
            "API access",
            "Datasets export"
        ]
    
    elif user.subscription_tier == SubscriptionTier.CANDIDATO_PREMIUM:
        info["features"]["available"] = [
            "Búsquedas ilimitadas",
            "Alertas en tiempo real",
            "Red Flags IA",
            "Favoritos",
            "Filtros avanzados",
            "Intelligence Insights"
        ]
        info["features"]["blocked"] = [
            "API access",
            "Datasets export (JSON/CSV)",
            "Market Intelligence reports"
        ]
    
    else:  # HR_PRO_PLAN
        info["features"]["available"] = [
            "Todo de PREMIUM",
            "API access",
            f"{user.api_credits} créditos API",
            "Datasets export",
            "Hiring Signals",
            "Market Intelligence",
            "Bright Data integration"
        ]
        info["features"]["blocked"] = []
    
    return info


# ==================== RATE LIMIT RESPONSES ====================

class RateLimitResponse:
    """
    Respuestas estandarizadas para rate limiting
    """
    
    @staticmethod
    def daily_limit_exceeded(user: User):
        """Límite diario de búsquedas alcanzado"""
        return {
            "error": "DAILY_LIMIT_EXCEEDED",
            "message": f"Has alcanzado el límite de {user.daily_search_limit} búsquedas diarias",
            "current_searches": user.daily_searches,
            "limit": user.daily_search_limit,
            "reset_at": (user.last_search_reset + timedelta(days=1)).isoformat(),
            "upgrade_to": "CANDIDATO_PREMIUM",
            "upgrade_url": "/pricing"
        }
    
    @staticmethod
    def insufficient_credits(user: User, required: int):
        """Créditos insuficientes"""
        return {
            "error": "INSUFFICIENT_CREDITS",
            "message": f"Esta operación requiere {required} créditos",
            "current_credits": user.api_credits,
            "required_credits": required,
            "missing_credits": required - user.api_credits,
            "buy_credits_url": "/billing/checkout/credits"
        }
    
    @staticmethod
    def tier_required(user: User, required_tier: str):
        """Tier insuficiente"""
        return {
            "error": "TIER_REQUIRED",
            "message": f"Esta función requiere {required_tier}",
            "current_tier": user.subscription_tier.value,
            "required_tier": required_tier,
            "upgrade_url": "/pricing"
        }
    
    @staticmethod
    def subscription_inactive(user: User):
        """Suscripción inactiva"""
        return {
            "error": "SUBSCRIPTION_INACTIVE",
            "message": "Tu suscripción está inactiva",
            "status": user.subscription_status.value,
            "renew_url": "/billing"
        }


if __name__ == "__main__":
    print("Middleware de rate limiting cargado correctamente")
    print("\nDecorators disponibles:")
    print("- @check_daily_search_limit")
    print("- @check_api_credits(credits_required=N)")
    print("- @check_subscription_active")
    print("- @require_tier(SubscriptionTier.XXX)")
