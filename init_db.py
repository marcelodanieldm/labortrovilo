"""
Script para inicializar la base de datos y crear usuarios de prueba
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from datetime import datetime
import sys

# Importar configuración y modelos
from config import settings

# Importar Base del archivo correcto
sys.path.insert(0, '.')
from models import Base, User, UserRole, SubscriptionTier, SubscriptionStatus

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt directamente"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_database():
    """Inicializa las tablas de la base de datos"""
    print("🔧 Inicializando base de datos...")
    engine = create_engine(settings.DATABASE_URL)
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")
    
    return engine

def create_demo_users(engine):
    """Crea usuarios de demostración"""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Verificar si ya existen usuarios
        existing_users = session.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Ya existen {existing_users} usuarios en la base de datos")
            response = input("¿Deseas crear usuarios de prueba de todas formas? (s/n): ")
            if response.lower() != 's':
                print("❌ Operación cancelada")
                return
        
        users_to_create = [
            {
                "email": "candidato@test.com",
                "password": "test123",
                "full_name": "Juan Candidato",
                "role": UserRole.CANDIDATO,
                "subscription_tier": SubscriptionTier.FREE
            },
            {
                "email": "hr@test.com",
                "password": "test123",
                "full_name": "María HR Professional",
                "role": UserRole.HR_PRO,
                "subscription_tier": SubscriptionTier.HR_PRO_PLAN,
                "api_credits": 1000
            },
            {
                "email": "admin@test.com",
                "password": "admin123",
                "full_name": "Admin Sistema",
                "role": UserRole.ADMIN,
                "subscription_tier": SubscriptionTier.CANDIDATO_PREMIUM
            },
            {
                "email": "super@test.com",
                "password": "super123",
                "full_name": "Super Usuario",
                "role": UserRole.SUPERUSER,
                "subscription_tier": SubscriptionTier.CANDIDATO_PREMIUM
            }
        ]
        
        print("\n👥 Creando usuarios de prueba...")
        for user_data in users_to_create:
            # Verificar si el usuario ya existe
            existing = session.query(User).filter_by(email=user_data["email"]).first()
            if existing:
                print(f"⚠️  Usuario {user_data['email']} ya existe, saltando...")
                continue
            
            password = user_data.pop("password")
            user = User(
                **user_data,
                hashed_password=hash_password(password),
                subscription_status=SubscriptionStatus.ACTIVE,
                created_at=datetime.utcnow()
            )
            session.add(user)
            print(f"✅ Creado: {user_data['email']} | Rol: {user_data['role'].value}")
        
        session.commit()
        print("\n🎉 ¡Usuarios creados exitosamente!")
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("📋 CREDENCIALES DE PRUEBA:")
        print("="*70)
        print("\n🆓 Candidato FREE:")
        print("   Email: candidato@test.com")
        print("   Password: test123")
        print("\n💼 HR Professional:")
        print("   Email: hr@test.com")
        print("   Password: test123")
        print("   Créditos API: 1000")
        print("\n👨‍💼 Administrador:")
        print("   Email: admin@test.com")
        print("   Password: admin123")
        print("\n🔐 Super Usuario:")
        print("   Email: super@test.com")
        print("   Password: super123")
        print("="*70)
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error al crear usuarios: {e}")
        raise
    finally:
        session.close()

def list_existing_users(engine):
    """Lista todos los usuarios existentes"""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        users = session.query(User).all()
        
        if not users:
            print("\n❌ No hay usuarios en la base de datos")
            return
        
        print(f"\n✅ Usuarios existentes ({len(users)}):")
        print("="*70)
        
        for user in users:
            print(f"\nID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Nombre: {user.full_name}")
            print(f"Rol: {user.role.value}")
            print(f"Tier: {user.subscription_tier.value}")
            print(f"Créditos API: {user.api_credits}")
            print(f"Activo: {'Sí' if user.is_active else 'No'}")
            print("-"*70)
            
    except Exception as e:
        print(f"❌ Error al listar usuarios: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("\n🚀 Labortrovilo - Inicialización de Base de Datos\n")
    
    # Inicializar base de datos
    engine = init_database()
    
    # Listar usuarios existentes
    list_existing_users(engine)
    
    # Crear usuarios de prueba
    print("\n")
    create_demo_users(engine)
    
    # Listar usuarios después de crear
    list_existing_users(engine)
