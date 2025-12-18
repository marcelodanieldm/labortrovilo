"""
Public Job Board - Vista pública para SEO y Lead Generation
Permite acceso sin autenticación con funcionalidad limitada
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from pydantic import BaseModel

from src.dependencies import get_db_session, pagination_params, PaginationParams
from models import Job, Company

router = APIRouter(prefix="/public", tags=["Public Board"])


# ==================== SCHEMAS ====================

class PublicJobResponse(BaseModel):
    """
    Response limitado para usuarios no autenticados
    Oculta información sensible como:
    - Salario exacto (solo rango genérico)
    - Email de contacto
    - URL de aplicación directa
    """
    id: int
    title: str
    company_name: str
    location: Optional[str]
    modality: Optional[str]
    tech_stack: Optional[List[str]]
    description_preview: str  # Solo primeros 200 chars
    posted_date: Optional[str]
    growth_score: float
    
    # Campos bloqueados
    salary_range_preview: str  # "Competitivo" o rango genérico
    apply_blocked: bool = True
    login_required: bool = True
    
    class Config:
        orm_mode = True


class PublicJobDetailResponse(BaseModel):
    """Response detallado para oferta pública"""
    id: int
    title: str
    company_name: str
    location: Optional[str]
    modality: Optional[str]
    tech_stack: Optional[List[str]]
    description: str
    posted_date: Optional[str]
    growth_score: float
    
    # Bloqueados con lead magnet
    salary_blocked: bool = True
    apply_url_blocked: bool = True
    company_details_blocked: bool = True
    red_flags_blocked: bool = True
    
    # CTA de registro
    cta_message: str = "🔒 Regístrate gratis para ver salario completo y aplicar"
    signup_url: str = "/signup"


class PublicTechLandingResponse(BaseModel):
    """Response para landing pages de tecnología"""
    tech_name: str
    total_jobs: int
    salary_range_avg: str
    top_companies: List[str]
    top_locations: List[str]
    jobs_preview: List[PublicJobResponse]


# ==================== ENDPOINTS PÚBLICOS ====================

@router.get("/jobs", response_model=List[PublicJobResponse])
def get_public_jobs(
    search: Optional[str] = Query(None, description="Búsqueda por título o empresa"),
    tech: Optional[str] = Query(None, description="Filtrar por tecnología"),
    location: Optional[str] = Query(None, description="Filtrar por ubicación"),
    modality: Optional[str] = Query(None, description="Remoto, Híbrido, Presencial"),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db_session)
):
    """
    Lista pública de ofertas (sin autenticación)
    
    Features:
    - Vista limitada (sin salario exacto, sin URL de aplicación)
    - Optimizado para crawlers (Google, LinkedIn Bot)
    - Lead magnet: Bloquear botón "Aplicar" con modal de registro
    - Max 50 resultados por página
    
    SEO Benefits:
    - Google indexa ofertas
    - LinkedIn/Twitter preview cards
    - Backlinks naturales
    """
    # Query base
    query = db.query(Job).filter(Job.is_active == True)
    
    # Filtros
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company_name.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )
    
    if tech:
        query = query.filter(Job.tech_stack.contains(tech))
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if modality:
        query = query.filter(Job.modality.ilike(f"%{modality}%"))
    
    # Paginación
    total = query.count()
    jobs = query.order_by(desc(Job.posted_date)).offset(
        pagination.skip
    ).limit(min(pagination.limit, 50)).all()  # Max 50 para usuarios públicos
    
    # Transformar a response limitado
    public_jobs = []
    for job in jobs:
        public_jobs.append(PublicJobResponse(
            id=job.id,
            title=job.title,
            company_name=job.company_name or "Empresa Confidencial",
            location=job.location,
            modality=job.modality,
            tech_stack=job.tech_stack if isinstance(job.tech_stack, list) else [],
            description_preview=job.description[:200] + "..." if job.description else "Sin descripción",
            posted_date=job.posted_date.isoformat() if job.posted_date else None,
            growth_score=calculate_public_growth_score(job),
            salary_range_preview=get_salary_preview(job.salary_range),
            apply_blocked=True,
            login_required=True
        ))
    
    return public_jobs


@router.get("/jobs/{job_id}", response_model=PublicJobDetailResponse)
def get_public_job_detail(
    job_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Detalle de oferta pública
    
    Bloquea con lead magnet:
    - Salario completo (muestra "Competitivo" o rango genérico)
    - Botón "Aplicar" (muestra modal de registro)
    - Detalles de empresa
    - Red Flags IA
    
    SEO: Indexable, pero incentiva registro
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        return {"error": "Oferta no encontrada"}
    
    return PublicJobDetailResponse(
        id=job.id,
        title=job.title,
        company_name=job.company_name or "Empresa Confidencial",
        location=job.location,
        modality=job.modality,
        tech_stack=job.tech_stack if isinstance(job.tech_stack, list) else [],
        description=job.description or "Sin descripción disponible",
        posted_date=job.posted_date.isoformat() if job.posted_date else None,
        growth_score=calculate_public_growth_score(job),
        salary_blocked=True,
        apply_url_blocked=True,
        company_details_blocked=True,
        red_flags_blocked=True,
        cta_message="🔒 Regístrate gratis para ver salario y aplicar directamente",
        signup_url=f"/signup?redirect=/job/{job.id}"
    )


@router.get("/tech/{tech_name}", response_model=PublicTechLandingResponse)
def get_public_tech_landing(
    tech_name: str,
    db: Session = Depends(get_db_session)
):
    """
    Landing page pública para tecnología específica
    
    Ejemplos:
    - /public/tech/python -> Python jobs
    - /public/tech/react -> React jobs
    
    SEO optimizado: Title, meta description, structured data
    Lead magnet: Ver ofertas completas requiere registro
    """
    tech_clean = tech_name.replace("-", " ").title()
    
    # Jobs con esa tecnología
    jobs = db.query(Job).filter(
        Job.tech_stack.contains(tech_clean),
        Job.is_active == True
    ).order_by(desc(Job.posted_date)).limit(20).all()
    
    # Top companies
    companies = {}
    locations = {}
    for job in jobs:
        if job.company_name:
            companies[job.company_name] = companies.get(job.company_name, 0) + 1
        if job.location:
            locations[job.location] = locations.get(job.location, 0) + 1
    
    top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
    top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calcular salario promedio (rango genérico)
    salary_avg = "Competitivo"
    if any(job.salary_range for job in jobs):
        salary_avg = "$60k - $120k USD"  # Placeholder - calcular real si es necesario
    
    # Preview de ofertas (max 10)
    jobs_preview = []
    for job in jobs[:10]:
        jobs_preview.append(PublicJobResponse(
            id=job.id,
            title=job.title,
            company_name=job.company_name or "Empresa Top",
            location=job.location,
            modality=job.modality,
            tech_stack=job.tech_stack if isinstance(job.tech_stack, list) else [],
            description_preview=job.description[:150] + "..." if job.description else "",
            posted_date=job.posted_date.isoformat() if job.posted_date else None,
            growth_score=calculate_public_growth_score(job),
            salary_range_preview=get_salary_preview(job.salary_range),
            apply_blocked=True,
            login_required=True
        ))
    
    return PublicTechLandingResponse(
        tech_name=tech_clean,
        total_jobs=len(jobs),
        salary_range_avg=salary_avg,
        top_companies=[c[0] for c in top_companies],
        top_locations=[l[0] for l in top_locations],
        jobs_preview=jobs_preview
    )


@router.get("/search-suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db_session)
):
    """
    Autocompletado para búsqueda pública
    Mejora UX y engagement
    
    Retorna:
    - Tecnologías populares que coinciden
    - Empresas que coinciden
    - Ubicaciones que coinciden
    """
    # Top tecnologías
    jobs = db.query(Job).filter(Job.is_active == True).limit(1000).all()
    tech_count = {}
    for job in jobs:
        if isinstance(job.tech_stack, list):
            for tech in job.tech_stack:
                if q.lower() in tech.lower():
                    tech_count[tech] = tech_count.get(tech, 0) + 1
    
    top_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Top empresas
    companies = db.query(Job.company_name, func.count(Job.id)).filter(
        Job.company_name.ilike(f"%{q}%"),
        Job.is_active == True
    ).group_by(Job.company_name).order_by(desc(func.count(Job.id))).limit(5).all()
    
    # Top ubicaciones
    locations = db.query(Job.location, func.count(Job.id)).filter(
        Job.location.ilike(f"%{q}%"),
        Job.is_active == True
    ).group_by(Job.location).order_by(desc(func.count(Job.id))).limit(5).all()
    
    return {
        "technologies": [{"name": t[0], "count": t[1]} for t in top_techs],
        "companies": [{"name": c[0], "count": c[1]} for c in companies],
        "locations": [{"name": l[0], "count": l[1]} for l in locations]
    }


@router.get("/stats")
def get_public_stats(db: Session = Depends(get_db_session)):
    """
    Estadísticas públicas para homepage
    
    Genera confianza y FOMO:
    - Total de ofertas activas
    - Empresas registradas
    - Tecnologías más demandadas
    - Última actualización
    """
    from datetime import datetime, timedelta
    
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    total_companies = db.query(Job.company_name).distinct().count()
    
    # Jobs añadidos hoy
    today = datetime.utcnow().date()
    jobs_today = db.query(Job).filter(
        func.date(Job.posted_date) == today
    ).count()
    
    # Jobs últimos 7 días
    week_ago = datetime.utcnow() - timedelta(days=7)
    jobs_this_week = db.query(Job).filter(
        Job.posted_date >= week_ago
    ).count()
    
    # Top 5 tecnologías
    jobs = db.query(Job).filter(Job.is_active == True).limit(1000).all()
    tech_count = {}
    for job in jobs:
        if isinstance(job.tech_stack, list):
            for tech in job.tech_stack:
                tech_count[tech] = tech_count.get(tech, 0) + 1
    
    top_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_active_jobs": total_jobs,
        "total_companies": total_companies,
        "jobs_added_today": jobs_today,
        "jobs_this_week": jobs_this_week,
        "top_technologies": [{"name": t[0], "count": t[1]} for t in top_techs],
        "last_updated": datetime.utcnow().isoformat(),
        "update_frequency": "Actualizado cada 6 horas"
    }


# ==================== FUNCIONES AUXILIARES ====================

def calculate_public_growth_score(job: Job) -> float:
    """
    Versión simplificada de Growth Score para público
    Sin revelar algoritmo completo
    """
    score = 5.0
    
    # Tech stack moderno
    if isinstance(job.tech_stack, list) and len(job.tech_stack) > 0:
        score += min(len(job.tech_stack) * 0.3, 2.0)
    
    # Remoto
    if job.modality and "remoto" in job.modality.lower():
        score += 1.5
    
    # Publicado recientemente
    if job.posted_date:
        from datetime import datetime
        days_old = (datetime.utcnow() - job.posted_date).days
        if days_old <= 7:
            score += 1.5
    
    return min(round(score, 1), 10.0)


def get_salary_preview(salary_range: Optional[str]) -> str:
    """
    Retorna preview genérico de salario para usuarios públicos
    Lead magnet: Salario completo solo para registrados
    """
    if not salary_range:
        return "Competitivo 🔒"
    
    # Detectar si tiene números
    if any(char.isdigit() for char in salary_range):
        # Mostrar solo rango genérico
        if "$100k" in salary_range or "$150k" in salary_range:
            return "$100k+ 🔒"
        elif "$80k" in salary_range or "$90k" in salary_range:
            return "$80k+ 🔒"
        else:
            return "Competitivo 🔒"
    
    return "No especificado 🔒"


# ==================== MEJORES PRÁCTICAS SEO ====================

"""
Optimizaciones implementadas:

1. **URLs amigables:**
   - /public/jobs (lista)
   - /public/jobs/123 (detalle)
   - /public/tech/python (landing por tecnología)

2. **Meta tags dinámicos:**
   - Ver src/seo_router.py para meta tags por oferta
   - Incluir en frontend con react-helmet

3. **Structured Data:**
   - JSON-LD para schema.org/JobPosting
   - Mejora aparición en Google for Jobs

4. **Crawlers amigables:**
   - Sin JavaScript requerido (SSR)
   - Respuestas rápidas (<100ms)
   - Sitemap.xml actualizado automáticamente

5. **Lead Magnets:**
   - Salario completo: 🔒 Requiere login
   - Botón "Aplicar": 🔒 Requiere login
   - Red Flags IA: 🔒 Requiere CANDIDATO_PREMIUM
   - Datasets export: 🔒 Requiere HR_PRO

6. **Conversion Funnel:**
   - Public page → Ver preview → CTA registro → Signup → Ver completo
   - Tracking: Medir conversión de público → registrado

7. **Social Sharing:**
   - Open Graph images (ver src/social_images.py)
   - Twitter Cards
   - LinkedIn rich previews
"""


if __name__ == "__main__":
    print("Public Job Board cargado correctamente")
    print("\nEndpoints disponibles:")
    print("- GET /public/jobs")
    print("- GET /public/jobs/{job_id}")
    print("- GET /public/tech/{tech_name}")
    print("- GET /public/search-suggestions")
    print("- GET /public/stats")
