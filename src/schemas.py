"""
Esquemas de Validación Pydantic / Pydantic Validigaj Skemoj
Senior Data Engineer Architecture - Data Validation Layer
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
from enum import Enum


class RemotePolicy(str, Enum):
    """Políticas de trabajo remoto / Fora labora politikoj"""
    FULL_REMOTE = "full_remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"


class CompanySize(str, Enum):
    """Tamaños de empresa / Kompaniaj grandecoj"""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class SourcePlatform(str, Enum):
    """Plataformas ATS conocidas / Konataj ATS-platformoj"""
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    SMARTRECRUITERS = "smartrecruiters"
    WORKABLE = "workable"
    BAMBOOHR = "bamboohr"
    JOBVITE = "jobvite"
    ICIMS = "icims"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


# ============================================================
# ESQUEMAS DE COMPANY / KOMPANIAJ SKEMOJ / COMPANY SCHEMAS
# ============================================================

class CompanyBase(BaseModel):
    """Esquema base de Company / Baza kompania skemo"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la empresa")
    growth_score: Optional[float] = Field(None, ge=0, le=100, description="Score 0-100")
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[CompanySize] = None
    website: Optional[str] = Field(None, max_length=500)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)
    headquarters: Optional[str] = Field(None, max_length=200)
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Valida que el nombre no esté vacío / Validigas ke la nomo ne estas malplena"""
        if not v or not v.strip():
            raise ValueError('Company name cannot be empty')
        return v.strip()


class CompanyCreate(CompanyBase):
    """Esquema para crear Company / Skemo por krei kompanion"""
    pass


class CompanyResponse(CompanyBase):
    """Esquema de respuesta de Company / Responda kompania skemo"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_scraped_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ESQUEMAS DE JOB / LABORAJ SKEMOJ / JOB SCHEMAS
# ============================================================

class JobBase(BaseModel):
    """Esquema base de Job / Baza labora skemo"""
    # Identificadores / Identigoj
    external_id: Optional[str] = Field(None, max_length=255)
    
    # Información básica / Baza informo
    title: str = Field(..., min_length=1, max_length=255, description="Título del trabajo")
    company_name: str = Field(..., min_length=1, max_length=255, description="Nombre de empresa")
    
    # Descripción / Priskribo
    description: Optional[str] = Field(None, description="Descripción procesada")
    raw_description: Optional[str] = Field(None, description="Descripción sin procesar")
    
    # Stack tecnológico / Teknologia stako
    stack: Optional[str] = Field(None, description="Stack como JSON o CSV")
    required_skills: Optional[str] = None
    nice_to_have_skills: Optional[str] = None
    
    # Compensación / Kompensacio
    salary_range: Optional[str] = Field(None, max_length=100)
    salary_min: Optional[float] = Field(None, ge=0, description="Salario mínimo")
    salary_max: Optional[float] = Field(None, ge=0, description="Salario máximo")
    salary_currency: str = Field(default="USD", max_length=10)
    
    # Ubicación / Loko
    location: Optional[str] = Field(None, max_length=200)
    is_remote: bool = Field(default=False)
    remote_policy: Optional[RemotePolicy] = None
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    
    # URL y fuente / URL kaj fonto
    url: str = Field(..., min_length=1, max_length=500, description="URL de la oferta")
    source_platform: Optional[SourcePlatform] = Field(default=SourcePlatform.UNKNOWN)
    
    # 🎯 CAMPOS DIFERENCIADORES / DISTINGAJ KAMPOJ
    hiring_urgency_score: float = Field(
        default=0.0, 
        ge=0.0, 
        le=100.0,
        description="Score 0-100 de urgencia de contratación"
    )
    is_it_niche: bool = Field(
        default=False,
        description="¿Es un nicho especializado de IT?"
    )
    
    # Metadatos temporales / Tempaj metadatumoj
    posted_date: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    @field_validator('title', 'company_name')
    @classmethod
    def strings_must_not_be_empty(cls, v: str) -> str:
        """Valida campos de texto / Validigas tekstajn kampojn"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Valida formato de URL / Validigas URL-formaton"""
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        v = v.strip()
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @field_validator('salary_max')
    @classmethod
    def salary_max_validation(cls, v: Optional[float], info) -> Optional[float]:
        """Valida que salary_max >= salary_min"""
        if v is not None and 'salary_min' in info.data:
            salary_min = info.data.get('salary_min')
            if salary_min is not None and v < salary_min:
                raise ValueError('salary_max must be >= salary_min')
        return v
    
    @field_validator('hiring_urgency_score')
    @classmethod
    def urgency_score_validation(cls, v: float) -> float:
        """Valida que el score esté en rango 0-100"""
        if not 0 <= v <= 100:
            raise ValueError('hiring_urgency_score must be between 0 and 100')
        return round(v, 2)


class JobCreate(JobBase):
    """Esquema para crear Job / Skemo por krei laboron"""
    company_id: Optional[int] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Senior Python Developer",
                "company_name": "TechCorp",
                "description": "We are looking for a senior developer...",
                "stack": "Python, Django, PostgreSQL, Docker",
                "salary_range": "$120k - $180k",
                "salary_min": 120000,
                "salary_max": 180000,
                "location": "Remote",
                "is_remote": True,
                "remote_policy": "full_remote",
                "url": "https://jobs.techcorp.com/python-dev",
                "hiring_urgency_score": 75.5,
                "is_it_niche": False,
                "source_platform": "greenhouse"
            }
        }
    )


class JobUpdate(BaseModel):
    """Esquema para actualizar Job / Skemo por ĝisdatigi laboron"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    hiring_urgency_score: Optional[float] = None
    last_verified: Optional[datetime] = None


class JobResponse(JobBase):
    """Esquema de respuesta de Job / Responda labora skemo"""
    id: int
    company_id: Optional[int] = None
    date_scraped: datetime
    created_at: datetime
    updated_at: datetime
    last_verified: Optional[datetime] = None
    scraping_errors: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """Respuesta paginada de lista de trabajos / Paĝigita respondo de laborlisto"""
    total: int
    page: int
    page_size: int
    jobs: List[JobResponse]
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ESQUEMAS DE SCRAPING / SKRAPAJ SKEMOJ / SCRAPING SCHEMAS
# ============================================================

class ScrapingResult(BaseModel):
    """Resultado de una operación de scraping / Rezulto de skrapoperacio"""
    success: bool
    url: str
    job_data: Optional[JobCreate] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "url": "https://jobs.example.com/dev",
                "job_data": None,
                "error_message": None,
                "timestamp": "2025-12-18T10:30:00"
            }
        }
    )


class ScrapingStats(BaseModel):
    """Estadísticas de sesión de scraping / Statistikoj de skrapa seanco"""
    total_urls: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    duplicates_found: int = 0
    saved_to_db: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    def calculate_success_rate(self) -> float:
        """Calcula tasa de éxito / Kalkulas sukcesprocenton"""
        if self.total_urls == 0:
            return 0.0
        return round((self.successful_scrapes / self.total_urls) * 100, 2)
