"""
Modelos de base de datos para Labortrovilo / Datumbazaj modeloj por Labortrovilo
Define la estructura de las tablas Jobs y Companies
Difinas la strukturon de la tabeloj Jobs kaj Companies
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

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
