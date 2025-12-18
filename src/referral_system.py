"""
Sistema de Referidos - Modelo Dropbox
Cada usuario puede referir a otros usuarios y ambos reciben recompensas
"""
import secrets
import string
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.dependencies import get_db_session, get_current_user
from src.payments import StripeManager
from models import User, Transaction, SubscriptionTier

router = APIRouter(prefix="/user", tags=["Referral System"])


# ==================== SCHEMAS ====================

class ReferralInfoResponse(BaseModel):
    """Response con información del sistema de referidos"""
    referral_code: str
    referral_url: str
    total_referrals: int
    referral_credits_earned: int
    pending_referrals: int
    referred_by: Optional[dict] = None


class ReferralStatsResponse(BaseModel):
    """Estadísticas detalladas de referidos"""
    referral_code: str
    total_referrals: int
    active_referrals: int
    credits_earned: int
    referrals_this_month: int
    top_performer: bool
    leaderboard_position: Optional[int] = None


class ApplyReferralRequest(BaseModel):
    """Request para aplicar código de referido al registrarse"""
    referral_code: str = Field(..., min_length=6, max_length=20)


# ==================== CONFIGURACIÓN ====================

# Recompensas del sistema
REFERRAL_REWARDS = {
    "referrer_credits": 50,      # Créditos para quien refiere
    "referred_credits": 50,      # Créditos para quien se registra
    "referrer_days": 0,          # Días extra de premium (futuro)
    "referred_days": 0,          # Días extra de premium (futuro)
}

# Condiciones para validar referido
REFERRAL_CONDITIONS = {
    "min_activity_days": 7,      # Días mínimos de actividad
    "min_searches": 3,           # Búsquedas mínimas
    "email_verified": True,      # Email verificado
}


# ==================== ENDPOINTS ====================

@router.get("/referral", response_model=ReferralInfoResponse)
def get_referral_info(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene información del sistema de referidos del usuario actual
    
    Retorna:
    - Código de referido único
    - URL de invitación
    - Total de referidos exitosos
    - Créditos ganados
    - Quién lo refirió (si aplica)
    """
    # Generar código si no existe
    if not current_user.referral_code:
        current_user.referral_code = generate_referral_code()
        db.commit()
    
    # URL de referido
    base_url = "https://labortrovilo.com"  # TODO: Obtener de settings
    referral_url = f"{base_url}/signup?ref={current_user.referral_code}"
    
    # Info de quién lo refirió
    referred_by = None
    if current_user.referred_by_id:
        referrer = db.query(User).filter(User.id == current_user.referred_by_id).first()
        if referrer:
            referred_by = {
                "email": referrer.email,
                "full_name": referrer.full_name,
                "joined_at": current_user.created_at.isoformat()
            }
    
    # Contar referidos pendientes (registrados pero no validados)
    pending_count = len([
        r for r in current_user.referrals 
        if (datetime.utcnow() - r.created_at).days < REFERRAL_CONDITIONS["min_activity_days"]
    ])
    
    return ReferralInfoResponse(
        referral_code=current_user.referral_code,
        referral_url=referral_url,
        total_referrals=current_user.total_referrals,
        referral_credits_earned=current_user.referral_credits_earned,
        pending_referrals=pending_count,
        referred_by=referred_by
    )


@router.get("/referral/stats", response_model=ReferralStatsResponse)
def get_referral_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Estadísticas avanzadas del sistema de referidos
    Incluye leaderboard position y comparación con top performers
    """
    # Referidos del mes actual
    from datetime import timedelta
    month_ago = datetime.utcnow() - timedelta(days=30)
    referrals_this_month = len([
        r for r in current_user.referrals 
        if r.created_at >= month_ago
    ])
    
    # Referidos activos (con actividad reciente)
    active_referrals = len([
        r for r in current_user.referrals 
        if r.is_active and (datetime.utcnow() - r.updated_at).days < 30
    ])
    
    # Leaderboard position
    all_users = db.query(User).filter(User.total_referrals > 0).order_by(
        User.total_referrals.desc()
    ).all()
    
    position = None
    for idx, user in enumerate(all_users, 1):
        if user.id == current_user.id:
            position = idx
            break
    
    # Top performer (top 10%)
    top_performer = position and position <= len(all_users) * 0.1
    
    return ReferralStatsResponse(
        referral_code=current_user.referral_code,
        total_referrals=current_user.total_referrals,
        active_referrals=active_referrals,
        credits_earned=current_user.referral_credits_earned,
        referrals_this_month=referrals_this_month,
        top_performer=top_performer,
        leaderboard_position=position
    )


@router.post("/referral/apply")
def apply_referral_code(
    request: ApplyReferralRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Aplica código de referido cuando un usuario se registra
    
    Validaciones:
    - Usuario aún no ha sido referido
    - Código de referido existe
    - No puede referirse a sí mismo
    
    Recompensas:
    - 50 créditos para el referrer
    - 50 créditos para el nuevo usuario
    """
    # Validar que no tenga referido previo
    if current_user.referred_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Ya tienes un referidor asignado",
                "referred_by": current_user.referrer.email if current_user.referrer else "Unknown"
            }
        )
    
    # Buscar referrer por código
    referrer = db.query(User).filter(
        User.referral_code == request.referral_code
    ).first()
    
    if not referrer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de referido inválido"
        )
    
    # Validar que no se refiera a sí mismo
    if referrer.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes usar tu propio código de referido"
        )
    
    # Aplicar referido
    current_user.referred_by_id = referrer.id
    
    # Dar recompensas inmediatas
    stripe_manager = StripeManager(db)
    
    # Créditos para el nuevo usuario
    stripe_manager.add_credits_to_user(
        user=current_user,
        credits=REFERRAL_REWARDS["referred_credits"],
        transaction_id=f"referral_signup_{current_user.id}"
    )
    
    # Créditos para el referrer
    stripe_manager.add_credits_to_user(
        user=referrer,
        credits=REFERRAL_REWARDS["referrer_credits"],
        transaction_id=f"referral_reward_{referrer.id}"
    )
    
    # Actualizar contadores
    referrer.total_referrals += 1
    referrer.referral_credits_earned += REFERRAL_REWARDS["referrer_credits"]
    current_user.referral_credits_earned = REFERRAL_REWARDS["referred_credits"]
    
    db.commit()
    
    return {
        "message": "¡Código de referido aplicado exitosamente! 🎉",
        "rewards": {
            "credits_received": REFERRAL_REWARDS["referred_credits"],
            "referrer_name": referrer.full_name or referrer.email.split("@")[0],
            "referrer_rewarded": REFERRAL_REWARDS["referrer_credits"]
        },
        "your_referral_code": current_user.referral_code or generate_referral_code()
    }


@router.get("/referral/leaderboard")
def get_referral_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db_session)
):
    """
    Obtiene el leaderboard de top referrers
    
    Gamificación: Mostrar top 10 usuarios con más referidos exitosos
    """
    top_referrers = db.query(User).filter(
        User.total_referrals > 0
    ).order_by(
        User.total_referrals.desc()
    ).limit(limit).all()
    
    leaderboard = []
    for idx, user in enumerate(top_referrers, 1):
        leaderboard.append({
            "position": idx,
            "name": user.full_name or user.email.split("@")[0],
            "total_referrals": user.total_referrals,
            "credits_earned": user.referral_credits_earned,
            "tier": user.subscription_tier.value,
            "badge": get_referral_badge(user.total_referrals)
        })
    
    return {
        "leaderboard": leaderboard,
        "total_participants": db.query(User).filter(User.total_referrals > 0).count(),
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/referral/history")
def get_referral_history(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Historial de todos los usuarios referidos
    """
    referrals = []
    for referred_user in current_user.referrals:
        # Calcular si ya validó (cumple condiciones mínimas)
        days_active = (datetime.utcnow() - referred_user.created_at).days
        is_validated = (
            days_active >= REFERRAL_CONDITIONS["min_activity_days"] and
            referred_user.is_active
        )
        
        referrals.append({
            "id": referred_user.id,
            "email": referred_user.email,
            "full_name": referred_user.full_name,
            "joined_at": referred_user.created_at.isoformat(),
            "tier": referred_user.subscription_tier.value,
            "is_active": referred_user.is_active,
            "is_validated": is_validated,
            "days_active": days_active,
            "credits_contributed": REFERRAL_REWARDS["referrer_credits"] if is_validated else 0
        })
    
    return {
        "total_referrals": len(referrals),
        "validated_referrals": sum(1 for r in referrals if r["is_validated"]),
        "pending_referrals": sum(1 for r in referrals if not r["is_validated"]),
        "referrals": referrals
    }


# ==================== FUNCIONES AUXILIARES ====================

def generate_referral_code() -> str:
    """
    Genera código de referido único
    Formato: 8 caracteres alfanuméricos
    Ejemplo: LAB-XY7K9M2P
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(8))
    return f"LAB-{code}"


def get_referral_badge(total_referrals: int) -> str:
    """
    Retorna badge según cantidad de referidos
    Gamificación: Bronce, Plata, Oro, Platino, Diamante
    """
    if total_referrals >= 100:
        return "💎 Diamante"
    elif total_referrals >= 50:
        return "🏆 Platino"
    elif total_referrals >= 25:
        return "🥇 Oro"
    elif total_referrals >= 10:
        return "🥈 Plata"
    elif total_referrals >= 5:
        return "🥉 Bronce"
    else:
        return "⭐ Novato"


def validate_referral(referred_user: User) -> bool:
    """
    Valida si un referido cumple las condiciones mínimas
    
    Condiciones:
    - Al menos 7 días de actividad
    - Al menos 3 búsquedas realizadas
    - Email verificado (futuro)
    """
    days_active = (datetime.utcnow() - referred_user.created_at).days
    
    return (
        days_active >= REFERRAL_CONDITIONS["min_activity_days"] and
        referred_user.daily_searches >= REFERRAL_CONDITIONS["min_searches"] and
        referred_user.is_active
    )


# ==================== WEBHOOK / CRON JOB ====================

def process_pending_referrals(db: Session):
    """
    [CRON JOB] Procesa referidos pendientes de validación
    
    Se ejecuta diariamente para:
    - Validar referidos que cumplieron condiciones
    - Dar recompensas adicionales (si aplica)
    - Enviar notificaciones
    
    Ejecutar con APScheduler:
    @scheduler.scheduled_job('cron', hour=3, minute=0)
    def validate_referrals():
        process_pending_referrals(db_session)
    """
    # Buscar usuarios referidos hace 7+ días pero no validados aún
    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=REFERRAL_CONDITIONS["min_activity_days"])
    
    pending_users = db.query(User).filter(
        User.referred_by_id.isnot(None),
        User.created_at <= cutoff_date,
        User.is_active == True
    ).all()
    
    validated_count = 0
    for user in pending_users:
        if validate_referral(user):
            # Ya validó - Enviar notificación al referrer (opcional)
            referrer = user.referrer
            if referrer:
                # TODO: Enviar email/notificación
                # send_notification(referrer, f"Tu referido {user.email} ha sido validado!")
                validated_count += 1
    
    db.commit()
    
    return {
        "processed": len(pending_users),
        "validated": validated_count
    }


# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/referral/stats")
def get_admin_referral_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    [ADMIN] Estadísticas globales del sistema de referidos
    """
    from src.auth import UserRole
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo ADMIN."
        )
    
    # Métricas globales
    total_users_with_code = db.query(User).filter(User.referral_code.isnot(None)).count()
    total_referred_users = db.query(User).filter(User.referred_by_id.isnot(None)).count()
    total_credits_given = db.query(User).with_entities(
        db.func.sum(User.referral_credits_earned)
    ).scalar() or 0
    
    # Conversion rate
    conversion_rate = (total_referred_users / total_users_with_code * 100) if total_users_with_code > 0 else 0
    
    return {
        "total_users_with_referral_code": total_users_with_code,
        "total_referred_users": total_referred_users,
        "total_credits_distributed": total_credits_given,
        "conversion_rate": round(conversion_rate, 2),
        "average_referrals_per_user": round(total_referred_users / total_users_with_code, 2) if total_users_with_code > 0 else 0
    }


if __name__ == "__main__":
    print("Referral System cargado correctamente")
    print("\nEndpoints disponibles:")
    print("- GET  /user/referral")
    print("- GET  /user/referral/stats")
    print("- POST /user/referral/apply")
    print("- GET  /user/referral/leaderboard")
    print("- GET  /user/referral/history")
    print("- GET  /user/admin/referral/stats [ADMIN]")
