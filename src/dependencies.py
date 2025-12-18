"""
Dependencias de FastAPI para Labortrovilo
FastAPI Dependencoj por Labortrovilo
FastAPI Dependencies for Labortrovilo

Middleware de autenticación y verificación de roles
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.auth import (
    decode_access_token, 
    get_user, 
    UserRole, 
    User,
    check_role_permission
)
from src.database import get_db


# ============================================================
# OAUTH2 SCHEME / OAUTH2 SKEMO
# ============================================================

# Define el esquema OAuth2 con URL de login
# Difinas la OAuth2-skemon kun ensaluta URL
# Defines OAuth2 scheme with login URL
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    scheme_name="JWT"
)


# ============================================================
# DEPENDENCIAS DE AUTENTICACIÓN / AŬTENTIKIGAJ DEPENDENCOJ
# ============================================================

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """
    Obtiene el usuario actual desde el token JWT
    Akiras la nunan uzanton de la JWT-ĵetono
    Gets current user from JWT token
    
    Esta dependencia debe usarse en todos los endpoints protegidos
    Ĉi tiu dependenco devus esti uzata en ĉiuj protektitaj finpunktoj
    This dependency should be used in all protected endpoints
    
    Args:
        token: Token JWT automáticamente extraído del header Authorization
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    # Decodificar token
    token_data = decode_access_token(token)
    
    # Obtener usuario de la base de datos
    user = get_user(username=token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Verifica que el usuario esté activo
    Kontrolas ke la uzanto estas aktiva
    Verifies that the user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


# ============================================================
# DEPENDENCIAS DE ROLES / ROLAJ DEPENDENCOJ / ROLE DEPENDENCIES
# ============================================================

class RoleChecker:
    """
    Clase para crear dependencias de verificación de roles
    Klaso por krei rolan kontrolan dependencon
    Class to create role verification dependencies
    
    Uso / Uzo / Usage:
        require_candidato = RoleChecker(UserRole.CANDIDATO)
        
        @app.get("/jobs")
        async def get_jobs(user: User = Depends(require_candidato)):
            ...
    """
    
    def __init__(self, required_role: UserRole):
        self.required_role = required_role
    
    async def __call__(
        self, 
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        """
        Verifica que el usuario tenga el rol requerido o superior
        Kontrolas ke la uzanto havas la bezonatan rolon aŭ pli altan
        Checks that the user has the required role or higher
        """
        if not check_role_permission(current_user.role, self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol {self.required_role.value} o superior. Tu rol: {current_user.role.value}"
            )
        return current_user


# Instancias de verificadores de roles / Rolkontrolaj ekzempleroj / Role checker instances
require_candidato = RoleChecker(UserRole.CANDIDATO)
require_hr_pro = RoleChecker(UserRole.HR_PRO)
require_admin = RoleChecker(UserRole.ADMIN)
require_superuser = RoleChecker(UserRole.SUPERUSER)


# ============================================================
# DEPENDENCIA DE BASE DE DATOS / DATUMBAZA DEPENDENCO
# ============================================================

def get_db_session() -> Session:
    """
    Obtiene una sesión de base de datos
    Akiras datumbazan seancon
    Gets a database session
    
    Esta dependencia se puede combinar con las de auth:
    
    @app.get("/endpoint")
    async def endpoint(
        user: User = Depends(require_hr_pro),
        db: Session = Depends(get_db_session)
    ):
        ...
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# ============================================================
# DEPENDENCIAS DE PAGINACIÓN / PAĜIGAJ DEPENDENCOJ
# ============================================================

class PaginationParams:
    """
    Parámetros de paginación estándar
    Normaj paĝigaj parametroj
    Standard pagination parameters
    """
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 50,
        max_limit: int = 100
    ):
        self.skip = skip
        self.limit = min(limit, max_limit)  # No permitir límites excesivos


def pagination_params(
    skip: int = 0,
    limit: int = 50
) -> PaginationParams:
    """
    Dependencia para paginación
    Dependenco por paĝigo
    Dependency for pagination
    
    Uso / Uzo / Usage:
        @app.get("/items")
        async def get_items(pagination: PaginationParams = Depends(pagination_params)):
            return db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
    """
    return PaginationParams(skip=skip, limit=limit)


# ============================================================
# DEPENDENCIAS DE FILTROS / FILTRAJ DEPENDENCOJ / FILTER DEPENDENCIES
# ============================================================

class JobFilterParams:
    """
    Parámetros de filtro para jobs
    Filtraj parametroj por laboroj
    Filter parameters for jobs
    """
    
    def __init__(
        self,
        stack: str | None = None,
        seniority: str | None = None,
        is_remote: bool | None = None,
        min_salary: float | None = None,
        country: str | None = None
    ):
        self.stack = stack
        self.seniority = seniority
        self.is_remote = is_remote
        self.min_salary = min_salary
        self.country = country


def job_filter_params(
    stack: str | None = None,
    seniority: str | None = None,
    is_remote: bool | None = None,
    min_salary: float | None = None,
    country: str | None = None
) -> JobFilterParams:
    """
    Dependencia para filtrar trabajos
    Dependenco por filtri laborojn
    Dependency for filtering jobs
    """
    return JobFilterParams(
        stack=stack,
        seniority=seniority,
        is_remote=is_remote,
        min_salary=min_salary,
        country=country
    )


# ============================================================
# EJEMPLO DE USO / EKZEMPLO DE UZO / USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("🔧 FastAPI Dependencies Module - Labortrovilo")
    print("="*60)
    print("\n✓ Dependencias disponibles:")
    print("  - get_current_user: Obtiene usuario del token")
    print("  - require_candidato: Requiere rol CANDIDATO")
    print("  - require_hr_pro: Requiere rol HR_PRO")
    print("  - require_admin: Requiere rol ADMIN")
    print("  - require_superuser: Requiere rol SUPERUSER")
    print("  - get_db_session: Sesión de base de datos")
    print("  - pagination_params: Paginación estándar")
    print("  - job_filter_params: Filtros de trabajos")
