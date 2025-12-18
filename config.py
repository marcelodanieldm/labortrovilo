"""
Configuración de ajustes para Labortrovilo / Agordoj por Labortrovilo
Gestión centralizada de configuración / Centra administrado de agordoj
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ajustes de aplicación / Aplikaj agordoj"""
    
    # Configuración de base de datos / Datumbaza agordado
    DATABASE_URL: str = "sqlite:///./labortrovilo.db"
    
    # Configuración de Playwright / Playwright agordado
    PLAYWRIGHT_HEADLESS: bool = True  # Ejecutar sin interfaz gráfica / Ruli sen grafika interfaco
    PLAYWRIGHT_TIMEOUT: int = 30000  # Tiempo de espera en milisegundos / Atenditempo en milisekundoj
    
    # Configuración de scraping / Skrapado agordado
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Configuración de aplicación / Aplika agordado
    BASE_DIR: Path = Path(__file__).resolve().parent  # Directorio base / Baza dosierujo
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración / Malloka agorda ekzemplero
settings = Settings()
