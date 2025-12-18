"""
Modelos de Base de Datos para Labortrovilo / Datumbazaj Modeloj por Labortrovilo
Senior Data Engineer Architecture - SQLAlchemy ORM Models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship, declarative_base

# Clase base para todos los modelos / Baza klaso por ĉiuj modeloj
Base = declarative_base()


class Company(Base):
    """
    Tabla de Empresas / Kompania Tabelo / Companies Table
    Almacena información agregada sobre empresas reclutadoras
    """
    __tablename__ = "companies"
    
    # Campos principales / Ĉefaj kampoj / Main fields
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único de empresa")
    name = Column(String(255), nullable=False, unique=True, index=True, comment="Nombre de la empresa")
    
    # Métricas de empresa / Kompaniaj metrikoj / Company metrics
    growth_score = Column(Float, nullable=True, comment="Puntuación de crecimiento 0-100")
    industry = Column(String(100), nullable=True, comment="Industria o sector")
    company_size = Column(String(50), nullable=True, comment="Tamaño: startup, medium, enterprise")
    
    # Metadatos / Metadatumoj / Metadata
    website = Column(String(500), nullable=True, comment="Sitio web corporativo")
    founded_year = Column(Integer, nullable=True, comment="Año de fundación")
    headquarters = Column(String(200), nullable=True, comment="Ubicación de sede principal")
    
    # Campos de auditoría / Kontrolkampoj / Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True, comment="Última vez que se scrapeó")
    
    # Relaciones / Rilatoj / Relationships
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}')>"


class Job(Base):
    """
    Tabla de Ofertas de Trabajo / Laboroferta Tabelo / Jobs Table
    Almacena todas las ofertas de trabajo scrapeadas con metadatos enriquecidos
    """
    __tablename__ = "jobs"
    
    # Identificadores / Identigoj / Identifiers
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único de trabajo")
    external_id = Column(String(255), nullable=True, index=True, comment="ID externo del ATS")
    
    # Información básica del trabajo / Baza laborinformo / Basic job info
    title = Column(String(255), nullable=False, index=True, comment="Título del puesto")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company_name = Column(String(255), nullable=False, comment="Nombre de empresa (denormalizado)")
    
    # Descripción y detalles / Priskribo kaj detaloj / Description and details
    description = Column(Text, nullable=True, comment="Descripción completa del trabajo")
    raw_description = Column(Text, nullable=True, comment="HTML/texto sin procesar")
    
    # Stack tecnológico / Teknologia stako / Tech stack
    stack = Column(Text, nullable=True, comment="Stack tecnológico como JSON o CSV")
    required_skills = Column(Text, nullable=True, comment="Habilidades requeridas")
    nice_to_have_skills = Column(Text, nullable=True, comment="Habilidades deseables")
    
    # Compensación / Kompensacio / Compensation
    salary_range = Column(String(100), nullable=True, comment="Rango salarial como string")
    salary_min = Column(Float, nullable=True, comment="Salario mínimo numérico")
    salary_max = Column(Float, nullable=True, comment="Salario máximo numérico")
    salary_currency = Column(String(10), nullable=True, default="USD", comment="Moneda del salario")
    
    # Ubicación / Loko / Location
    location = Column(String(200), nullable=True, comment="Ubicación del trabajo")
    is_remote = Column(Boolean, default=False, comment="¿Es trabajo remoto?")
    remote_policy = Column(String(50), nullable=True, comment="Política: full_remote, hybrid, onsite")
    country = Column(String(100), nullable=True, index=True, comment="País")
    city = Column(String(100), nullable=True, comment="Ciudad")
    
    # URL y fuente / URL kaj fonto / URL and source
    url = Column(String(500), nullable=False, unique=True, index=True, comment="URL única de la oferta")
    source_platform = Column(String(100), nullable=True, comment="ATS: greenhouse, lever, etc")
    
    # 🎯 CAMPOS DIFERENCIADORES / DISTINGAJ KAMPOJ / DIFFERENTIATING FIELDS
    hiring_urgency_score = Column(
        Float, 
        nullable=True, 
        default=0.0,
        comment="Score 0-100: urgencia de contratación basada en señales"
    )
    is_it_niche = Column(
        Boolean, 
        default=False, 
        comment="¿Es un nicho especializado de IT? (ej: blockchain, quantum)"
    )
    
    # 🤖 CAMPOS PROCESADOS POR IA / AI-TRAKTITAJ KAMPOJ / AI-PROCESSED FIELDS
    seniority_level = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Nivel: Intern, Junior, Mid, Senior, Lead, C-Level"
    )
    salary_estimate = Column(
        String(100),
        nullable=True,
        comment="Estimación salarial generada por IA si no está explícita"
    )
    hiring_intent = Column(
        String(50),
        nullable=True,
        comment="Intención: growth (crecimiento) o replacement (reemplazo)"
    )
    red_flags = Column(
        Text,
        nullable=True,
        comment="JSON array de problemas potenciales identificados por IA"
    )
    ai_processed = Column(
        Boolean,
        default=False,
        index=True,
        comment="¿Ha sido procesado por el módulo de IA?"
    )
    ai_processed_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp de procesamiento por IA"
    )
    description_hash = Column(
        String(64),
        nullable=True,
        index=True,
        comment="Hash SHA256 de la descripción para caché"
    )
    
    # Metadatos temporales / Tempaj metadatumoj / Temporal metadata
    posted_date = Column(DateTime, nullable=True, comment="Fecha de publicación original")
    date_scraped = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Fecha de scraping")
    last_verified = Column(DateTime, nullable=True, comment="Última verificación de vigencia")
    is_active = Column(Boolean, default=True, index=True, comment="¿Oferta aún activa?")
    
    # Campos de auditoría / Kontrolkampoj / Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    scraping_errors = Column(Integer, default=0, comment="Contador de errores de scraping")
    
    # Relaciones / Rilatoj / Relationships
    company = relationship("Company", back_populates="jobs")
    
    # Índices compuestos para optimización / Komponitaj indeksoj / Composite indexes
    __table_args__ = (
        Index('idx_job_company_active', 'company_id', 'is_active'),
        Index('idx_job_location_remote', 'country', 'is_remote'),
        Index('idx_job_posted_scraped', 'posted_date', 'date_scraped'),
        Index('idx_job_urgency', 'hiring_urgency_score'),
        Index('idx_job_niche', 'is_it_niche'),
    )
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company_name}', urgency={self.hiring_urgency_score})>"
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario / Konvertas al vortaro / Convert to dict"""
        return {
            'id': self.id,
            'title': self.title,
            'company_name': self.company_name,
            'location': self.location,
            'salary_range': self.salary_range,
            'url': self.url,
            'hiring_urgency_score': self.hiring_urgency_score,
            'is_it_niche': self.is_it_niche,
            'is_remote': self.is_remote,
            'date_scraped': self.date_scraped.isoformat() if self.date_scraped else None
        }
