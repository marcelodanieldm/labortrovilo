"""
Sistema de Autenticación y Autorización para Labortrovilo API
Aŭtentikiga kaj Aŭtorizacia Sistema por Labortrovilo API
Authentication and Authorization System for Labortrovilo API

Senior Backend Developer + Security Expert Architecture
"""
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from jose import JWTError, jwt
import hashlib
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException, status

from config import settings


# ============================================================
# ROLES Y PERMISOS / ROLOJ KAJ PERMESOJ / ROLES AND PERMISSIONS
# ============================================================

class UserRole(str, Enum):
    """
    Roles de usuario con niveles de acceso jerárquicos
    Uzantoroloj kun hierarkiaj alirniveloj
    User roles with hierarchical access levels
    """
    CANDIDATO = "candidato"      # Nivel 1: Busca trabajos
    HR_PRO = "hr_pro"            # Nivel 2: Acceso a market intelligence
    ADMIN = "admin"              # Nivel 3: Gestión de scrapers
    SUPERUSER = "superuser"      # Nivel 4: Control total


# Jerarquía de permisos / Permeshierarkio / Permission hierarchy
ROLE_HIERARCHY = {
    UserRole.CANDIDATO: 1,
    UserRole.HR_PRO: 2,
    UserRole.ADMIN: 3,
    UserRole.SUPERUSER: 4
}


# ============================================================
# MODELOS PYDANTIC / PYDANTIC MODELOJ / PYDANTIC MODELS
# ============================================================

class Token(BaseModel):
    """Token JWT de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos


class TokenData(BaseModel):
    """Datos extraídos del token JWT"""
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class User(BaseModel):
    """Usuario del sistema"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Esquema para crear usuario"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.CANDIDATO


class UserInDB(User):
    """Usuario con contraseña hasheada"""
    hashed_password: str


# ============================================================
# CONFIGURACIÓN DE SEGURIDAD / SEKURECA AGORDADO / SECURITY CONFIG
# ============================================================

# Configuración de hash de contraseñas / Pasvorta haŝa agordado
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT / JWT agordado / JWT configuration
SECRET_KEY = getattr(settings, 'SECRET_KEY', "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_USE_ENV_VAR")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas


# ============================================================
# FUNCIONES DE AUTENTICACIÓN / AŬTENTIKIGAJ FUNKCIOJ / AUTH FUNCTIONS
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash
    Kontrolas pasvorton kontraŭ ĝia haŝo
    Verifies a password against its hash
    """
    # Usando SHA256 simple por compatibilidad
    hashed_attempt = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_attempt == hashed_password


def get_password_hash(password: str) -> str:
    """
    Genera hash de contraseña
    Generas pasvortan haŝon
    Generates password hash
    """
    # Usando SHA256 simple por compatibilidad  
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso
    Kreas JWT-alirĵetonon
    Creates a JWT access token
    
    Args:
        data: Datos a codificar en el token (username, email, role)
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decodifica y valida un token JWT
    Malkodas kaj validigas JWT-ĵetonon
    Decodes and validates a JWT token
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        TokenData con la información del usuario
        
    Raises:
        HTTPException: Si el token es inválido o expiró
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        email: str = payload.get("email")
        role_str: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
        
        # Convertir string a enum
        try:
            role = UserRole(role_str) if role_str else None
        except ValueError:
            raise credentials_exception
        
        token_data = TokenData(username=username, email=email, role=role)
        return token_data
        
    except JWTError:
        raise credentials_exception


def check_role_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Verifica si un usuario tiene permiso basándose en jerarquía de roles
    Kontrolas ĉu uzanto havas permeson bazitan sur rolhierarkio
    Checks if a user has permission based on role hierarchy
    
    Un usuario de nivel superior puede acceder a endpoints de niveles inferiores
    Pli alta nivela uzanto povas aliri pli malaltajn nivelojn
    Higher level user can access lower level endpoints
    
    Args:
        user_role: Rol actual del usuario
        required_role: Rol mínimo requerido para el endpoint
        
    Returns:
        True si tiene permiso, False si no
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    
    return user_level >= required_level


# ============================================================
# BASE DE DATOS TEMPORAL DE USUARIOS / DUMPA UZANTODATUMBAZO
# ============================================================
# NOTA: En producción, esto debe estar en una tabla de SQLAlchemy
# En esta implementación usamos un dict para simplificar

# Usuarios de ejemplo / Ekzemplaj uzantoj / Sample users
# Pre-hashed passwords to avoid bcrypt issues on init
# Passwords: password123, hrpass123, adminpass123, superpass123
FAKE_USERS_DB = {
    "candidato": UserInDB(
        id=1,
        username="candidato",
        email="candidato@example.com",
        full_name="Juan Candidato",
        role=UserRole.CANDIDATO,
        is_active=True,
        created_at=datetime.utcnow(),
        # SHA256 hash of "password123"
        hashed_password=hashlib.sha256(b"password123").hexdigest()
    ),
    "hr_pro": UserInDB(
        id=2,
        username="hr_pro",
        email="hr@company.com",
        full_name="María HR Professional",
        role=UserRole.HR_PRO,
        is_active=True,
        created_at=datetime.utcnow(),
        # SHA256 hash of "hrpass123"
        hashed_password=hashlib.sha256(b"hrpass123").hexdigest()
    ),
    "admin": UserInDB(
        id=3,
        username="admin",
        email="admin@labortrovilo.com",
        full_name="Carlos Admin",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow(),
        # SHA256 hash of "adminpass123"
        hashed_password=hashlib.sha256(b"adminpass123").hexdigest()
    ),
    "superuser": UserInDB(
        id=4,
        username="superuser",
        email="super@labortrovilo.com",
        full_name="Ana Superuser",
        role=UserRole.SUPERUSER,
        is_active=True,
        created_at=datetime.utcnow(),
        # SHA256 hash of "superpass123"
        hashed_password=hashlib.sha256(b"superpass123").hexdigest()
    )
}


def get_user(username: str) -> Optional[UserInDB]:
    """
    Obtiene un usuario por username
    Akiras uzanton per uzantnomo
    Gets a user by username
    """
    return FAKE_USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Autentica un usuario verificando contraseña
    Aŭtentikas uzanton kontrolante pasvorton
    Authenticates a user by verifying password
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        UserInDB si es válido, None si no
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ============================================================
# FUNCIONES DE UTILIDAD / UTILAJ FUNKCIOJ / UTILITY FUNCTIONS
# ============================================================

def create_demo_token(role: UserRole) -> str:
    """
    Crea un token de demostración para testing rápido
    Kreas demon-ĵetonon por rapida testado
    Creates a demo token for quick testing
    
    Args:
        role: Rol para el cual crear el token
        
    Returns:
        Token JWT válido
    """
    # Buscar usuario con ese rol
    user = None
    for u in FAKE_USERS_DB.values():
        if u.role == role:
            user = u
            break
    
    if not user:
        raise ValueError(f"No existe usuario con rol {role}")
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "email": user.email,
            "role": user.role.value
        }
    )
    return access_token


# ============================================================
# EJEMPLO DE USO / EKZEMPLO DE UZO / USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("🔐 Sistema de Autenticación - Labortrovilo")
    print("="*60)
    
    # Crear tokens de demo para cada rol
    print("\n📋 Tokens de Demo Generados:\n")
    
    for role in UserRole:
        token = create_demo_token(role)
        print(f"{role.value.upper()}:")
        print(f"Token: {token[:50]}...")
        print(f"Válido por: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
        print()
    
    # Test de autenticación
    print("\n🧪 Test de Autenticación:")
    user = authenticate_user("candidato", "password123")
    if user:
        print(f"✓ Usuario autenticado: {user.username} ({user.role.value})")
    
    # Test de permisos
    print("\n🔑 Test de Permisos:")
    print(f"¿CANDIDATO puede acceder a endpoint HR_PRO? {check_role_permission(UserRole.CANDIDATO, UserRole.HR_PRO)}")
    print(f"¿HR_PRO puede acceder a endpoint CANDIDATO? {check_role_permission(UserRole.HR_PRO, UserRole.CANDIDATO)}")
    print(f"¿SUPERUSER puede acceder a todo? {check_role_permission(UserRole.SUPERUSER, UserRole.ADMIN)}")
