"""
Generador de Social Sharing Images
Crea imágenes Open Graph (1200x630px) dinámicas para compartir en redes sociales
"""
import io
import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from src.dependencies import get_db_session
from models import Job, Company
from config import settings

router = APIRouter(tags=["Social Images"])


# ==================== CONFIGURACIÓN ====================

# Dimensiones Open Graph recomendadas
OG_WIDTH = 1200
OG_HEIGHT = 630

# Colores de Labortrovilo (dark theme)
COLORS = {
    "bg_primary": (17, 24, 39),      # gray-900
    "bg_secondary": (31, 41, 55),    # gray-800
    "accent": (99, 102, 241),        # indigo-500
    "text_primary": (255, 255, 255), # white
    "text_secondary": (156, 163, 175), # gray-400
    "success": (34, 197, 94),        # green-500
    "warning": (251, 191, 36),       # amber-400
}


# ==================== ENDPOINT PRINCIPAL ====================

@router.get("/social-image/job/{job_id}")
def generate_job_social_image(
    job_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Genera imagen Open Graph para una oferta de trabajo
    1200x630px con logo empresa, tech stack y Growth Score
    
    Usado en meta tags:
    <meta property="og:image" content="/api/social-image/job/123" />
    """
    # Obtener job
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generar imagen
    img_bytes = create_job_image(job)
    
    return Response(content=img_bytes, media_type="image/png")


@router.get("/social-image/tech/{tech_name}")
def generate_tech_landing_image(
    tech_name: str,
    db: Session = Depends(get_db_session)
):
    """
    Genera imagen para landing pages de tecnología
    Ej: /vagas/python -> Imagen con logo Python + contador de ofertas
    """
    tech_clean = tech_name.replace("-", " ").title()
    
    # Contar ofertas
    jobs_count = db.query(Job).filter(
        Job.tech_stack.contains(tech_clean)
    ).count()
    
    # Generar imagen
    img_bytes = create_tech_landing_image(tech_clean, jobs_count)
    
    return Response(content=img_bytes, media_type="image/png")


# ==================== GENERADORES DE IMÁGENES ====================

def create_job_image(job: Job) -> bytes:
    """
    Crea imagen para compartir oferta de trabajo
    
    Layout:
    +--------------------------------------------------+
    | 🏢 COMPANY LOGO (top-left)    Labortrovilo Logo |
    |                                                  |
    | 💼 JOB TITLE (grande, bold)                     |
    |                                                  |
    | 📍 Location   |   💰 Salary Range               |
    |                                                  |
    | 🔧 [Python] [React] [Docker] [AWS]              |
    |                                                  |
    | ⭐ Growth Score: 8.7/10          1847 ofertas    |
    +--------------------------------------------------+
    """
    # Crear canvas
    img = Image.new('RGB', (OG_WIDTH, OG_HEIGHT), color=COLORS["bg_primary"])
    draw = ImageDraw.Draw(img)
    
    # Cargar fuentes
    try:
        font_title = ImageFont.truetype("arial.ttf", 72)
        font_subtitle = ImageFont.truetype("arial.ttf", 42)
        font_body = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except:
        # Fallback si no encuentra las fuentes
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Logo de Labortrovilo (top-right)
    draw.text(
        (OG_WIDTH - 250, 40),
        "Labortrovilo",
        fill=COLORS["accent"],
        font=font_body
    )
    
    # Company name (top-left)
    company_name = job.company_name or "Empresa Top"
    draw.text(
        (60, 40),
        f"🏢 {company_name[:30]}",
        fill=COLORS["text_secondary"],
        font=font_body
    )
    
    # Job Title (centro, grande)
    title = job.title[:50] if len(job.title) > 50 else job.title
    draw.text(
        (60, 140),
        title,
        fill=COLORS["text_primary"],
        font=font_title
    )
    
    # Location y Salary (debajo del título)
    location = job.location or "Remoto"
    draw.text(
        (60, 260),
        f"📍 {location[:30]}",
        fill=COLORS["text_secondary"],
        font=font_subtitle
    )
    
    if job.salary_range:
        draw.text(
            (600, 260),
            f"💰 {job.salary_range[:25]}",
            fill=COLORS["success"],
            font=font_subtitle
        )
    
    # Tech Stack (badges)
    if isinstance(job.tech_stack, list):
        tech_y = 360
        tech_x = 60
        for i, tech in enumerate(job.tech_stack[:6]):  # Max 6 techs
            # Badge background
            badge_width = len(tech) * 18 + 30
            draw.rounded_rectangle(
                [(tech_x, tech_y), (tech_x + badge_width, tech_y + 50)],
                radius=10,
                fill=COLORS["bg_secondary"],
                outline=COLORS["accent"],
                width=2
            )
            # Tech name
            draw.text(
                (tech_x + 15, tech_y + 10),
                tech[:15],
                fill=COLORS["text_primary"],
                font=font_body
            )
            tech_x += badge_width + 20
            
            # Nueva línea después de 3 badges
            if (i + 1) % 3 == 0:
                tech_x = 60
                tech_y += 70
    
    # Growth Score (bottom-left)
    growth_score = calculate_growth_score(job)
    score_color = COLORS["success"] if growth_score >= 8 else (
        COLORS["warning"] if growth_score >= 6 else COLORS["text_secondary"]
    )
    draw.text(
        (60, OG_HEIGHT - 100),
        f"⭐ Growth Score: {growth_score}/10",
        fill=score_color,
        font=font_subtitle
    )
    
    # Total ofertas (bottom-right)
    draw.text(
        (OG_WIDTH - 300, OG_HEIGHT - 100),
        "1847 ofertas activas",
        fill=COLORS["text_secondary"],
        font=font_small
    )
    
    # Convertir a bytes
    img_io = io.BytesIO()
    img.save(img_io, format='PNG', quality=95)
    img_io.seek(0)
    
    return img_io.getvalue()


def create_tech_landing_image(tech_name: str, jobs_count: int) -> bytes:
    """
    Crea imagen para landing pages de tecnología
    
    Layout:
    +--------------------------------------------------+
    |                                                  |
    |              🐍 PYTHON JOBS                      |
    |                                                  |
    |          ╔════════════════════╗                 |
    |          ║   247 ofertas      ║                 |
    |          ║   Actualizadas hoy ║                 |
    |          ╚════════════════════╝                 |
    |                                                  |
    |        Labortrovilo - Growth Platform            |
    +--------------------------------------------------+
    """
    # Crear canvas con gradiente
    img = Image.new('RGB', (OG_WIDTH, OG_HEIGHT), color=COLORS["bg_primary"])
    draw = ImageDraw.Draw(img)
    
    # Gradiente simple (de arriba a abajo)
    for y in range(OG_HEIGHT):
        color_factor = y / OG_HEIGHT
        color = tuple(
            int(COLORS["bg_primary"][i] + (COLORS["bg_secondary"][i] - COLORS["bg_primary"][i]) * color_factor)
            for i in range(3)
        )
        draw.line([(0, y), (OG_WIDTH, y)], fill=color)
    
    # Cargar fuentes
    try:
        font_huge = ImageFont.truetype("arial.ttf", 96)
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_medium = ImageFont.truetype("arial.ttf", 48)
    except:
        font_huge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Tech name (centro, muy grande)
    tech_emoji = get_tech_emoji(tech_name)
    title = f"{tech_emoji} {tech_name.upper()} JOBS"
    
    # Calcular posición para centrar
    bbox = draw.textbbox((0, 0), title, font=font_huge)
    text_width = bbox[2] - bbox[0]
    text_x = (OG_WIDTH - text_width) // 2
    
    draw.text(
        (text_x, 120),
        title,
        fill=COLORS["text_primary"],
        font=font_huge
    )
    
    # Card con número de ofertas
    card_width = 500
    card_height = 200
    card_x = (OG_WIDTH - card_width) // 2
    card_y = 280
    
    # Card background
    draw.rounded_rectangle(
        [(card_x, card_y), (card_x + card_width, card_y + card_height)],
        radius=20,
        fill=COLORS["bg_secondary"],
        outline=COLORS["accent"],
        width=4
    )
    
    # Jobs count (dentro del card)
    count_text = f"{jobs_count} ofertas"
    bbox = draw.textbbox((0, 0), count_text, font=font_large)
    count_width = bbox[2] - bbox[0]
    count_x = card_x + (card_width - count_width) // 2
    
    draw.text(
        (count_x, card_y + 40),
        count_text,
        fill=COLORS["accent"],
        font=font_large
    )
    
    # "Actualizadas hoy"
    subtitle = "Actualizadas hoy"
    bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
    subtitle_width = bbox[2] - bbox[0]
    subtitle_x = card_x + (card_width - subtitle_width) // 2
    
    draw.text(
        (subtitle_x, card_y + 130),
        subtitle,
        fill=COLORS["text_secondary"],
        font=font_medium
    )
    
    # Footer
    footer = "Labortrovilo - Growth Platform"
    bbox = draw.textbbox((0, 0), footer, font=font_medium)
    footer_width = bbox[2] - bbox[0]
    footer_x = (OG_WIDTH - footer_width) // 2
    
    draw.text(
        (footer_x, OG_HEIGHT - 80),
        footer,
        fill=COLORS["text_secondary"],
        font=font_medium
    )
    
    # Convertir a bytes
    img_io = io.BytesIO()
    img.save(img_io, format='PNG', quality=95)
    img_io.seek(0)
    
    return img_io.getvalue()


# ==================== FUNCIONES AUXILIARES ====================

def calculate_growth_score(job: Job) -> float:
    """
    Calcula Growth Score de una oferta (0-10)
    
    Factores:
    - Salario competitivo (+2)
    - Tech stack moderno (+2)
    - Remoto (+1.5)
    - Empresa reconocida (+1.5)
    - Publicado recientemente (+1.5)
    - Description completa (+1)
    - Location atractiva (+0.5)
    """
    score = 5.0  # Base score
    
    # Salario competitivo
    if job.salary_range:
        if any(keyword in job.salary_range.lower() for keyword in ["$100k", "$150k", "$200k"]):
            score += 2.0
        elif any(keyword in job.salary_range.lower() for keyword in ["$80k", "$90k"]):
            score += 1.0
    
    # Tech stack moderno
    if isinstance(job.tech_stack, list):
        modern_techs = ["Python", "React", "TypeScript", "Kubernetes", "AWS", "Docker", "Go", "Rust"]
        tech_matches = sum(1 for tech in job.tech_stack if any(mt.lower() in tech.lower() for mt in modern_techs))
        score += min(tech_matches * 0.4, 2.0)
    
    # Remoto
    if job.modality and "remoto" in job.modality.lower():
        score += 1.5
    
    # Description completa
    if job.description and len(job.description) > 200:
        score += 1.0
    
    # Publicado recientemente (últimos 7 días)
    if job.posted_date:
        from datetime import datetime, timedelta
        days_old = (datetime.utcnow() - job.posted_date).days
        if days_old <= 7:
            score += 1.5
        elif days_old <= 14:
            score += 0.8
    
    return min(round(score, 1), 10.0)


def get_tech_emoji(tech_name: str) -> str:
    """
    Retorna emoji apropiado para cada tecnología
    """
    tech_lower = tech_name.lower()
    
    emoji_map = {
        "python": "🐍",
        "javascript": "⚡",
        "typescript": "📘",
        "react": "⚛️",
        "vue": "💚",
        "angular": "🅰️",
        "node": "🟢",
        "go": "🐹",
        "rust": "🦀",
        "java": "☕",
        "kotlin": "🔷",
        "swift": "🍎",
        "docker": "🐳",
        "kubernetes": "☸️",
        "aws": "☁️",
        "azure": "☁️",
        "gcp": "☁️",
        "sql": "🗄️",
        "mongodb": "🍃",
        "postgres": "🐘",
        "redis": "🔴",
        "graphql": "🔺",
        "flutter": "💙",
        "android": "🤖",
        "ios": "📱",
    }
    
    for key, emoji in emoji_map.items():
        if key in tech_lower:
            return emoji
    
    return "💼"  # Default


# ==================== LOGO UPLOADER (OPCIONAL) ====================

@router.post("/admin/upload-company-logo/{company_id}")
async def upload_company_logo(
    company_id: int,
    # file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    """
    [ADMIN] Sube logo de empresa para usar en social images
    
    TODO: Implementar upload real con S3 o almacenamiento local
    Por ahora, usar logos por defecto o URLs externas
    """
    return {
        "message": "Feature coming soon",
        "description": "Por ahora usamos logos genéricos. Implementar con S3 en futuro."
    }


if __name__ == "__main__":
    print("Social Images Generator cargado correctamente")
    print("Endpoints disponibles:")
    print("- GET /social-image/job/{job_id}")
    print("- GET /social-image/tech/{tech_name}")
