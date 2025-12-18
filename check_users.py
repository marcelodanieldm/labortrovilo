"""
Script para revisar usuarios en la base de datos
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

# Crear conexión a la base de datos
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_users():
    """Revisa todos los usuarios en la base de datos"""
    session = SessionLocal()
    try:
        # Consultar todos los usuarios
        result = session.execute(text("""
            SELECT id, email, role, is_active, credits, created_at 
            FROM users 
            ORDER BY created_at DESC
        """))
        
        users = result.fetchall()
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            print("\n📝 Tablas disponibles:")
            tables_result = session.execute(text("""
                SELECT name FROM sqlite_master WHERE type='table'
            """))
            for table in tables_result.fetchall():
                print(f"  - {table[0]}")
            return
        
        print(f"\n✅ Encontrados {len(users)} usuarios:\n")
        print("=" * 100)
        
        for user in users:
            user_id, email, role, is_active, credits, created_at = user
            status = "🟢 Activo" if is_active else "🔴 Inactivo"
            print(f"""
ID: {user_id}
Email: {email}
Rol: {role}
Estado: {status}
Créditos: {credits}
Creado: {created_at}
{"-" * 100}
""")
        
    except Exception as e:
        print(f"❌ Error al consultar usuarios: {e}")
        print("\n📋 Intentando ver la estructura de la base de datos...")
        try:
            tables_result = session.execute(text("""
                SELECT name FROM sqlite_master WHERE type='table'
            """))
            print("\nTablas disponibles:")
            for table in tables_result.fetchall():
                print(f"  - {table[0]}")
        except Exception as e2:
            print(f"Error al listar tablas: {e2}")
    finally:
        session.close()

if __name__ == "__main__":
    check_users()
