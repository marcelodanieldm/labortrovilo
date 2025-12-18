# Inicialización del paquete src / Pakaj ekigo de src
# Package initialization

"""
Labortrovilo - Backend Package
Paquete principal con modelos, schemas y motor de scraping
"""

__version__ = "2.1.0"  # AI Module added
__author__ = "Daniel - Senior Data Engineer & AI Engineer"

from src.models import Job, Company, Base
from src.schemas import JobCreate, JobResponse, CompanyCreate, CompanyResponse, ScrapingResult
from src.database import get_db, init_db, db_manager
from src.scraper_engine import LabortroviloScraper
from src.ai_processor import AIJobProcessor, get_ai_processor

__all__ = [
    "Job",
    "Company",
    "Base",
    "JobCreate",
    "JobResponse",
    "CompanyCreate",
    "CompanyResponse",
    "ScrapingResult",
    "get_db",
    "init_db",
    "db_manager",
    "LabortroviloScraper",
    "AIJobProcessor",
    "get_ai_processor",
]
