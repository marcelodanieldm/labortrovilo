"""
Script simple para verificar la base de datos
"""
import sqlite3
import os

db_path = "labortrovilo.db"

if not os.path.exists(db_path):
    print(f"❌ La base de datos {db_path} no existe")
else:
    print(f"✅ Base de datos encontrada: {db_path}")
    
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ver qué tablas existen
print("\n📋 Tablas en la base de datos:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print("  ❌ No hay tablas creadas")
else:
    for table in tables:
        print(f"  - {table[0]}")
        
        # Contar registros en cada tabla
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    └─ {count} registros")
        except:
            pass

# Si existe la tabla users, mostrar los usuarios
if any(t[0] == 'users' for t in tables):
    print("\n👥 Usuarios:")
    cursor.execute("SELECT id, email, role, is_active, credits FROM users")
    users = cursor.fetchall()
    
    if users:
        for user in users:
            print(f"\n  ID: {user[0]}")
            print(f"  Email: {user[1]}")
            print(f"  Rol: {user[2]}")
            print(f"  Activo: {'Sí' if user[3] else 'No'}")
            print(f"  Créditos: {user[4]}")
            print("  " + "-" * 40)
    else:
        print("  ❌ No hay usuarios registrados")

conn.close()
