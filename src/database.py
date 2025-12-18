"""
Configuración de Base de Datos / Datumbaza Agordado
Senior Data Engineer Architecture - Database Layer
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from config import settings
from src.models import Base

# Configurar logging / Agordi registradon / Configure logging
logger = logging.getLogger(__name__)


# Crear motor de base de datos / Krei datumbazan motoron / Create database engine
def create_db_engine():
    """
    Crea el motor de base de datos con configuración optimizada
    Kreas la datumbazan motoron kun optimigita agordado
    """
    connect_args = {}
    
    # Configuración específica para SQLite / SQLite-specifa agordado
    if "sqlite" in settings.DATABASE_URL:
        connect_args = {
            "check_same_thread": False,
            "timeout": 30  # Timeout en segundos / Tempo-limigo en sekundoj
        }
    
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG_SQL,  # Mostrar queries SQL si está en debug / Montri SQL-demandojn se en sencimiga reĝimo
        pool_pre_ping=True,  # Verificar conexiones antes de usarlas / Kontroli konektojn antaŭ uzi
        connect_args=connect_args,
        # Para SQLite, usar StaticPool en desarrollo / Por SQLite, uzi StaticPool en evoluigo
        poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None
    )
    
    # Habilitar foreign keys para SQLite / Ebligi fremdajn ŝlosilojn por SQLite
    if "sqlite" in settings.DATABASE_URL:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
            cursor.close()
    
    return engine


# Instancia global del motor / Malloka ekzemplero de la motoro
engine = create_db_engine()

# Fábrica de sesiones / Seanca fabriko / Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # No expirar objetos después de commit
)


def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    Ekigas la datumbazon kreante ĉiujn tabelojn
    Creates all database tables
    """
    try:
        logger.info("Inicializando base de datos / Initializing database...")
        
        # Crear todas las tablas / Krei ĉiujn tabelojn
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Base de datos inicializada correctamente / Database initialized successfully")
        
        # Verificar tablas creadas / Kontroli kreitajn tabelojn
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tablas creadas: {', '.join(tables)}")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"✗ Error inicializando base de datos: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Error inesperado: {e}")
        raise


def drop_all_tables():
    """
    PELIGRO: Elimina todas las tablas de la base de datos
    DANĜERO: Forigas ĉiujn tabelojn de la datumbazo
    DANGER: Drops all database tables
    """
    try:
        logger.warning("⚠️ Eliminando todas las tablas de la base de datos...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Todas las tablas eliminadas")
        return True
    except SQLAlchemyError as e:
        logger.error(f"✗ Error eliminando tablas: {e}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Gestor de contexto para sesiones de base de datos
    Kunteksta administranto por datumbazaj seancoj
    Context manager for database sessions
    
    Uso / Uzo / Usage:
        with get_db() as db:
            job = db.query(Job).first()
    """
    db = SessionLocal()
    try:
        yield db
        # Confirmar cambios automáticamente / Aŭtomate konfirmi ŝanĝojn
        db.commit()
        
    except SQLAlchemyError as e:
        # Revertir cambios en caso de error / Malfari ŝanĝojn se okazas eraro
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
        
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {e}")
        raise
        
    finally:
        # Siempre cerrar la sesión / Ĉiam fermi la seancon
        db.close()


def get_db_session() -> Session:
    """
    Obtiene una sesión de base de datos
    Akiras datumbazan seancon
    Gets a database session
    
    IMPORTANTE: Debes cerrar manualmente con session.close()
    GRAVA: Vi devas mane fermi per session.close()
    IMPORTANT: You must manually close with session.close()
    """
    return SessionLocal()


class DatabaseManager:
    """
    Administrador de base de datos con métodos de utilidad
    Datumbaza administranto kun utilaj metodoj
    Database manager with utility methods
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def health_check(self) -> bool:
        """
        Verifica la salud de la conexión a la base de datos
        Kontrolas la sanecon de la datumbaza konekto
        """
        try:
            from sqlalchemy import text
            with get_db() as db:
                db.execute(text("SELECT 1"))
            logger.info("✓ Database health check passed")
            return True
        except Exception as e:
            logger.error(f"✗ Database health check failed: {e}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Obtiene el conteo de registros en una tabla"""
        try:
            with get_db() as db:
                from sqlalchemy import text
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                return count
        except Exception as e:
            logger.error(f"Error counting records in {table_name}: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de la base de datos"""
        try:
            return {
                'total_jobs': self.get_table_count('jobs'),
                'total_companies': self.get_table_count('companies'),
                'active_jobs': self.get_table_count('jobs WHERE is_active = 1'),
                'health': self.health_check()
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


# Instancia global del administrador / Malloka administranta ekzemplero
db_manager = DatabaseManager()
