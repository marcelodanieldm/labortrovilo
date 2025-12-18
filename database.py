"""
Configuración de base de datos y gestión de sesiones / Datumbaza agordado kaj seanca administrado
Maneja la configuración del motor SQLAlchemy y creación de sesiones / Administras la agordon de SQLAlchemy motoro kaj kreon de seancoj
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator

from config import settings
from models import Base


# Crear motor de base de datos / Krei datumbazan motoron
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Cambiar a True para registrar consultas SQL / Ŝanĝi al True por registri SQL-demandojn
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Crear fábrica de sesiones / Krei seancan fabrikon
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializa la base de datos creando todas las tablas / Ekigas la datumbazon kreante ĉiujn tabelojn
    """
    try:
        # Crear todas las tablas definidas en los modelos / Krei ĉiujn tabelojn difinitajn en la modeloj
        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized successfully")
    except SQLAlchemyError as e:
        print(f"✗ Error initializing database: {e}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Gestor de contexto para sesiones de base de datos / Kunteksta administranto por datumbazaj seancoj
    Asegura limpieza adecuada y manejo de errores / Certigas taŭgan purigon kaj traktadon de eraroj
    """
    # Crear nueva sesión / Krei novan seancon
    db = SessionLocal()
    try:
        yield db
        # Confirmar cambios si todo está bien / Konfirmi ŝanĝojn se ĉio estas bone
        db.commit()
    except SQLAlchemyError as e:
        # Revertir cambios en caso de error / Malfari ŝanĝojn se okazas eraro
        db.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        # Siempre cerrar la sesión / Ĉiam fermi la seancon
        db.close()


def get_db_session() -> Session:
    """
    Obtiene una sesión de base de datos / Akiras datumbazan seancon
    Recuerda cerrarla después de usar / Memoru fermi ĝin post uzo
    """
    return SessionLocal()
