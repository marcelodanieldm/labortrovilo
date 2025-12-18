"""
Modelos de base de datos para Labortrovilo / Datumbazaj modeloj por Labortrovilo
Define la estructura de las tablas Jobs, Companies, Users, Alerts y Notifications
Difinas la strukturon de la tabeloj Jobs, Companies, Users, Alerts kaj Notifications
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint, Boolean, Enum, JSON
from sqlalchemy.orm import relationship, declarative_base
import enum

# Clase base para todos los modelos / Baza klaso por ĉiuj modeloj
Base = declarative_base()


class Company(Base):
    """
    Representa una empresa en la base de datos / Reprezentas kompanion en la datumbazo
    Almacena información y métricas de la empresa / Stokas informojn kaj metrikojn de la kompanio
    """
    __tablename__ = "companies"
    
    # Identificador único / Unika identigilo
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Nombre de la empresa (único e indexado) / Nomo de la kompanio (unika kaj indeksita)
    name = Column(String(255), nullable=False, unique=True, index=True)
    # Puntuación de crecimiento / Kreska poentaro
    growth_score = Column(Float, nullable=True)
    # Industria a la que pertenece / Industrio al kiu apartenas
    industry = Column(String(100), nullable=True)
    # Fecha de creación / Dato de kreado
    created_at = Column(DateTime, default=datetime.utcnow)
    # Fecha de última actualización / Dato de lasta ĝisdatigo
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con trabajos / Rilato kun laboroj
    jobs = relationship("Job", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name='{self.name}', industry='{self.industry}')>"


class Job(Base):
    """
    Representa una oferta de trabajo en la base de datos / Reprezentas laboroferton en la datumbazo
    Almacena detalles del trabajo y referencia a la empresa / Stokas detalojn de la laboro kaj referencon al la kompanio
    """
    __tablename__ = "jobs"
    
    # Identificador único / Unika identigilo
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Título del trabajo / Titolo de la laboro
    title = Column(String(255), nullable=False)
    # ID de la empresa (clave foránea) / ID de la kompanio (fremda ŝlosilo)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    # Nombre de empresa (desnormalizado para acceso rápido) / Nomo de kompanio (denormaligita por rapida aliro)
    company_name = Column(String(255), nullable=False)
    # Descripción original del trabajo / Originala priskribo de la laboro
    raw_description = Column(Text, nullable=True)
    # Stack tecnológico limpio (JSON o separado por comas) / Purigita teknologia stako (JSON aŭ dividita per komoj)
    cleaned_stack = Column(Text, nullable=True)
    # Salario mínimo / Minimuma salajro
    salary_min = Column(Float, nullable=True)
    # Salario máximo / Maksimuma salajro
    salary_max = Column(Float, nullable=True)
    # URL de origen (única para evitar duplicados) / Fonta URL (unika por eviti duoblojn)
    source_url = Column(String(500), nullable=False, unique=True, index=True)
    # Fecha de publicación / Dato de publikigo
    posted_date = Column(DateTime, nullable=True)
    # Fecha de extracción / Dato de ekstraktado
    scraped_at = Column(DateTime, default=datetime.utcnow)
    # Fecha de última actualización / Dato de lasta ĝisdatigo
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con empresa / Rilato kun kompanio
    company = relationship("Company", back_populates="jobs")
    
    # Asegurar que no haya URLs duplicadas / Certigi ke ne ekzistu duoblaj URL-oj
    __table_args__ = (
        UniqueConstraint('source_url', name='uq_job_source_url'),
    )
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company_name}')>"


# Enums para roles y canales de notificación
class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema"""
    CANDIDATO = "CANDIDATO"
    HR_PRO = "HR_PRO"
    ADMIN = "ADMIN"
    SUPERUSER = "SUPERUSER"


class NotificationChannel(str, enum.Enum):
    """Canales de notificación disponibles"""
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    DISCORD = "DISCORD"


class NotificationFrequency(str, enum.Enum):
    """Frecuencia de notificaciones"""
    IMMEDIATE = "IMMEDIATE"  # Inmediato
    HOURLY = "HOURLY"  # Cada hora
    DAILY = "DAILY"  # Diario
    WEEKLY = "WEEKLY"  # Semanal


class User(Base):
    """
    Representa un usuario del sistema
    Almacena información de autenticación y preferencias
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATO, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    alert_configs = relationship("AlertConfig", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"


class AlertConfig(Base):
    """
    Configuración de alertas personalizadas por usuario
    Permite definir criterios y canales de notificación
    """
    __tablename__ = "alert_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)  # Nombre descriptivo de la alerta
    is_active = Column(Boolean, default=True)
    
    # Criterios de filtrado (almacenados como JSON)
    tech_stack = Column(JSON, nullable=True)  # Lista de tecnologías: ["React", "Python"]
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    keywords = Column(JSON, nullable=True)  # Palabras clave en título/descripción
    modality = Column(String(50), nullable=True)  # Remoto, Híbrido, Presencial
    
    # Configuración de notificación
    channels = Column(JSON, nullable=False)  # ["EMAIL", "SLACK"]
    frequency = Column(Enum(NotificationFrequency), default=NotificationFrequency.IMMEDIATE)
    
    # Para HR_PRO: Market Signals
    enable_market_signals = Column(Boolean, default=False)
    hiring_velocity_threshold = Column(Integer, default=3)  # Alertar si empresa publica X puestos en un día
    
    # Webhooks personalizados
    slack_webhook_url = Column(String(500), nullable=True)
    discord_webhook_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="alert_configs")
    
    def __repr__(self):
        return f"<AlertConfig(name='{self.name}', user_id={self.user_id})>"


class Notification(Base):
    """
    Registro de notificaciones enviadas
    Tracking de todas las notificaciones del sistema
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    
    # Tipo de notificación
    notification_type = Column(String(50), nullable=False)  # JOB_MATCH, MARKET_SIGNAL, GOLDEN_LEAD
    
    # Contenido
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Canal y estado
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Para Golden Leads
    is_golden_lead = Column(Boolean, default=False)
    urgency_score = Column(Float, nullable=True)
    
    # Extra data (metadata reservado en SQLAlchemy)
    extra_data = Column(JSON, nullable=True)  # Info adicional específica del tipo
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="notifications")
    job = relationship("Job")
    
    def __repr__(self):
        return f"<Notification(type='{self.notification_type}', user_id={self.user_id})>"
