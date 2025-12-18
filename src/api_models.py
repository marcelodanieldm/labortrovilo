"""
Modelos Pydantic para API REST de Labortrovilo
API REST Pydantic Modeloj por Labortrovilo
Pydantic Models for Labortrovilo REST API

Response schemas específicos para cada endpoint
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# MODELOS DE RESPUESTA PARA JOBS (CANDIDATO)
# ============================================================

class JobPublicResponse(BaseModel):
    """
    Respuesta pública de trabajos para CANDIDATO
    Publika laboro-respondo por KANDIDATO
    Public job response for CANDIDATO
    
    Oculta campos sensibles como hiring_intent y red_flags
    """
    id: int
    title: str
    company_name: str
    location: Optional[str] = None
    is_remote: bool
    description: Optional[str] = None
    stack: Optional[str] = None  # Tech stack como string o JSON
    seniority_level: Optional[str] = None
    salary_range: Optional[str] = None
    salary_estimate: Optional[str] = None
    url: str
    posted_date: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Respuesta paginada de lista de trabajos"""
    total: int
    page: int
    page_size: int
    jobs: List[JobPublicResponse]


# ============================================================
# MODELOS DE MARKET INTELLIGENCE (HR_PRO)
# ============================================================

class CompanyStatsResponse(BaseModel):
    """Estadísticas de una empresa"""
    company_name: str
    total_jobs: int
    avg_urgency_score: float
    active_jobs: int
    seniority_distribution: Dict[str, int]


class TechStackStatsResponse(BaseModel):
    """Estadísticas de un stack tecnológico"""
    technology: str
    job_count: int
    avg_salary_min: Optional[float] = None
    avg_salary_max: Optional[float] = None
    avg_urgency_score: float
    avg_hiring_urgency: float = Field(..., description="Promedio de hiring_urgency_score")


class MarketIntelligenceResponse(BaseModel):
    """
    Respuesta completa de market intelligence para HR_PRO
    Kompleta market-inteligenta respondo por HR_PRO
    Complete market intelligence response for HR_PRO
    
    Incluye analíticas avanzadas y campos premium
    """
    summary: Dict[str, Any] = Field(..., description="Resumen general del mercado")
    top_hiring_companies: List[CompanyStatsResponse] = Field(..., description="Empresas con más vacantes")
    tech_stack_analysis: List[TechStackStatsResponse] = Field(..., description="Análisis por tecnología")
    salary_trends: Dict[str, Any] = Field(..., description="Tendencias salariales")
    urgency_metrics: Dict[str, Any] = Field(..., description="Métricas de urgencia de contratación")
    generated_at: datetime


class JobPremiumResponse(JobPublicResponse):
    """
    Respuesta extendida para HR_PRO con campos adicionales
    Etendita respondo por HR_PRO kun kromaj kampoj
    Extended response for HR_PRO with additional fields
    """
    hiring_urgency_score: Optional[float] = None
    is_it_niche: bool
    hiring_intent: Optional[str] = None
    red_flags: Optional[str] = None  # JSON string
    ai_processed: bool
    description_hash: Optional[str] = None


# ============================================================
# MODELOS DE ADMINISTRACIÓN (ADMIN)
# ============================================================

class ScraperStatusResponse(BaseModel):
    """Estado de un scraper"""
    name: str
    status: str  # running, idle, error
    last_run: Optional[datetime] = None
    total_jobs_scraped: int
    success_rate: float
    errors_count: int
    avg_response_time: Optional[float] = None


class ScraperErrorLogResponse(BaseModel):
    """Log de error de scraper"""
    id: int
    scraper_name: str
    error_type: str
    error_message: str
    url: Optional[str] = None
    timestamp: datetime
    resolved: bool


class AdminScrapersDashboardResponse(BaseModel):
    """
    Dashboard completo de scrapers para ADMIN
    Kompleta skrapila panelo por ADMIN
    Complete scrapers dashboard for ADMIN
    """
    scrapers: List[ScraperStatusResponse]
    recent_errors: List[ScraperErrorLogResponse]
    total_jobs_in_db: int
    total_companies: int
    jobs_scraped_today: int
    jobs_scraped_this_week: int
    system_health: str  # healthy, degraded, critical


# ============================================================
# MODELOS DE SUPERUSER (BILLING Y STATS GLOBALES)
# ============================================================

class UserActivityStats(BaseModel):
    """Estadísticas de actividad de usuarios"""
    total_users: int
    active_users_today: int
    users_by_role: Dict[str, int]
    api_calls_today: int
    api_calls_this_month: int


class BillingStats(BaseModel):
    """Estadísticas de facturación"""
    total_revenue_month: float
    revenue_by_plan: Dict[str, float]
    active_subscriptions: int
    churned_users_month: int
    mrr: float = Field(..., description="Monthly Recurring Revenue")


class SystemStats(BaseModel):
    """Estadísticas globales del sistema"""
    database_size_mb: float
    api_uptime_percent: float
    avg_response_time_ms: float
    cache_hit_rate: float
    ai_processing_cost_month: float


class SuperuserBillingResponse(BaseModel):
    """
    Respuesta completa de billing y control total para SUPERUSER
    Kompleta faktura kaj totala kontrola respondo por SUPERUSER
    Complete billing and full control response for SUPERUSER
    """
    user_activity: UserActivityStats
    billing: BillingStats
    system: SystemStats
    platform_health: str
    alerts: List[str]
    generated_at: datetime


# ============================================================
# MODELOS DE DATASET (DaaS - DATA AS A SERVICE)
# ============================================================

class DatasetMetadata(BaseModel):
    """Metadatos del dataset descargable"""
    version: str
    total_records: int
    date_range_start: datetime
    date_range_end: datetime
    filters_applied: Dict[str, Any]
    generated_at: datetime


class DatasetJobResponse(BaseModel):
    """
    Job completo para dataset HR_PRO
    Kompleta laboro por HR_PRO datumaro
    Complete job for HR_PRO dataset
    
    Incluye TODOS los campos (es un producto premium)
    """
    id: int
    external_id: Optional[str] = None
    title: str
    company_name: str
    description: Optional[str] = None
    raw_description: Optional[str] = None
    stack: Optional[str] = None
    required_skills: Optional[str] = None
    seniority_level: Optional[str] = None
    salary_range: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_estimate: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool
    country: Optional[str] = None
    url: str
    source_platform: Optional[str] = None
    hiring_urgency_score: Optional[float] = None
    is_it_niche: bool
    hiring_intent: Optional[str] = None
    red_flags: Optional[str] = None
    posted_date: Optional[datetime] = None
    date_scraped: datetime
    ai_processed: bool
    
    class Config:
        from_attributes = True


class DatasetDownloadResponse(BaseModel):
    """
    Respuesta de descarga de dataset (DaaS)
    Datumara elŝuta respondo (DaaS)
    Dataset download response (DaaS)
    
    Modelo de negocio: Venta de datos validados a HR_PRO
    """
    metadata: DatasetMetadata
    jobs: List[DatasetJobResponse]


# ============================================================
# MODELOS DE AUTENTICACIÓN
# ============================================================

class LoginRequest(BaseModel):
    """Request de login"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Response de login exitoso"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any] = Field(..., description="Información básica del usuario")


# ============================================================
# MODELOS GENÉRICOS DE RESPUESTA
# ============================================================

class SuccessResponse(BaseModel):
    """Respuesta genérica de éxito"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Respuesta genérica de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ============================================================
# EJEMPLO DE USO / EKZEMPLO DE UZO / USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("📋 API Models Module - Labortrovilo")
    print("="*60)
    print("\n✓ Modelos Pydantic disponibles:")
    print("  - JobPublicResponse: Para CANDIDATO (campos públicos)")
    print("  - JobPremiumResponse: Para HR_PRO (con red_flags, hiring_intent)")
    print("  - MarketIntelligenceResponse: Analíticas para HR_PRO")
    print("  - AdminScrapersDashboardResponse: Dashboard de scrapers")
    print("  - SuperuserBillingResponse: Estadísticas globales")
    print("  - DatasetDownloadResponse: Dataset completo (DaaS)")
