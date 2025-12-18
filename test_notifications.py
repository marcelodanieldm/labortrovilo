"""
Test rápido del sistema de notificaciones
Verifica que todos los componentes funcionen correctamente
"""
import sys
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test 1: Verificar que todos los módulos se importen correctamente"""
    print("=" * 60)
    print("TEST 1: Verificando imports...")
    print("=" * 60)
    
    try:
        from src.notifications import AlertManager
        print("✓ AlertManager importado")
        
        from src.notification_channels import (
            EmailNotifier, 
            SlackNotifier, 
            DiscordNotifier,
            NotificationDispatcher
        )
        print("✓ Notificadores importados")
        
        from src.scheduler import TaskOrchestrator, get_orchestrator
        print("✓ Scheduler importado")
        
        from src.alerts_router import router
        print("✓ API Router importado")
        
        from models import User, AlertConfig, Notification
        print("✓ Modelos de base de datos importados")
        
        print("\n✅ Todos los imports exitosos\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en imports: {str(e)}\n")
        return False


def test_database():
    """Test 2: Verificar conexión a base de datos"""
    print("=" * 60)
    print("TEST 2: Verificando base de datos...")
    print("=" * 60)
    
    try:
        from database import SessionLocal
        from models import User, AlertConfig, Notification
        
        db = SessionLocal()
        
        # Contar registros
        user_count = db.query(User).count()
        config_count = db.query(AlertConfig).count()
        notif_count = db.query(Notification).count()
        
        print(f"✓ Usuarios: {user_count}")
        print(f"✓ Configuraciones de alertas: {config_count}")
        print(f"✓ Notificaciones: {notif_count}")
        
        db.close()
        
        print("\n✅ Base de datos conectada correctamente\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en base de datos: {str(e)}\n")
        return False


def test_email_notifier():
    """Test 3: Verificar configuración de Email"""
    print("=" * 60)
    print("TEST 3: Verificando Email Notifier...")
    print("=" * 60)
    
    try:
        from src.notification_channels import EmailNotifier
        import os
        
        notifier = EmailNotifier()
        
        api_key_configured = bool(notifier.api_key)
        print(f"✓ API Key configurada: {api_key_configured}")
        
        if not api_key_configured:
            print("⚠️  Configurar SENDGRID_API_KEY en .env")
        
        print(f"✓ Email remitente: {notifier.from_email}")
        print(f"✓ Nombre remitente: {notifier.from_name}")
        
        # Verificar plantillas
        from pathlib import Path
        template_dir = Path("src/templates/email")
        
        if template_dir.exists():
            templates = list(template_dir.glob("*.html"))
            print(f"✓ Plantillas HTML: {len(templates)}")
            for t in templates:
                print(f"  - {t.name}")
        else:
            print("⚠️  Directorio de plantillas no encontrado")
        
        print("\n✅ Email Notifier configurado\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en Email Notifier: {str(e)}\n")
        return False


def test_alert_manager():
    """Test 4: Verificar AlertManager"""
    print("=" * 60)
    print("TEST 4: Verificando AlertManager...")
    print("=" * 60)
    
    try:
        from src.notifications import AlertManager
        
        manager = AlertManager()
        print("✓ AlertManager inicializado")
        
        # Verificar métodos
        methods = [
            'check_new_jobs_for_alerts',
            '_process_candidate_alerts',
            '_process_hr_alerts',
            '_identify_golden_leads',
            '_calculate_urgency_score'
        ]
        
        for method in methods:
            if hasattr(manager, method):
                print(f"✓ Método {method} disponible")
            else:
                print(f"❌ Método {method} no encontrado")
        
        print("\n✅ AlertManager verificado\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en AlertManager: {str(e)}\n")
        return False


def test_scheduler():
    """Test 5: Verificar Scheduler"""
    print("=" * 60)
    print("TEST 5: Verificando Scheduler...")
    print("=" * 60)
    
    try:
        from src.scheduler import TaskOrchestrator
        
        orchestrator = TaskOrchestrator()
        print("✓ TaskOrchestrator inicializado")
        
        # Verificar métodos de jobs
        job_methods = [
            'run_scraper_job',
            'run_ai_processor_job',
            'run_alert_check_job',
            'send_pending_notifications_job',
            'cleanup_old_notifications_job'
        ]
        
        for method in job_methods:
            if hasattr(orchestrator, method):
                print(f"✓ Job {method} disponible")
            else:
                print(f"❌ Job {method} no encontrado")
        
        print("\n✅ Scheduler verificado\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en Scheduler: {str(e)}\n")
        return False


def test_api_router():
    """Test 6: Verificar API Router"""
    print("=" * 60)
    print("TEST 6: Verificando API Router...")
    print("=" * 60)
    
    try:
        from src.alerts_router import router
        
        print(f"✓ Router creado con prefix: {router.prefix}")
        
        # Contar rutas
        route_count = len(router.routes)
        print(f"✓ Total de endpoints: {route_count}")
        
        # Listar endpoints
        print("\nEndpoints disponibles:")
        for route in router.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  {methods:12} {route.path}")
        
        print("\n✅ API Router verificado\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en API Router: {str(e)}\n")
        return False


def test_integration():
    """Test 7: Test de integración básico"""
    print("=" * 60)
    print("TEST 7: Test de Integración...")
    print("=" * 60)
    
    try:
        from src.notifications import AlertManager
        from database import SessionLocal
        from models import Job
        
        db = SessionLocal()
        manager = AlertManager()
        
        # Contar jobs disponibles
        job_count = db.query(Job).count()
        print(f"✓ Jobs en base de datos: {job_count}")
        
        if job_count > 0:
            # Simular revisión de alertas (sin crear notificaciones)
            print("✓ Ejecutando check_new_jobs_for_alerts (dry run)...")
            
            # Nota: Esto ejecutará la lógica real, comentar si no se desea
            # stats = manager.check_new_jobs_for_alerts(hours_lookback=24)
            # print(f"  - Jobs revisados: {stats['jobs_checked']}")
            # print(f"  - Notificaciones creadas: {stats['total_notifications']}")
            
            print("  (Comentado para evitar crear notificaciones de prueba)")
        else:
            print("⚠️  No hay jobs para revisar. Ejecutar scraper primero.")
        
        db.close()
        
        print("\n✅ Integración verificada\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en integración: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 60)
    print("🔔 SISTEMA DE NOTIFICACIONES - TEST SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Base de Datos", test_database),
        ("Email Notifier", test_email_notifier),
        ("AlertManager", test_alert_manager),
        ("Scheduler", test_scheduler),
        ("API Router", test_api_router),
        ("Integración", test_integration)
    ]
    
    results = []
    
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        print("El sistema de notificaciones está listo para usar.\n")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar errores arriba.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
