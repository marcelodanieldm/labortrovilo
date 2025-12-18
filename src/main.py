"""
API REST Principal de Labortrovilo
Ĉefa REST API de Labortrovilo
Main REST API for Labortrovilo

Senior Backend Developer + Security Expert Architecture
FastAPI Application con autenticación JWT y control de roles
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from config import settings
from src.auth import (
    UserRole, 
    authenticate_user, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.dependencies import (
    require_candidato,
    require_hr_pro,
    require_admin,
    require_superuser,
    get_db_session,
    pagination_params,
    job_filter_params,
    PaginationParams,
    JobFilterParams,
    get_current_user
)
from src.api_models import (
    LoginResponse,
    JobPublicResponse,
    JobListResponse,
    JobPremiumResponse,
    MarketIntelligenceResponse,
    CompanyStatsResponse,
    TechStackStatsResponse,
    AdminScrapersDashboardResponse,
    ScraperStatusResponse,
    SuperuserBillingResponse,
    UserActivityStats,
    BillingStats,
    SystemStats,
    DatasetDownloadResponse,
    DatasetMetadata,
    DatasetJobResponse,
    SuccessResponse
)
from src.models import Job, Company
from src.database import init_db, db_manager


# ============================================================
# INICIALIZACIÓN DE FASTAPI
# ============================================================

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints de autenticación y gestión de tokens"
        },
        {
            "name": "Candidato",
            "description": "Endpoints públicos para búsqueda de trabajos (rol: CANDIDATO)"
        },
        {
            "name": "HR Professional",
            "description": "Endpoints premium con market intelligence (rol: HR_PRO)"
        },
        {
            "name": "Admin",
            "description": "Endpoints de administración de scrapers (rol: ADMIN)"
        },
        {
            "name": "Superuser",
            "description": "Endpoints de control total y billing (rol: SUPERUSER)"
        }
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENDPOINT RAÍZ / ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API
    Radika finpunkto de la API
    Root endpoint of the API
    """
    return {
        "message": "🔍 Labortrovilo API - Sistema de scraping inteligente de trabajos",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "operational"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    db_health = db_manager.health_check()
    return {
        "status": "healthy" if db_health else "unhealthy",
        "database": "connected" if db_health else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================
# AUTENTICACIÓN / AUTHENTICATION
# ============================================================

@app.post(
    "/api/v1/auth/login",
    response_model=LoginResponse,
    tags=["Authentication"],
    summary="Login de usuario",
    description="Autentica un usuario y devuelve un token JWT"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login
    Ensaluta finpunkto
    Login endpoint
    
    Usuarios de demo:
    - username: candidato, password: password123
    - username: hr_pro, password: hrpass123
    - username: admin, password: adminpass123
    - username: superuser, password: superpass123
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token = create_access_token(
        data={
            "sub": user.username,
            "email": user.email,
            "role": user.role.value
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name
        }
    )


@app.get(
    "/api/v1/auth/me",
    tags=["Authentication"],
    summary="Información del usuario actual"
)
async def get_me(current_user = Depends(get_current_user)):
    """Obtiene información del usuario actual desde el token"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }


# ============================================================
# ENDPOINTS PARA CANDIDATO (Nivel 1)
# ============================================================

@app.get(
    "/api/v1/jobs",
    response_model=JobListResponse,
    tags=["Candidato"],
    summary="Listado de trabajos (Público para CANDIDATO)",
    description="Devuelve trabajos filtrados. Oculta campos sensibles como hiring_intent y red_flags."
)
async def get_jobs(
    user = Depends(require_candidato),
    filters: JobFilterParams = Depends(job_filter_params),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db_session)
):
    """
    Lista trabajos públicos para CANDIDATO
    Listas publikajn laborojn por KANDIDATO
    Lists public jobs for CANDIDATO
    
    Campos ocultos / Kaŝitaj kampoj / Hidden fields:
    - hiring_intent
    - red_flags
    - description_hash
    """
    # Construir query base
    query = db.query(Job).filter(Job.is_active == True)
    
    # Aplicar filtros
    if filters.stack:
        query = query.filter(Job.stack.contains(filters.stack))
    
    if filters.seniority:
        query = query.filter(Job.seniority_level == filters.seniority)
    
    if filters.is_remote is not None:
        query = query.filter(Job.is_remote == filters.is_remote)
    
    if filters.min_salary:
        query = query.filter(Job.salary_min >= filters.min_salary)
    
    if filters.country:
        query = query.filter(Job.country == filters.country)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginación y obtener resultados
    jobs = query.offset(pagination.skip).limit(pagination.limit).all()
    
    # Convertir a respuesta pública (sin campos sensibles)
    jobs_response = [
        JobPublicResponse.model_validate(job) for job in jobs
    ]
    
    return JobListResponse(
        total=total,
        page=pagination.skip // pagination.limit + 1,
        page_size=len(jobs_response),
        jobs=jobs_response
    )


@app.get(
    "/api/v1/jobs/{job_id}",
    response_model=JobPublicResponse,
    tags=["Candidato"],
    summary="Detalle de un trabajo"
)
async def get_job_detail(
    job_id: int,
    user = Depends(require_candidato),
    db: Session = Depends(get_db_session)
):
    """Obtiene el detalle de un trabajo específico"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo no encontrado"
        )
    
    return JobPublicResponse.model_validate(job)


# ============================================================
# ENDPOINTS PARA HR_PRO (Nivel 2) - MARKET INTELLIGENCE
# ============================================================

@app.get(
    "/api/v1/market-intelligence",
    response_model=MarketIntelligenceResponse,
    tags=["HR Professional"],
    summary="Market Intelligence (Exclusivo HR_PRO)",
    description="Analíticas avanzadas: empresas con más vacantes, salarios por tecnología, urgency scores"
)
async def get_market_intelligence(
    user = Depends(require_hr_pro),
    db: Session = Depends(get_db_session)
):
    """
    Market Intelligence para HR_PRO
    Market-Inteligenteco por HR_PRO
    Market Intelligence for HR_PRO
    
    Incluye:
    - Top empresas contratando
    - Análisis de tech stack con salarios
    - Métricas de urgencia
    - Tendencias salariales
    """
    # 1. Resumen general
    total_jobs = db.query(func.count(Job.id)).scalar()
    active_jobs = db.query(func.count(Job.id)).filter(Job.is_active == True).scalar()
    total_companies = db.query(func.count(Company.id)).scalar()
    
    summary = {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_companies": total_companies,
        "avg_urgency_score": db.query(func.avg(Job.hiring_urgency_score)).scalar() or 0.0
    }
    
    # 2. Top empresas con más vacantes
    top_companies_data = (
        db.query(
            Job.company_name,
            func.count(Job.id).label("total_jobs"),
            func.avg(Job.hiring_urgency_score).label("avg_urgency"),
            func.count(Job.id).filter(Job.is_active == True).label("active_jobs")
        )
        .group_by(Job.company_name)
        .order_by(func.count(Job.id).desc())
        .limit(10)
        .all()
    )
    
    top_companies = [
        CompanyStatsResponse(
            company_name=row[0],
            total_jobs=row[1],
            avg_urgency_score=row[2] or 0.0,
            active_jobs=row[3] or 0,
            seniority_distribution={}  # Simplified
        )
        for row in top_companies_data
    ]
    
    # 3. Análisis de tech stack (simplificado)
    tech_stack_analysis = [
        TechStackStatsResponse(
            technology="Python",
            job_count=db.query(func.count(Job.id)).filter(Job.stack.contains("Python")).scalar() or 0,
            avg_salary_min=80000.0,
            avg_salary_max=150000.0,
            avg_urgency_score=65.5,
            avg_hiring_urgency=65.5
        ),
        TechStackStatsResponse(
            technology="JavaScript",
            job_count=db.query(func.count(Job.id)).filter(Job.stack.contains("JavaScript")).scalar() or 0,
            avg_salary_min=70000.0,
            avg_salary_max=130000.0,
            avg_urgency_score=60.0,
            avg_hiring_urgency=60.0
        )
    ]
    
    # 4. Tendencias salariales
    salary_trends = {
        "avg_min_salary": db.query(func.avg(Job.salary_min)).scalar() or 0.0,
        "avg_max_salary": db.query(func.avg(Job.salary_max)).scalar() or 0.0,
        "jobs_with_salary_info": db.query(func.count(Job.id)).filter(Job.salary_min.isnot(None)).scalar() or 0
    }
    
    # 5. Métricas de urgencia
    urgency_metrics = {
        "high_urgency_jobs": db.query(func.count(Job.id)).filter(Job.hiring_urgency_score > 70).scalar() or 0,
        "medium_urgency_jobs": db.query(func.count(Job.id)).filter(
            and_(Job.hiring_urgency_score >= 50, Job.hiring_urgency_score <= 70)
        ).scalar() or 0,
        "low_urgency_jobs": db.query(func.count(Job.id)).filter(Job.hiring_urgency_score < 50).scalar() or 0
    }
    
    return MarketIntelligenceResponse(
        summary=summary,
        top_hiring_companies=top_companies,
        tech_stack_analysis=tech_stack_analysis,
        salary_trends=salary_trends,
        urgency_metrics=urgency_metrics,
        generated_at=datetime.utcnow()
    )


@app.get(
    "/api/v1/jobs/premium",
    response_model=List[JobPremiumResponse],
    tags=["HR Professional"],
    summary="Jobs con campos premium (HR_PRO)",
    description="Incluye hiring_intent, red_flags y todos los campos de IA"
)
async def get_premium_jobs(
    user = Depends(require_hr_pro),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db_session)
):
    """
    Jobs premium para HR_PRO con TODOS los campos
    Premium-laboroj por HR_PRO kun ĈIUJ kampoj
    Premium jobs for HR_PRO with ALL fields
    """
    jobs = (
        db.query(Job)
        .filter(Job.is_active == True)
        .offset(pagination.skip)
        .limit(pagination.limit)
        .all()
    )
    
    return [JobPremiumResponse.model_validate(job) for job in jobs]


@app.get(
    "/api/v1/dataset",
    response_model=DatasetDownloadResponse,
    tags=["HR Professional"],
    summary="Descargar dataset completo (DaaS - Data as a Service)",
    description="Modelo de negocio: Descarga últimos 100 empleos validados en formato JSON"
)
async def download_dataset(
    user = Depends(require_hr_pro),
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Dataset completo para venta de datos (DaaS)
    Kompleta datumaro por vendo de datumoj (DaaS)
    Complete dataset for data selling (DaaS)
    
    Modelo de negocio premium: HR_PRO puede descargar datos estructurados
    """
    # Obtener últimos N jobs validados
    jobs = (
        db.query(Job)
        .filter(Job.ai_processed == True)
        .order_by(Job.date_scraped.desc())
        .limit(limit)
        .all()
    )
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay trabajos procesados disponibles"
        )
    
    # Metadatos del dataset
    metadata = DatasetMetadata(
        version="1.0.0",
        total_records=len(jobs),
        date_range_start=min(job.date_scraped for job in jobs),
        date_range_end=max(job.date_scraped for job in jobs),
        filters_applied={"ai_processed": True, "limit": limit},
        generated_at=datetime.utcnow()
    )
    
    # Convertir jobs a formato dataset
    dataset_jobs = [DatasetJobResponse.model_validate(job) for job in jobs]
    
    return DatasetDownloadResponse(
        metadata=metadata,
        jobs=dataset_jobs
    )


# ============================================================
# ENDPOINTS PARA ADMIN (Nivel 3) - SCRAPERS MANAGEMENT
# ============================================================

@app.get(
    "/api/v1/admin/scrapers",
    response_model=AdminScrapersDashboardResponse,
    tags=["Admin"],
    summary="Dashboard de scrapers (Exclusivo ADMIN)",
    description="Estado de scrapers, errores de logs, volumen de datos capturados"
)
async def get_scrapers_dashboard(
    user = Depends(require_admin),
    db: Session = Depends(get_db_session)
):
    """
    Dashboard de administración de scrapers
    Skrapila administra panelo
    Scrapers administration dashboard
    
    Incluye:
    - Estado de cada scraper
    - Logs de errores recientes
    - Métricas de volumen de datos
    """
    # Estadísticas de la BD
    stats = db_manager.get_stats()
    
    # Scrapers simulados (en producción, esto vendría de una tabla de logs)
    scrapers = [
        ScraperStatusResponse(
            name="LabortroviloScraper",
            status="idle",
            last_run=datetime.utcnow() - timedelta(hours=2),
            total_jobs_scraped=stats.get('total_jobs', 0),
            success_rate=0.85,
            errors_count=5,
            avg_response_time=2.5
        )
    ]
    
    # Errores recientes simulados
    recent_errors = []
    
    # Jobs scrapeados hoy y esta semana
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    jobs_today = db.query(func.count(Job.id)).filter(Job.date_scraped >= today_start).scalar() or 0
    jobs_week = db.query(func.count(Job.id)).filter(Job.date_scraped >= week_start).scalar() or 0
    
    # Salud del sistema
    system_health = "healthy" if db_manager.health_check() else "critical"
    
    return AdminScrapersDashboardResponse(
        scrapers=scrapers,
        recent_errors=recent_errors,
        total_jobs_in_db=stats.get('total_jobs', 0),
        total_companies=stats.get('total_companies', 0),
        jobs_scraped_today=jobs_today,
        jobs_scraped_this_week=jobs_week,
        system_health=system_health
    )


@app.post(
    "/api/v1/admin/scrapers/run",
    tags=["Admin"],
    summary="Ejecutar scraper manualmente"
)
async def run_scraper(
    user = Depends(require_admin),
    scraper_name: str = "LabortroviloScraper",
    urls: List[str] = []
):
    """Ejecuta un scraper manualmente (endpoint placeholder)"""
    return SuccessResponse(
        success=True,
        message=f"Scraper '{scraper_name}' ejecutado exitosamente",
        data={"urls_processed": len(urls)}
    )


# ============================================================
# ENDPOINTS PARA SUPERUSER (Nivel 4) - FULL CONTROL
# ============================================================

@app.get(
    "/api/v1/superuser/billing",
    response_model=SuperuserBillingResponse,
    tags=["Superuser"],
    summary="Billing y estadísticas globales (Exclusivo SUPERUSER)",
    description="Control total: usuarios, facturación, sistema, alertas"
)
async def get_billing_dashboard(
    user = Depends(require_superuser),
    db: Session = Depends(get_db_session)
):
    """
    Dashboard completo para SUPERUSER
    Kompleta panelo por SUPERUSER
    Complete dashboard for SUPERUSER
    
    Incluye:
    - Actividad de usuarios
    - Facturación y revenue
    - Estadísticas del sistema
    - Alertas críticas
    """
    # Actividad de usuarios (simulado)
    user_activity = UserActivityStats(
        total_users=4,  # Demo users
        active_users_today=2,
        users_by_role={
            "candidato": 1,
            "hr_pro": 1,
            "admin": 1,
            "superuser": 1
        },
        api_calls_today=127,
        api_calls_this_month=3450
    )
    
    # Billing (simulado)
    billing = BillingStats(
        total_revenue_month=5420.00,
        revenue_by_plan={
            "free": 0.0,
            "hr_pro": 4200.0,
            "enterprise": 1220.0
        },
        active_subscriptions=12,
        churned_users_month=1,
        mrr=5420.00
    )
    
    # Sistema
    stats = db_manager.get_stats()
    system = SystemStats(
        database_size_mb=15.3,
        api_uptime_percent=99.8,
        avg_response_time_ms=145.2,
        cache_hit_rate=0.78,
        ai_processing_cost_month=23.50
    )
    
    # Alertas
    alerts = []
    if stats.get('total_jobs', 0) == 0:
        alerts.append("⚠️ No hay trabajos en la base de datos")
    
    return SuperuserBillingResponse(
        user_activity=user_activity,
        billing=billing,
        system=system,
        platform_health="healthy",
        alerts=alerts,
        generated_at=datetime.utcnow()
    )


# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la API"""
    init_db()
    print("="*60)
    print("🚀 Labortrovilo API iniciada exitosamente")
    print(f"📚 Documentación: http://localhost:8000/docs")
    print("="*60)


# ============================================================
# MAIN (para ejecutar con uvicorn)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
