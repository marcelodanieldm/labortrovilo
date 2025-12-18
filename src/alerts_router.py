"""
Router de Alertas de Labortrovilo
Endpoints para configuración de alertas personalizadas por usuarios
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.dependencies import get_db_session, get_current_user
from src.auth import UserRole
from models import User, AlertConfig, Notification, NotificationChannel, NotificationFrequency
from pydantic import BaseModel, Field, validator

# Crear router
router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ==================== SCHEMAS ====================

class AlertConfigBase(BaseModel):
    """Schema base para configuración de alertas"""
    tech_stack: Optional[List[str]] = Field(None, description="Tecnologías de interés")
    keywords: Optional[List[str]] = Field(None, description="Palabras clave en título/descripción")
    salary_min: Optional[int] = Field(None, ge=0, description="Salario mínimo")
    salary_max: Optional[int] = Field(None, ge=0, description="Salario máximo")
    modality: Optional[str] = Field(None, description="Modalidad (remoto, híbrido, presencial)")
    channels: List[str] = Field(default=["EMAIL"], description="Canales de notificación")
    frequency: str = Field(default="DAILY", description="Frecuencia de alertas")
    market_signals_enabled: bool = Field(default=False, description="Recibir señales de mercado")
    golden_leads_only: bool = Field(default=False, description="Solo Golden Leads")
    slack_webhook_url: Optional[str] = Field(None, description="Webhook de Slack")
    discord_webhook_url: Optional[str] = Field(None, description="Webhook de Discord")
    
    @validator('channels')
    def validate_channels(cls, v):
        """Valida que los canales sean válidos"""
        valid_channels = ['EMAIL', 'SLACK', 'DISCORD']
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f"Canal inválido: {channel}. Válidos: {valid_channels}")
        return v
    
    @validator('frequency')
    def validate_frequency(cls, v):
        """Valida que la frecuencia sea válida"""
        valid_frequencies = ['IMMEDIATE', 'HOURLY', 'DAILY', 'WEEKLY']
        if v not in valid_frequencies:
            raise ValueError(f"Frecuencia inválida: {v}. Válidas: {valid_frequencies}")
        return v
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        """Valida que salary_max >= salary_min"""
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v < values['salary_min']:
                raise ValueError("salary_max debe ser mayor o igual que salary_min")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "tech_stack": ["Python", "FastAPI", "React"],
                "keywords": ["senior", "lead"],
                "salary_min": 80000,
                "salary_max": 150000,
                "modality": "remoto",
                "channels": ["EMAIL", "SLACK"],
                "frequency": "DAILY",
                "market_signals_enabled": True,
                "golden_leads_only": False,
                "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
            }
        }


class AlertConfigCreate(AlertConfigBase):
    """Schema para crear configuración de alertas"""
    pass


class AlertConfigUpdate(BaseModel):
    """Schema para actualizar configuración de alertas (campos opcionales)"""
    tech_stack: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    modality: Optional[str] = None
    channels: Optional[List[str]] = None
    frequency: Optional[str] = None
    market_signals_enabled: Optional[bool] = None
    golden_leads_only: Optional[bool] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    is_active: Optional[bool] = None


class AlertConfigResponse(AlertConfigBase):
    """Schema de respuesta para configuración de alertas"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class NotificationResponse(BaseModel):
    """Schema de respuesta para notificaciones"""
    id: int
    user_id: int
    job_id: Optional[int]
    notification_type: str
    title: str
    message: str
    channel: str
    is_sent: bool
    sent_at: Optional[datetime]
    is_golden_lead: bool
    urgency_score: Optional[float]
    extra_data: Optional[dict]
    created_at: datetime
    
    class Config:
        orm_mode = True


class NotificationListResponse(BaseModel):
    """Schema de respuesta para lista de notificaciones"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class AlertStatsResponse(BaseModel):
    """Schema de respuesta para estadísticas de alertas"""
    total_notifications: int
    notifications_sent: int
    notifications_pending: int
    golden_leads_count: int
    last_alert_sent: Optional[datetime]
    active_config: bool


# ==================== ENDPOINTS ====================

@router.post("/config", response_model=AlertConfigResponse, status_code=status.HTTP_201_CREATED)
def create_alert_config(
    config_data: AlertConfigCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea o actualiza la configuración de alertas del usuario
    
    - **tech_stack**: Lista de tecnologías de interés (ej: ["Python", "React"])
    - **keywords**: Palabras clave en título/descripción
    - **salary_min/max**: Rango salarial de interés
    - **channels**: Canales de notificación (EMAIL, SLACK, DISCORD)
    - **frequency**: Frecuencia de alertas (IMMEDIATE, HOURLY, DAILY, WEEKLY)
    """
    # Verificar si ya existe configuración
    existing_config = db.query(AlertConfig).filter(
        AlertConfig.user_id == current_user.id
    ).first()
    
    if existing_config:
        # Actualizar configuración existente
        for field, value in config_data.dict(exclude_unset=True).items():
            # Convertir listas a JSON strings para campos JSON
            if field in ['tech_stack', 'keywords', 'channels']:
                value = json.dumps(value) if value else None
            setattr(existing_config, field, value)
        
        existing_config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_config)
        
        return existing_config
    
    # Crear nueva configuración
    import json
    
    new_config = AlertConfig(
        user_id=current_user.id,
        tech_stack=json.dumps(config_data.tech_stack) if config_data.tech_stack else None,
        keywords=json.dumps(config_data.keywords) if config_data.keywords else None,
        salary_min=config_data.salary_min,
        salary_max=config_data.salary_max,
        modality=config_data.modality,
        channels=json.dumps(config_data.channels),
        frequency=NotificationFrequency[config_data.frequency],
        market_signals_enabled=config_data.market_signals_enabled,
        golden_leads_only=config_data.golden_leads_only,
        slack_webhook_url=config_data.slack_webhook_url,
        discord_webhook_url=config_data.discord_webhook_url,
        is_active=True
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return new_config


@router.get("/config", response_model=AlertConfigResponse)
def get_alert_config(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la configuración de alertas del usuario actual
    """
    config = db.query(AlertConfig).filter(
        AlertConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes configuración de alertas. Crea una primero."
        )
    
    return config


@router.put("/config/{config_id}", response_model=AlertConfigResponse)
def update_alert_config(
    config_id: int,
    config_update: AlertConfigUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza la configuración de alertas del usuario
    """
    config = db.query(AlertConfig).filter(
        and_(
            AlertConfig.id == config_id,
            AlertConfig.user_id == current_user.id
        )
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de alertas no encontrada"
        )
    
    # Actualizar campos
    import json
    update_data = config_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            # Convertir listas a JSON strings
            if field in ['tech_stack', 'keywords', 'channels'] and isinstance(value, list):
                value = json.dumps(value)
            # Convertir frequency a enum
            elif field == 'frequency':
                value = NotificationFrequency[value]
            
            setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/config/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_config(
    config_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina la configuración de alertas del usuario
    """
    config = db.query(AlertConfig).filter(
        and_(
            AlertConfig.id == config_id,
            AlertConfig.user_id == current_user.id
        )
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de alertas no encontrada"
        )
    
    db.delete(config)
    db.commit()
    
    return None


@router.post("/config/{config_id}/toggle", response_model=AlertConfigResponse)
def toggle_alert_config(
    config_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Activa o desactiva la configuración de alertas
    """
    config = db.query(AlertConfig).filter(
        and_(
            AlertConfig.id == config_id,
            AlertConfig.user_id == current_user.id
        )
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de alertas no encontrada"
        )
    
    config.is_active = not config.is_active
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    return config


@router.get("/notifications", response_model=NotificationListResponse)
def get_user_notifications(
    page: int = 1,
    page_size: int = 20,
    only_golden_leads: bool = False,
    only_unsent: bool = False,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de notificaciones del usuario
    
    - **page**: Número de página (default: 1)
    - **page_size**: Resultados por página (default: 20, max: 100)
    - **only_golden_leads**: Filtrar solo Golden Leads
    - **only_unsent**: Filtrar solo notificaciones no enviadas
    """
    if page_size > 100:
        page_size = 100
    
    # Query base
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    # Filtros opcionales
    if only_golden_leads:
        query = query.filter(Notification.is_golden_lead == True)
    
    if only_unsent:
        query = query.filter(Notification.is_sent == False)
    
    # Contar total
    total = query.count()
    
    # Paginación
    notifications = (
        query
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total
    )


@router.get("/stats", response_model=AlertStatsResponse)
def get_alert_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene estadísticas de alertas del usuario
    """
    # Verificar configuración
    config = db.query(AlertConfig).filter(
        AlertConfig.user_id == current_user.id
    ).first()
    
    # Estadísticas de notificaciones
    total_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    notifications_sent = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_sent == True
        )
    ).count()
    
    notifications_pending = total_notifications - notifications_sent
    
    golden_leads_count = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_golden_lead == True
        )
    ).count()
    
    last_alert = (
        db.query(Notification)
        .filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_sent == True
            )
        )
        .order_by(Notification.sent_at.desc())
        .first()
    )
    
    return AlertStatsResponse(
        total_notifications=total_notifications,
        notifications_sent=notifications_sent,
        notifications_pending=notifications_pending,
        golden_leads_count=golden_leads_count,
        last_alert_sent=last_alert.sent_at if last_alert else None,
        active_config=config.is_active if config else False
    )


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una notificación específica del historial
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    db.delete(notification)
    db.commit()
    
    return None


# ==================== ENDPOINTS ADMIN ====================

@router.get("/admin/all-configs", response_model=List[AlertConfigResponse])
def get_all_alert_configs(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    [ADMIN] Obtiene todas las configuraciones de alertas de todos los usuarios
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo ADMIN o SUPERUSER."
        )
    
    configs = db.query(AlertConfig).all()
    return configs


@router.get("/admin/stats", response_model=dict)
def get_system_alert_stats(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    [ADMIN] Obtiene estadísticas globales del sistema de alertas
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo ADMIN o SUPERUSER."
        )
    
    total_configs = db.query(AlertConfig).count()
    active_configs = db.query(AlertConfig).filter(AlertConfig.is_active == True).count()
    total_notifications = db.query(Notification).count()
    notifications_sent = db.query(Notification).filter(Notification.is_sent == True).count()
    golden_leads = db.query(Notification).filter(Notification.is_golden_lead == True).count()
    
    return {
        "total_alert_configs": total_configs,
        "active_alert_configs": active_configs,
        "total_notifications": total_notifications,
        "notifications_sent": notifications_sent,
        "notifications_pending": total_notifications - notifications_sent,
        "golden_leads_identified": golden_leads
    }
