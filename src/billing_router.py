"""
Router de Billing y Monetización de Labortrovilo
Endpoints para gestionar suscripciones, créditos y pagos
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.dependencies import get_db_session, get_current_user
from src.payments import StripeManager, get_pricing_info, PRICING
from models import User, Subscription, Transaction, SubscriptionTier, SubscriptionStatus

# Crear router
router = APIRouter(prefix="/billing", tags=["Billing"])


# ==================== SCHEMAS ====================

class CheckoutSessionRequest(BaseModel):
    """Request para crear sesión de checkout"""
    tier: str = Field(..., description="FREE, CANDIDATO_PREMIUM, HR_PRO_PLAN")
    interval: str = Field("month", description="month o year")
    success_url: Optional[str] = Field(None, description="URL de redirección exitosa")
    cancel_url: Optional[str] = Field(None, description="URL de redirección cancelada")


class CheckoutSessionResponse(BaseModel):
    """Response con URL de checkout"""
    url: str
    session_id: str


class CreditPurchaseRequest(BaseModel):
    """Request para comprar créditos API"""
    credits: int = Field(..., description="100, 500, 1000 o 5000")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class SubscriptionInfoResponse(BaseModel):
    """Response con info completa de suscripción"""
    tier: str
    status: str
    features: List[str]
    daily_search_limit: int
    daily_searches_used: int
    api_credits: int
    api_credits_used: int
    subscription_start: Optional[str]
    subscription_end: Optional[str]
    stripe_subscription_id: Optional[str]
    can_upgrade: bool
    subscription_details: Optional[dict]


class TransactionResponse(BaseModel):
    """Response para transacción"""
    id: int
    transaction_type: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    credits_purchased: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class CancelSubscriptionRequest(BaseModel):
    """Request para cancelar suscripción"""
    immediately: bool = Field(False, description="Si True, cancela inmediatamente")


class PricingInfoResponse(BaseModel):
    """Response con información de pricing"""
    tiers: dict
    api_credits: dict


# ==================== ENDPOINTS ====================

@router.get("/pricing", response_model=PricingInfoResponse)
def get_pricing():
    """
    Obtiene la información de pricing para todos los tiers y créditos
    Endpoint público - no requiere autenticación
    """
    return get_pricing_info()


@router.post("/checkout/subscription", response_model=CheckoutSessionResponse)
def create_subscription_checkout(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una sesión de Stripe Checkout para suscripción
    
    - **tier**: FREE, CANDIDATO_PREMIUM, HR_PRO_PLAN
    - **interval**: month o year
    - **success_url**: URL de redirección al completar pago
    - **cancel_url**: URL de redirección si cancela
    """
    try:
        # Validar tier
        tier = SubscriptionTier[request.tier]
        
        if tier == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FREE tier no requiere pago"
            )
        
        # Verificar que no tenga ya ese tier
        if current_user.subscription_tier == tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya tienes el tier {tier.value}"
            )
        
        # Crear sesión de checkout
        stripe_manager = StripeManager(db)
        
        success_url = request.success_url or "http://localhost:3000/billing/success"
        cancel_url = request.cancel_url or "http://localhost:3000/pricing"
        
        session = stripe_manager.create_checkout_session(
            user=current_user,
            tier=tier,
            interval=request.interval,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return session
        
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier inválido: {request.tier}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando checkout: {str(e)}"
        )


@router.post("/checkout/credits", response_model=CheckoutSessionResponse)
def create_credits_checkout(
    request: CreditPurchaseRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una sesión de checkout para comprar créditos API
    
    Solo disponible para usuarios con tier HR_PRO_PLAN
    
    - **credits**: 100, 500, 1000 o 5000
    """
    # Verificar que sea HR_PRO
    if current_user.subscription_tier != SubscriptionTier.HR_PRO_PLAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios HR_PRO pueden comprar créditos API"
        )
    
    # Validar cantidad de créditos
    if request.credits not in [100, 500, 1000, 5000]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cantidad de créditos inválida. Opciones: 100, 500, 1000, 5000"
        )
    
    try:
        stripe_manager = StripeManager(db)
        
        success_url = request.success_url or "http://localhost:3000/billing/success"
        cancel_url = request.cancel_url or "http://localhost:3000/billing"
        
        session = stripe_manager.create_credit_purchase_session(
            user=current_user,
            credits_amount=request.credits,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return session
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando checkout: {str(e)}"
        )


@router.get("/subscription", response_model=SubscriptionInfoResponse)
def get_subscription_info(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene información completa de la suscripción del usuario actual
    """
    stripe_manager = StripeManager(db)
    return stripe_manager.get_subscription_info(current_user)


@router.post("/subscription/cancel")
def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Cancela la suscripción del usuario
    
    - **immediately**: Si True, cancela inmediatamente. Si False, cancela al final del período
    """
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tienes suscripción activa para cancelar"
        )
    
    try:
        stripe_manager = StripeManager(db)
        stripe_manager.cancel_subscription(current_user, immediately=request.immediately)
        
        return {
            "message": "Suscripción cancelada exitosamente",
            "immediately": request.immediately,
            "effective_date": "Inmediatamente" if request.immediately else current_user.subscription_end_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelando suscripción: {str(e)}"
        )


@router.post("/subscription/upgrade")
def upgrade_subscription(
    new_tier: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Cambia el tier de suscripción (upgrade o downgrade)
    
    Soporta proration - se cobra/reembolsa la diferencia
    """
    try:
        tier = SubscriptionTier[new_tier]
        
        if tier == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cambiar a FREE tier. Usa /cancel en su lugar"
            )
        
        if current_user.subscription_tier == tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya tienes el tier {tier.value}"
            )
        
        stripe_manager = StripeManager(db)
        updated_sub = stripe_manager.update_subscription_tier(current_user, tier)
        
        return {
            "message": f"Suscripción actualizada a {tier.value}",
            "new_tier": tier.value,
            "new_amount": updated_sub.amount,
            "effective_immediately": True
        }
        
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier inválido: {new_tier}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando suscripción: {str(e)}"
        )


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transaction_history(
    limit: int = 50,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de transacciones del usuario
    
    - **limit**: Número máximo de transacciones (default: 50, max: 100)
    """
    if limit > 100:
        limit = 100
    
    stripe_manager = StripeManager(db)
    transactions = stripe_manager.get_transaction_history(current_user, limit=limit)
    
    return transactions


@router.get("/credits/balance")
def get_credit_balance(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el balance actual de créditos API
    
    Solo para usuarios HR_PRO
    """
    if current_user.subscription_tier != SubscriptionTier.HR_PRO_PLAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios HR_PRO tienen acceso a créditos API"
        )
    
    return {
        "api_credits": current_user.api_credits,
        "api_credits_used": current_user.api_credits_used,
        "tier": current_user.subscription_tier.value
    }


@router.get("/search-quota")
def get_search_quota(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado de la cuota de búsquedas diarias
    """
    return {
        "daily_searches": current_user.daily_searches,
        "daily_search_limit": current_user.daily_search_limit,
        "searches_remaining": max(0, current_user.daily_search_limit - current_user.daily_searches),
        "last_reset": current_user.last_search_reset.isoformat() if current_user.last_search_reset else None,
        "tier": current_user.subscription_tier.value
    }


# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/subscriptions", response_model=List[dict])
def get_all_subscriptions(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    [ADMIN] Obtiene todas las suscripciones activas
    """
    from src.auth import UserRole
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo ADMIN o SUPERUSER."
        )
    
    subscriptions = db.query(Subscription).all()
    
    return [
        {
            "id": sub.id,
            "user_id": sub.user_id,
            "tier": sub.tier.value,
            "status": sub.status.value,
            "amount": sub.amount,
            "currency": sub.currency,
            "interval": sub.interval,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "created_at": sub.created_at.isoformat()
        }
        for sub in subscriptions
    ]


@router.get("/admin/revenue")
def get_revenue_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    [ADMIN] Obtiene estadísticas de revenue
    """
    from src.auth import UserRole
    from sqlalchemy import func
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo ADMIN o SUPERUSER."
        )
    
    # Total de usuarios por tier
    users_by_tier = db.query(
        User.subscription_tier,
        func.count(User.id)
    ).group_by(User.subscription_tier).all()
    
    # Revenue mensual estimado (suscripciones activas)
    active_subs = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).all()
    
    mrr = sum(sub.amount for sub in active_subs if sub.interval == "month")
    arr = mrr * 12
    
    # Total de transacciones exitosas
    total_revenue = db.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.status == "succeeded"
    ).scalar() or 0
    
    return {
        "users_by_tier": {tier.value: count for tier, count in users_by_tier},
        "active_subscriptions": len(active_subs),
        "mrr": round(mrr, 2),
        "arr": round(arr, 2),
        "total_revenue": round(total_revenue, 2),
        "currency": "usd"
    }


if __name__ == "__main__":
    print("Router de billing cargado correctamente")
