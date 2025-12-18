"""
Configuración de ajustes para Labortrovilo / Agordoj por Labortrovilo
Gestión centralizada de configuración / Centra administrado de agordoj
Senior Data Engineer Architecture - Configuration Management
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Ajustes de aplicación / Aplikaj agordoj
    Configuración centralizada con validación Pydantic
    """
    
    # ============================================================
    # CONFIGURACIÓN DE BASE DE DATOS / DATUMBAZA AGORDADO
    # ============================================================
    DATABASE_URL: str = "sqlite:///./labortrovilo.db"
    DEBUG_SQL: bool = False  # Mostrar queries SQL en consola / Montri SQL-demandojn en konzolo
    
    # ============================================================
    # CONFIGURACIÓN DE PLAYWRIGHT / PLAYWRIGHT AGORDADO
    # ============================================================
    PLAYWRIGHT_HEADLESS: bool = True  # Ejecutar sin interfaz gráfica / Ruli sen grafika interfaco
    PLAYWRIGHT_TIMEOUT: int = 30000  # Tiempo de espera en milisegundos / Atenditempo en milisekundoj
    
    # ============================================================
    # CONFIGURACIÓN DE SCRAPING / SKRAPADO AGORDADO
    # ============================================================
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Delays entre requests (en segundos) / Prokrastoj inter petoj (en sekundoj)
    REQUEST_DELAY_MIN: float = 1.0
    REQUEST_DELAY_MAX: float = 3.0
    
    # Retry configuration / Reprova agordado
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # segundos / sekundoj
    
    # ============================================================
    # CONFIGURACIÓN DE APLICACIÓN / APLIKA AGORDADO
    # ============================================================
    BASE_DIR: Path = Path(__file__).resolve().parent  # Directorio base / Baza dosierujo
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Configuración de logging / Registra agordado
    LOG_FILE: str = "logs/scraper.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    
    # ============================================================
    # CONFIGURACIÓN DE IA / AI AGORDADO / AI CONFIGURATION
    # ============================================================
    OPENAI_API_KEY: str = ""  # sk-...
    ANTHROPIC_API_KEY: str = ""  # sk-ant-...
    AI_PROVIDER: str = "openai"  # openai o anthropic
    AI_MODEL: str = "gpt-4o-mini"  # gpt-4o-mini, gpt-4, claude-3-haiku, etc.
    AI_CACHE_ENABLED: bool = True  # Sistema de caché para evitar llamadas duplicadas
    LOG_BACKUP_COUNT: int = 5
    
    # ============================================================
    # CONFIGURACIÓN DE SEGURIDAD / SEKURECA AGORDADO
    # ============================================================
    # API Keys y tokens (cargar desde .env) / API-ŝlosiloj kaj ĵetonoj
    API_KEY: str = ""
    SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración / Malloka agorda ekzemplero
settings = Settings()


# Validaciones post-carga / Post-ŝargaj validigoj
if __name__ == "__main__":
    print("⚙️ Configuración de Labortrovilo:")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   PLAYWRIGHT_HEADLESS: {settings.PLAYWRIGHT_HEADLESS}")
    print(f"   USER_AGENT: {settings.USER_AGENT[:50]}...")
    print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")
