"""
Script de Test Básico para Labortrovilo Scraper
Skripto por Baza Testo de Labortrovilo Skrapilo
Basic Test Script for Labortrovilo Scraper

Senior Data Engineer - Testing Module
"""
import asyncio
import logging
from datetime import datetime

from src.scraper_engine import LabortroviloScraper
from src.database import init_db, db_manager
from config import settings

# Configurar logging para tests / Agordi registradon por testoj
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_basic_scraping():
    """
    Test básico del motor de scraping / Baza testo de la skrapada motoro
    """
    logger.info("="*80)
    logger.info("🧪 INICIANDO TEST BÁSICO DE LABORTROVILO SCRAPER")
    logger.info("="*80)
    
    # Paso 1: Inicializar base de datos / Paŝo 1: Ekigi datumbazon
    logger.info("\n📊 Paso 1: Inicializando base de datos...")
    init_db()
    
    # Verificar salud de BD / Kontroli datumbazan sanon
    if db_manager.health_check():
        logger.info("✓ Base de datos OK")
    else:
        logger.error("✗ Problemas con la base de datos")
        return
    
    # Paso 2: Crear instancia del scraper / Paŝo 2: Krei skrapilan ekzempleron
    logger.info("\n🤖 Paso 2: Creando instancia de LabortroviloScraper...")
    scraper = LabortroviloScraper(headless=settings.PLAYWRIGHT_HEADLESS)
    
    try:
        # Paso 3: Inicializar navegador / Paŝo 3: Ekigi retumilon
        logger.info("\n🌐 Paso 3: Inicializando navegador Playwright...")
        await scraper.initialize()
        
        # Paso 4: URLs de prueba / Paŝo 4: Provaj URL-oj
        logger.info("\n🔗 Paso 4: Preparando URLs de prueba...")
        
        # URLs reales de Work at a Startup (YCombinator) - estructura HTML limpia
        # Realaj URL-oj de Work at a Startup (YCombinator) - pura HTML-strukturo
        test_urls = [
            # YCombinator Work at a Startup - ejemplos de trabajos tech
            "https://www.workatastartup.com/jobs/64891",  # Software Engineer
            "https://www.workatastartup.com/jobs/64890",  # Backend Engineer
            
            # Puedes agregar más URLs de prueba aquí:
            # Greenhouse examples (si tienes URLs específicas):
            # "https://boards.greenhouse.io/yourcompany/jobs/123456",
            
            # Lever examples (si tienes URLs específicas):
            # "https://jobs.lever.co/yourcompany/job-id",
        ]
        
        if not test_urls or not test_urls[0]:
            logger.warning("⚠️ NO HAY URLs DE PRUEBA CONFIGURADAS")
            logger.warning("⚠️ Por favor, edita test_scraper.py y agrega URLs reales")
            logger.warning("⚠️ Los selectores genéricos necesitan personalización por ATS")
            logger.info("\n✓ Test de inicialización completado exitosamente")
            logger.info("✓ El scraper está listo para usarse con URLs reales")
            return
        
        # Paso 5: Ejecutar scraping / Paŝo 5: Plenumi skrapadon
        logger.info(f"\n🚀 Paso 5: Ejecutando scraping de {len(test_urls)} URLs...")
        results = await scraper.scrape_multiple_jobs(test_urls)
        
        # Paso 6: Analizar resultados / Paŝo 6: Analizi rezultojn
        logger.info("\n📈 Paso 6: Analizando resultados...")
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"   Exitosos: {successful}/{len(results)}")
        logger.info(f"   Fallidos: {failed}/{len(results)}")
        
        # Mostrar detalles de cada resultado / Montri detalojn de ĉiu rezulto
        for i, result in enumerate(results, 1):
            status = "✓" if result.success else "✗"
            logger.info(f"\n   Resultado {i}: {status}")
            logger.info(f"      URL: {result.url}")
            if result.job_data:
                logger.info(f"      Título: {result.job_data.title}")
                logger.info(f"      Empresa: {result.job_data.company_name}")
                logger.info(f"      Urgency Score: {result.job_data.hiring_urgency_score}")
                logger.info(f"      IT Niche: {result.job_data.is_it_niche}")
            if result.error_message:
                logger.info(f"      Error: {result.error_message}")
        
        # Paso 7: Estadísticas de BD / Paŝo 7: Datumbazaj statistikoj
        logger.info("\n📊 Paso 7: Estadísticas de Base de Datos:")
        db_stats = db_manager.get_stats()
        for key, value in db_stats.items():
            logger.info(f"   {key}: {value}")
        
        logger.info("\n" + "="*80)
        logger.info("✅ TEST COMPLETADO EXITOSAMENTE")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n✗ ERROR EN TEST: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        # Paso 8: Limpieza / Paŝo 8: Purigado
        logger.info("\n🧹 Paso 8: Limpiando recursos...")
        await scraper.close()
        logger.info("✓ Recursos liberados")


async def test_database_only():
    """
    Test solo de base de datos sin scraping / Testo nur de datumbazo sen skrapado
    """
    logger.info("\n🧪 TEST DE BASE DE DATOS ÚNICAMENTE")
    logger.info("="*80)
    
    # Inicializar BD / Ekigi datumbazon
    init_db()
    
    # Health check / Sankontrolo
    health = db_manager.health_check()
    logger.info(f"Health Check: {'✓ OK' if health else '✗ FAIL'}")
    
    # Estadísticas / Statistikoj
    stats = db_manager.get_stats()
    logger.info(f"\nEstadísticas de BD:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n✓ Test de BD completado")


def main():
    """Función principal / Ĉefa funkcio"""
    print("\n" + "="*80)
    print("🔍 LABORTROVILO - TEST SUITE")
    print("   Senior Data Engineer Architecture")
    print("="*80)
    
    print("\nOpciones de test:")
    print("1. Test completo (BD + Scraping)")
    print("2. Test solo de Base de Datos")
    print("3. Salir")
    
    choice = input("\nSelecciona una opción (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_basic_scraping())
    elif choice == "2":
        asyncio.run(test_database_only())
    elif choice == "3":
        print("👋 Saliendo...")
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
