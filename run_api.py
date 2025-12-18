"""
Script de Inicio Rápido para Labortrovilo API
Rapida Starta Skripto por Labortrovilo API
Quick Start Script for Labortrovilo API

Ejecuta la API con uvicorn
"""
import uvicorn
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("="*60)
    print("🚀 Iniciando Labortrovilo API...")
    print("="*60)
    print("\n📚 Documentación disponible en:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n🔐 Usuarios de demo:")
    print("   - CANDIDATO:  username=candidato,  password=password123")
    print("   - HR_PRO:     username=hr_pro,     password=hrpass123")
    print("   - ADMIN:      username=admin,      password=adminpass123")
    print("   - SUPERUSER:  username=superuser,  password=superpass123")
    print("\n⌨️  Presiona CTRL+C para detener el servidor")
    print("="*60)
    print()
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
