"""
Test del Módulo de IA para Labortrovilo
AI-Modula Testo por Labortrovilo
AI Module Test for Labortrovilo

Script de prueba para el procesador de IA
"""
import asyncio
import logging
from datetime import datetime

from src.database import init_db, get_db
from src.models import Job, Company
from src.ai_processor import get_ai_processor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_jobs():
    """
    Crea trabajos de ejemplo en la BD para testing
    Kreas ekzemplajn laborojn en la datumbazo por testado
    Creates sample jobs in DB for testing
    """
    logger.info("📝 Creando trabajos de ejemplo para testing...")
    
    with get_db() as db:
        # Verificar si ya existen trabajos de ejemplo
        existing = db.query(Job).filter(Job.title.like('%TEST:%')).count()
        if existing > 0:
            logger.info(f"⚠️ Ya existen {existing} trabajos de prueba")
            response = input("¿Quieres eliminarlos y crear nuevos? (s/n): ")
            if response.lower() == 's':
                db.query(Job).filter(Job.title.like('%TEST:%')).delete()
                db.commit()
                logger.info("✓ Trabajos de prueba anteriores eliminados")
            else:
                logger.info("⏭️ Usando trabajos existentes")
                return
        
        # Crear empresa de prueba
        company = Company(
            name="TEST: TechStartup Inc",
            industry="Technology",
            company_size="startup"
        )
        db.add(company)
        db.commit()
        
        # Trabajo 1: Senior Backend Engineer
        job1 = Job(
            title="TEST: Senior Backend Engineer",
            company_id=company.id,
            company_name=company.name,
            description="""
We're looking for an experienced Senior Backend Engineer to join our growing team!

Requirements:
- 5+ years of experience with Python and Django
- Strong knowledge of PostgreSQL and Redis
- Experience with AWS (EC2, S3, Lambda)
- Docker and Kubernetes
- RESTful API design

Responsibilities:
- Design and implement scalable backend services
- Mentor junior developers
- Lead technical architecture decisions
- Work with cross-functional teams

We offer:
- Competitive salary: $120,000 - $160,000
- Fully remote work
- Health insurance and 401k
- Flexible hours

We're rapidly expanding our engineering team to support new product launches.
            """,
            location="San Francisco, CA (Remote)",
            is_remote=True,
            url="https://example.com/jobs/test-1",
            source_platform="test",
            posted_date=datetime.utcnow(),
            ai_processed=False
        )
        
        # Trabajo 2: Junior Frontend Developer
        job2 = Job(
            title="TEST: Junior Frontend Developer",
            company_id=company.id,
            company_name=company.name,
            description="""
Join our team as a Junior Frontend Developer!

We're looking for:
- 0-2 years of experience
- Knowledge of React, TypeScript, and HTML/CSS
- Basic understanding of responsive design
- Git and version control

What you'll do:
- Build user interfaces for our web app
- Collaborate with designers and backend team
- Learn from senior developers

Salary: $60,000 - $80,000
Location: New York, NY (Hybrid - 3 days in office)

This is a replacement position for a developer who recently left the team.
            """,
            location="New York, NY",
            is_remote=False,
            url="https://example.com/jobs/test-2",
            source_platform="test",
            posted_date=datetime.utcnow(),
            ai_processed=False
        )
        
        # Trabajo 3: Full Stack "Ninja" (red flags example)
        job3 = Job(
            title="TEST: Full Stack Ninja Rockstar",
            company_id=company.id,
            company_name=company.name,
            description="""
We need a full-stack ninja who can do it all!

Requirements (MUST HAVE ALL):
- 10+ years experience with: Python, Java, Ruby, Go, Rust, JavaScript, PHP
- Expert in: React, Angular, Vue, Svelte, jQuery
- Databases: PostgreSQL, MySQL, MongoDB, Redis, Cassandra, DynamoDB
- DevOps: AWS, Azure, GCP, Kubernetes, Docker, Terraform
- Mobile: iOS (Swift), Android (Kotlin), React Native, Flutter
- Blockchain development with Solidity
- Machine Learning with TensorFlow and PyTorch

We offer competitive salary (salary TBD) and work hard play hard culture!

You must be available 24/7 for urgent issues. Flexible hours means you work whenever we need you!
            """,
            location="Anywhere",
            is_remote=True,
            url="https://example.com/jobs/test-3",
            source_platform="test",
            posted_date=datetime.utcnow(),
            ai_processed=False
        )
        
        db.add_all([job1, job2, job3])
        db.commit()
        
        logger.info("✓ 3 trabajos de ejemplo creados exitosamente")


def test_single_job_processing():
    """
    Test de procesamiento de un solo trabajo
    Testo de traktado de unu sola laboro
    Test processing of a single job
    """
    logger.info("\n" + "="*80)
    logger.info("🧪 TEST 1: Procesamiento de un solo trabajo")
    logger.info("="*80)
    
    try:
        # Inicializar procesador
        processor = get_ai_processor(provider="openai")
        
        # Obtener primer trabajo no procesado
        with get_db() as db:
            job = db.query(Job).filter(Job.ai_processed == False).first()
            
            if not job:
                logger.warning("⚠️ No hay trabajos sin procesar")
                return
            
            logger.info(f"\n📋 Trabajo a procesar:")
            logger.info(f"   ID: {job.id}")
            logger.info(f"   Título: {job.title}")
            logger.info(f"   Empresa: {job.company_name}")
            
            # Procesar
            result = processor.process_description({
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'description': job.description
            })
            
            if result:
                logger.info("\n✓ Resultado de IA:")
                logger.info(f"   Tech Stack: {result.get('tech_stack', [])}")
                logger.info(f"   Seniority: {result.get('seniority_level')}")
                logger.info(f"   Remote: {result.get('is_remote')}")
                logger.info(f"   Salary Estimate: {result.get('salary_estimate')}")
                logger.info(f"   Hiring Intent: {result.get('hiring_intent')}")
                logger.info(f"   Red Flags: {result.get('red_flags', [])}")
            else:
                logger.error("✗ No se pudo procesar el trabajo")
        
        logger.info("\n✓ Test completado exitosamente")
        
    except Exception as e:
        logger.error(f"\n✗ Error en test: {e}")
        import traceback
        logger.error(traceback.format_exc())


def test_batch_processing():
    """
    Test de procesamiento en lote
    Testo de amasa traktado
    Test batch processing
    """
    logger.info("\n" + "="*80)
    logger.info("🧪 TEST 2: Procesamiento en lote con enrich_job_data()")
    logger.info("="*80)
    
    try:
        # Inicializar procesador
        processor = get_ai_processor(provider="openai")
        
        # Procesar múltiples trabajos
        stats = processor.enrich_job_data(limit=5)
        
        logger.info("\n✓ Test de lote completado")
        
    except Exception as e:
        logger.error(f"\n✗ Error en test: {e}")
        import traceback
        logger.error(traceback.format_exc())


def test_cache_system():
    """
    Test del sistema de caché
    Testo de la kaŝmemora sistemo
    Test cache system
    """
    logger.info("\n" + "="*80)
    logger.info("🧪 TEST 3: Sistema de caché")
    logger.info("="*80)
    
    try:
        processor = get_ai_processor(provider="openai")
        
        with get_db() as db:
            job = db.query(Job).filter(Job.ai_processed == True).first()
            
            if not job:
                logger.warning("⚠️ No hay trabajos procesados para test de caché")
                logger.info("   Ejecuta primero test_batch_processing()")
                return
            
            logger.info(f"\n📋 Reprocesando trabajo ya procesado:")
            logger.info(f"   ID: {job.id}")
            logger.info(f"   Hash: {job.description_hash[:8]}...")
            
            # Primera llamada - debería usar caché
            logger.info("\n🔄 Primera llamada (debería usar caché):")
            result1 = processor.process_description({
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'description': job.description
            })
            
            # Segunda llamada - también debería usar caché
            logger.info("\n🔄 Segunda llamada (también debería usar caché):")
            result2 = processor.process_description({
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'description': job.description
            })
            
            if result1 == result2:
                logger.info("\n✓ Caché funcionando correctamente - resultados idénticos")
            else:
                logger.warning("\n⚠️ Resultados diferentes - verificar caché")
        
    except Exception as e:
        logger.error(f"\n✗ Error en test: {e}")
        import traceback
        logger.error(traceback.format_exc())


def view_processed_jobs():
    """
    Muestra todos los trabajos procesados por IA
    Montras ĉiujn AI-traktitajn laborojn
    Shows all AI-processed jobs
    """
    logger.info("\n" + "="*80)
    logger.info("📊 TRABAJOS PROCESADOS POR IA")
    logger.info("="*80)
    
    with get_db() as db:
        jobs = db.query(Job).filter(Job.ai_processed == True).all()
        
        if not jobs:
            logger.info("\n⚠️ No hay trabajos procesados todavía")
            return
        
        logger.info(f"\n✓ Total de trabajos procesados: {len(jobs)}")
        
        for i, job in enumerate(jobs, 1):
            logger.info(f"\n--- Trabajo #{i} ---")
            logger.info(f"ID: {job.id}")
            logger.info(f"Título: {job.title}")
            logger.info(f"Empresa: {job.company_name}")
            logger.info(f"Seniority: {job.seniority_level}")
            logger.info(f"Salary Estimate: {job.salary_estimate}")
            logger.info(f"Hiring Intent: {job.hiring_intent}")
            logger.info(f"Remote: {job.is_remote}")
            
            # Tech stack
            if job.stack:
                import json
                try:
                    stack = json.loads(job.stack)
                    logger.info(f"Tech Stack: {', '.join(stack)}")
                except:
                    logger.info(f"Tech Stack: {job.stack}")
            
            # Red flags
            if job.red_flags:
                import json
                try:
                    flags = json.loads(job.red_flags)
                    logger.info(f"Red Flags: {len(flags)}")
                    for flag in flags:
                        logger.info(f"  ⚠️ {flag}")
                except:
                    logger.info(f"Red Flags: {job.red_flags}")
            
            logger.info(f"Procesado: {job.ai_processed_at}")


def main():
    """Menú principal de tests"""
    print("\n" + "="*80)
    print("🤖 LABORTROVILO - TEST SUITE DE IA")
    print("   Senior AI Engineer Module")
    print("="*80)
    
    # Inicializar BD
    init_db()
    
    # Menú
    while True:
        print("\n📋 Opciones de test:")
        print("1. Crear trabajos de ejemplo")
        print("2. Test de procesamiento individual")
        print("3. Test de procesamiento en lote")
        print("4. Test de sistema de caché")
        print("5. Ver trabajos procesados")
        print("6. Salir")
        
        try:
            choice = input("\nSelecciona una opción (1-6): ").strip()
            
            if choice == '1':
                create_sample_jobs()
            elif choice == '2':
                test_single_job_processing()
            elif choice == '3':
                test_batch_processing()
            elif choice == '4':
                test_cache_system()
            elif choice == '5':
                view_processed_jobs()
            elif choice == '6':
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por usuario")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
