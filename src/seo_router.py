"""
SEO Router - Generación dinámica de sitemaps y optimización SEO
Genera automáticamente sitemaps basados en tecnologías más buscadas
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.dependencies import get_db_session
from models import Job, Company
from config import settings

router = APIRouter(tags=["SEO"])


# ==================== SITEMAP.XML ====================

@router.get("/sitemap.xml", response_class=Response)
def generate_sitemap(db: Session = Depends(get_db_session)):
    """
    Genera sitemap.xml dinámico con:
    - Páginas estáticas (home, pricing, about)
    - Landing pages por tecnología (/vagas/python, /vagas/react, etc)
    - Landing pages por ubicación (/vagas/argentina, /vagas/brasil)
    - Landing pages por modalidad (/vagas/remoto, /vagas/hibrido)
    - Ofertas individuales (últimas 500)
    
    Google recomienda máximo 50k URLs por sitemap
    """
    
    # Base URL
    base_url = settings.API_BASE_URL or "https://labortrovilo.com"
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Páginas estáticas
    static_pages = [
        {"loc": f"{base_url}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{base_url}/pricing", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{base_url}/about", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{base_url}/blog", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base_url}/contact", "priority": "0.6", "changefreq": "monthly"},
    ]
    
    # Tecnologías más demandadas (extraídas de tech_stack JSON)
    # Análisis de tech_stack en todos los jobs
    top_techs = get_top_technologies(db, limit=50)
    tech_pages = [
        {
            "loc": f"{base_url}/vagas/{tech.lower().replace(' ', '-')}",
            "priority": "0.9",
            "changefreq": "daily"
        }
        for tech in top_techs
    ]
    
    # Ubicaciones más populares
    top_locations = get_top_locations(db, limit=30)
    location_pages = [
        {
            "loc": f"{base_url}/vagas/{loc.lower().replace(' ', '-').replace(',', '')}",
            "priority": "0.8",
            "changefreq": "daily"
        }
        for loc in top_locations
    ]
    
    # Modalidades
    modality_pages = [
        {"loc": f"{base_url}/vagas/remoto", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base_url}/vagas/hibrido", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base_url}/vagas/presencial", "priority": "0.7", "changefreq": "daily"},
    ]
    
    # Últimas 500 ofertas (las más recientes tienen mejor SEO)
    recent_jobs = db.query(Job).order_by(desc(Job.posted_date)).limit(500).all()
    job_pages = [
        {
            "loc": f"{base_url}/job/{job.id}",
            "priority": "0.7",
            "changefreq": "weekly",
            "lastmod": job.posted_date.strftime("%Y-%m-%d") if job.posted_date else current_date
        }
        for job in recent_jobs
    ]
    
    # Combinar todas las URLs
    all_urls = static_pages + tech_pages + location_pages + modality_pages + job_pages
    
    # Generar XML
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in all_urls:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{url["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{url.get("lastmod", current_date)}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        sitemap_xml += f'    <priority>{url["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    return Response(content=sitemap_xml, media_type="application/xml")


# ==================== ROBOTS.TXT ====================

@router.get("/robots.txt", response_class=Response)
def generate_robots():
    """
    Genera robots.txt optimizado para crawlers
    """
    base_url = settings.API_BASE_URL or "https://labortrovilo.com"
    
    robots_txt = f"""# Labortrovilo - Robots.txt
# https://labortrovilo.com
# Actualizado: {datetime.utcnow().strftime("%Y-%m-%d")}

User-agent: *
Allow: /
Allow: /vagas/
Allow: /job/
Allow: /pricing
Allow: /about
Allow: /blog
Disallow: /api/
Disallow: /admin/
Disallow: /billing/
Disallow: /user/

# Crawl-delay para respetar nuestros recursos
Crawl-delay: 2

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Agentes específicos
User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: LinkedInBot
Allow: /
Allow: /job/
Crawl-delay: 1

User-agent: Twitterbot
Allow: /
Allow: /job/
Crawl-delay: 1
"""
    
    return Response(content=robots_txt, media_type="text/plain")


# ==================== FUNCIONES AUXILIARES ====================

def get_top_technologies(db: Session, limit: int = 50) -> List[str]:
    """
    Extrae las tecnologías más demandadas de tech_stack JSON
    Retorna lista de strings: ['Python', 'JavaScript', 'React', ...]
    """
    # Obtener todos los jobs con tech_stack
    jobs = db.query(Job).filter(Job.tech_stack.isnot(None)).all()
    
    # Contar ocurrencias de cada tecnología
    tech_count = {}
    for job in jobs:
        if isinstance(job.tech_stack, list):
            for tech in job.tech_stack:
                tech_clean = tech.strip().title()
                tech_count[tech_clean] = tech_count.get(tech_clean, 0) + 1
    
    # Ordenar por frecuencia
    top_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)
    
    # Retornar top N
    return [tech for tech, count in top_techs[:limit]]


def get_top_locations(db: Session, limit: int = 30) -> List[str]:
    """
    Obtiene las ubicaciones más frecuentes
    Retorna lista de strings: ['Buenos Aires', 'São Paulo', ...]
    """
    # Query agrupando por location
    results = db.query(
        Job.location,
        func.count(Job.id).label('count')
    ).filter(
        Job.location.isnot(None)
    ).group_by(
        Job.location
    ).order_by(
        desc('count')
    ).limit(limit).all()
    
    return [loc for loc, count in results if loc]


# ==================== STRUCTURED DATA (JSON-LD) ====================

def generate_job_structured_data(job: Job, company: Company = None) -> dict:
    """
    Genera JSON-LD para schema.org/JobPosting
    Mejora aparición en Google for Jobs
    
    Uso en frontend:
    <script type="application/ld+json">
      {json.dumps(structured_data)}
    </script>
    """
    base_url = settings.API_BASE_URL or "https://labortrovilo.com"
    
    structured_data = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": job.title,
        "description": job.description or f"Oportunidad de trabajo como {job.title}",
        "datePosted": job.posted_date.isoformat() if job.posted_date else datetime.utcnow().isoformat(),
        "validThrough": (job.posted_date.replace(day=job.posted_date.day + 30).isoformat() 
                        if job.posted_date else datetime.utcnow().isoformat()),
        "employmentType": job.modality or "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": job.company_name or (company.name if company else "Empresa Confidencial"),
            "sameAs": company.website if company and company.website else base_url,
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job.location or "Remoto",
                "addressCountry": "AR"  # Ajustar según tu mercado
            }
        },
        "baseSalary": {},
        "skills": job.tech_stack if isinstance(job.tech_stack, list) else []
    }
    
    # Añadir salario si está disponible
    if job.salary_range:
        structured_data["baseSalary"] = {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "value": job.salary_range,
                "unitText": "YEAR"
            }
        }
    
    return structured_data


# ==================== META TAGS HELPER ====================

def generate_job_meta_tags(job: Job, company: Company = None) -> dict:
    """
    Genera meta tags para SEO y Social Sharing
    
    Retorna:
    {
        "title": "...",
        "description": "...",
        "keywords": "...",
        "og:title": "...",
        "og:description": "...",
        "og:image": "...",
        "twitter:card": "...",
        ...
    }
    """
    base_url = settings.API_BASE_URL or "https://labortrovilo.com"
    
    # Tech stack como string
    tech_stack_str = ", ".join(job.tech_stack) if isinstance(job.tech_stack, list) else ""
    
    # Title optimizado (60 chars max)
    title = f"{job.title} - {job.company_name or 'Empresa Top'}"
    if len(title) > 60:
        title = f"{job.title[:45]}... - {job.company_name[:10]}"
    
    # Description optimizada (160 chars max)
    description = (
        f"💼 {job.title} en {job.company_name or 'empresa líder'}. "
        f"🔧 {tech_stack_str[:80]}. "
        f"📍 {job.location or 'Remoto'}. "
        f"Aplica ahora en Labortrovilo!"
    )[:160]
    
    # Keywords
    keywords = f"{job.title}, {tech_stack_str}, {job.location or 'remoto'}, trabajo, empleo"
    
    # URL de imagen social (generada dinámicamente)
    og_image = f"{base_url}/api/social-image/job/{job.id}"
    
    meta_tags = {
        # Basic SEO
        "title": title,
        "description": description,
        "keywords": keywords,
        
        # Open Graph (Facebook, LinkedIn)
        "og:type": "website",
        "og:title": title,
        "og:description": description,
        "og:image": og_image,
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:url": f"{base_url}/job/{job.id}",
        "og:site_name": "Labortrovilo",
        
        # Twitter Card
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": og_image,
        "twitter:site": "@labortrovilo",
        
        # LinkedIn specific
        "linkedin:owner": "Labortrovilo",
    }
    
    return meta_tags


# ==================== ENDPOINT PARA FRONTEND ====================

@router.get("/seo/job/{job_id}")
def get_job_seo_data(job_id: int, db: Session = Depends(get_db_session)):
    """
    Retorna datos SEO completos para una oferta
    Usado por frontend para inyectar meta tags
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        return {"error": "Job not found"}
    
    # Obtener company si existe
    company = db.query(Company).filter(Company.name == job.company_name).first()
    
    return {
        "meta_tags": generate_job_meta_tags(job, company),
        "structured_data": generate_job_structured_data(job, company),
        "canonical_url": f"{settings.API_BASE_URL or 'https://labortrovilo.com'}/job/{job.id}"
    }


@router.get("/seo/tech/{tech_name}")
def get_tech_landing_seo(tech_name: str, db: Session = Depends(get_db_session)):
    """
    Genera meta tags para landing pages de tecnología
    Ej: /vagas/python, /vagas/react
    """
    base_url = settings.API_BASE_URL or "https://labortrovilo.com"
    tech_clean = tech_name.replace("-", " ").title()
    
    # Contar ofertas con esa tecnología
    jobs_count = db.query(func.count(Job.id)).filter(
        Job.tech_stack.contains(tech_clean)
    ).scalar()
    
    title = f"{jobs_count} Vagas de {tech_clean} - Labortrovilo"
    description = (
        f"🚀 Encontra las mejores {jobs_count} oportunidades de trabajo con {tech_clean}. "
        f"Ofertas actualizadas diariamente. Salarios competitivos. Empresas top."
    )
    
    return {
        "meta_tags": {
            "title": title,
            "description": description,
            "og:title": title,
            "og:description": description,
            "og:image": f"{base_url}/api/social-image/tech/{tech_name}",
            "og:url": f"{base_url}/vagas/{tech_name}",
        },
        "canonical_url": f"{base_url}/vagas/{tech_name}",
        "jobs_count": jobs_count
    }


if __name__ == "__main__":
    print("SEO Router cargado correctamente")
    print("Endpoints disponibles:")
    print("- GET /sitemap.xml")
    print("- GET /robots.txt")
    print("- GET /seo/job/{job_id}")
    print("- GET /seo/tech/{tech_name}")
