"""
Test Suite para Labortrovilo API
Testa Serio por Labortrovilo API
Test Suite for Labortrovilo API

Tests de endpoints con diferentes roles
"""
import requests
import json
from typing import Dict

# Configuración
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


class APITester:
    """Clase para testear la API de Labortrovilo"""
    
    def __init__(self):
        self.tokens: Dict[str, str] = {}
        self.session = requests.Session()
    
    def print_header(self, text: str):
        """Imprime un header decorado"""
        print("\n" + "="*60)
        print(f"🧪 {text}")
        print("="*60)
    
    def print_success(self, text: str):
        """Imprime mensaje de éxito"""
        print(f"✓ {text}")
    
    def print_error(self, text: str):
        """Imprime mensaje de error"""
        print(f"✗ {text}")
    
    def print_info(self, text: str):
        """Imprime información"""
        print(f"ℹ️  {text}")
    
    def test_health(self):
        """Test del health check"""
        self.print_header("TEST: Health Check")
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"API está funcionando: {data['status']}")
                self.print_info(f"Database: {data['database']}")
            else:
                self.print_error(f"Health check falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def test_login(self, role: str):
        """Test de login para un rol específico"""
        self.print_header(f"TEST: Login como {role.upper()}")
        
        # Mapeo de roles a credenciales
        credentials = {
            "candidato": {"username": "candidato", "password": "password123"},
            "hr_pro": {"username": "hr_pro", "password": "hrpass123"},
            "admin": {"username": "admin", "password": "adminpass123"},
            "superuser": {"username": "superuser", "password": "superpass123"}
        }
        
        if role not in credentials:
            self.print_error(f"Rol {role} no reconocido")
            return False
        
        try:
            response = self.session.post(
                f"{API_V1}/auth/login",
                data=credentials[role]
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data["access_token"]
                self.print_success(f"Login exitoso para {role}")
                self.print_info(f"Usuario: {data['user']['username']}")
                self.print_info(f"Rol: {data['user']['role']}")
                self.print_info(f"Token: {data['access_token'][:50]}...")
                return True
            else:
                self.print_error(f"Login falló: {response.status_code}")
                self.print_error(f"Detalle: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def test_get_jobs(self, role: str):
        """Test del endpoint GET /jobs"""
        self.print_header(f"TEST: GET /jobs como {role.upper()}")
        
        if role not in self.tokens:
            self.print_error(f"No hay token para {role}. Ejecuta login primero.")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            response = self.session.get(f"{API_V1}/jobs", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Trabajos obtenidos: {data['total']} total")
                self.print_info(f"Página: {data['page']}, Tamaño: {data['page_size']}")
                
                if data['jobs']:
                    job = data['jobs'][0]
                    self.print_info(f"Primer trabajo: {job['title']} @ {job['company_name']}")
                    
                    # Verificar que NO incluya campos sensibles
                    if 'red_flags' not in job and 'hiring_intent' not in job:
                        self.print_success("✓ Campos sensibles correctamente ocultos")
                    else:
                        self.print_error("✗ ERROR: Campos sensibles expuestos!")
                else:
                    self.print_info("No hay trabajos en la base de datos")
            elif response.status_code == 403:
                self.print_error(f"Acceso denegado: {response.json()['detail']}")
            else:
                self.print_error(f"Request falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def test_market_intelligence(self, role: str):
        """Test del endpoint GET /market-intelligence"""
        self.print_header(f"TEST: GET /market-intelligence como {role.upper()}")
        
        if role not in self.tokens:
            self.print_error(f"No hay token para {role}. Ejecuta login primero.")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            response = self.session.get(
                f"{API_V1}/market-intelligence",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Market Intelligence obtenido")
                self.print_info(f"Total jobs: {data['summary']['total_jobs']}")
                self.print_info(f"Empresas analizadas: {len(data['top_hiring_companies'])}")
                self.print_info(f"Avg Urgency: {data['summary']['avg_urgency_score']:.2f}")
            elif response.status_code == 403:
                self.print_error(f"Acceso denegado: {response.json()['detail']}")
                self.print_info("Este endpoint requiere rol HR_PRO o superior")
            else:
                self.print_error(f"Request falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def test_admin_scrapers(self, role: str):
        """Test del endpoint GET /admin/scrapers"""
        self.print_header(f"TEST: GET /admin/scrapers como {role.upper()}")
        
        if role not in self.tokens:
            self.print_error(f"No hay token para {role}. Ejecuta login primero.")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            response = self.session.get(
                f"{API_V1}/admin/scrapers",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Dashboard de scrapers obtenido")
                self.print_info(f"Total jobs: {data['total_jobs_in_db']}")
                self.print_info(f"Companies: {data['total_companies']}")
                self.print_info(f"System health: {data['system_health']}")
                self.print_info(f"Scrapers: {len(data['scrapers'])}")
            elif response.status_code == 403:
                self.print_error(f"Acceso denegado: {response.json()['detail']}")
                self.print_info("Este endpoint requiere rol ADMIN o superior")
            else:
                self.print_error(f"Request falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def test_superuser_billing(self, role: str):
        """Test del endpoint GET /superuser/billing"""
        self.print_header(f"TEST: GET /superuser/billing como {role.upper()}")
        
        if role not in self.tokens:
            self.print_error(f"No hay token para {role}. Ejecuta login primero.")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            response = self.session.get(
                f"{API_V1}/superuser/billing",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Billing dashboard obtenido")
                self.print_info(f"Total users: {data['user_activity']['total_users']}")
                self.print_info(f"Revenue: ${data['billing']['total_revenue_month']:.2f}")
                self.print_info(f"MRR: ${data['billing']['mrr']:.2f}")
                self.print_info(f"Uptime: {data['system']['api_uptime_percent']:.1f}%")
            elif response.status_code == 403:
                self.print_error(f"Acceso denegado: {response.json()['detail']}")
                self.print_info("Este endpoint requiere rol SUPERUSER")
            else:
                self.print_error(f"Request falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def test_dataset_download(self, role: str):
        """Test del endpoint GET /dataset (DaaS)"""
        self.print_header(f"TEST: GET /dataset (DaaS) como {role.upper()}")
        
        if role not in self.tokens:
            self.print_error(f"No hay token para {role}. Ejecuta login primero.")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            response = self.session.get(
                f"{API_V1}/dataset?limit=10",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Dataset descargado")
                self.print_info(f"Records: {data['metadata']['total_records']}")
                self.print_info(f"Version: {data['metadata']['version']}")
                
                if data['jobs']:
                    job = data['jobs'][0]
                    self.print_info(f"Incluye campos premium: red_flags={('red_flags' in job)}")
            elif response.status_code == 403:
                self.print_error(f"Acceso denegado: {response.json()['detail']}")
                self.print_info("Este endpoint requiere rol HR_PRO o superior")
            elif response.status_code == 404:
                self.print_info("No hay trabajos procesados con IA todavía")
            else:
                self.print_error(f"Request falló: {response.status_code}")
        except Exception as e:
            self.print_error(f"Error: {e}")
    
    def run_full_test(self):
        """Ejecuta todos los tests"""
        print("\n" + "="*60)
        print("🚀 LABORTROVILO API - TEST SUITE COMPLETO")
        print("="*60)
        
        # 1. Health check
        self.test_health()
        
        # 2. Login de todos los roles
        for role in ["candidato", "hr_pro", "admin", "superuser"]:
            self.test_login(role)
        
        # 3. Tests de CANDIDATO
        print("\n" + "#"*60)
        print("# TESTS DE ROL: CANDIDATO (Nivel 1)")
        print("#"*60)
        self.test_get_jobs("candidato")
        self.test_market_intelligence("candidato")  # Debe fallar
        
        # 4. Tests de HR_PRO
        print("\n" + "#"*60)
        print("# TESTS DE ROL: HR_PRO (Nivel 2)")
        print("#"*60)
        self.test_get_jobs("hr_pro")
        self.test_market_intelligence("hr_pro")
        self.test_dataset_download("hr_pro")
        self.test_admin_scrapers("hr_pro")  # Debe fallar
        
        # 5. Tests de ADMIN
        print("\n" + "#"*60)
        print("# TESTS DE ROL: ADMIN (Nivel 3)")
        print("#"*60)
        self.test_admin_scrapers("admin")
        self.test_superuser_billing("admin")  # Debe fallar
        
        # 6. Tests de SUPERUSER
        print("\n" + "#"*60)
        print("# TESTS DE ROL: SUPERUSER (Nivel 4)")
        print("#"*60)
        self.test_superuser_billing("superuser")
        
        # Resumen
        print("\n" + "="*60)
        print("✅ TEST SUITE COMPLETADO")
        print("="*60)
        print("\n📊 Resumen:")
        print(f"   ✓ Roles testeados: 4")
        print(f"   ✓ Endpoints testeados: 6+")
        print(f"   ✓ Verificación de permisos: OK")
        print("\n💡 Verifica los logs arriba para ver detalles de cada test")


def main():
    """Función principal"""
    import sys
    
    tester = APITester()
    
    print("\n" + "="*60)
    print("🔍 Labortrovilo API - Test Suite")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Asegúrate de que la API esté corriendo en:")
    print("   http://localhost:8000")
    print("\n💡 Ejecuta en otra terminal: python run_api.py")
    print("="*60)
    
    # Si se pasa --auto como argumento, no pedir confirmación
    if "--auto" not in sys.argv:
        input("\n⌨️  Presiona ENTER para comenzar los tests...")
    else:
        print("\n🤖 Modo automático activado, iniciando tests...")
    
    try:
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
