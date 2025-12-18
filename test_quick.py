"""
Test Rápido Automatizado para Labortrovilo
Rapida Aŭtomata Testo por Labortrovilo
Quick Automated Test for Labortrovilo

Este script ejecuta un test automatizado sin menús interactivos
"""
import asyncio
import logging
from datetime import datetime

from src.scraper_engine import LabortroviloScraper
from src.database import init_db, db_manager
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Test automatizado principal"""
    logger.info("="*80)
    logger.info("🧪 LABORTROVILO - TEST RÁPIDO AUTOMATIZADO")
    logger.info("="*80)
    
    # Inicializar BD
    logger.info("\n📊 Inicializando base de datos...")
    init_db()
    
    if db_manager.health_check():
        logger.info("✓ Base de datos OK")
    else:
        logger.error("✗ Problemas con la base de datos")
        return
    
    # Crear scraper
    logger.info("\n🤖 Creando instancia de LabortroviloScraper...")
    scraper = LabortroviloScraper(headless=False)  # headless=False para ver el navegador
    
    try:
        # Inicializar navegador
        logger.info("\n🌐 Inicializando navegador Playwright...")
        await scraper.initialize()
        
        # URLs de prueba - Work at a Startup (YCombinator)
        # Nota: Estas URLs son ejemplos. Para pruebas reales, visita:
        # https://www.workatastartup.com/companies y copia URLs reales
        logger.info("\n🔗 Preparando URLs de prueba...")
        test_urls = [
            # Página principal de YC Jobs - más genérica pero debería funcionar
            "https://www.ycombinator.com/companies",
            
            # O usa URLs de otros job boards populares:
            # "https://jobs.github.com/positions/12345",
            # "https://stackoverflow.com/jobs/12345",
        ]
        
        # Ejecutar scraping
        logger.info(f"\n🚀 Scrapeando {len(test_urls)} URL(s)...\n")
        results = await scraper.scrape_multiple_jobs(test_urls)
        
        # Analizar resultados
        logger.info("\n" + "="*80)
        logger.info("📈 RESULTADOS DEL TEST")
        logger.info("="*80)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"\n✓ Exitosos: {successful}/{len(results)}")
        logger.info(f"✗ Fallidos: {failed}/{len(results)}")
        
        # Mostrar detalles
        for i, result in enumerate(results, 1):
            logger.info(f"\n--- Resultado #{i} ---")
            logger.info(f"URL: {result.url}")
            logger.info(f"Status: {'✓ ÉXITO' if result.success else '✗ FALLO'}")
            
            if result.job_data:
                logger.info(f"\n📋 Datos Extraídos:")
                logger.info(f"   Título: {result.job_data.title}")
                logger.info(f"   Empresa: {result.job_data.company_name}")
                logger.info(f"   Ubicación: {result.job_data.location}")
                logger.info(f"   Remoto: {result.job_data.is_remote}")
                logger.info(f"   Platform: {result.job_data.source_platform}")
                logger.info(f"\n🎯 Campos Diferenciadores:")
                logger.info(f"   Urgency Score: {result.job_data.hiring_urgency_score:.1f}/100")
                logger.info(f"   IT Niche: {'SÍ' if result.job_data.is_it_niche else 'NO'}")
                
                if result.job_data.description:
                    desc_preview = result.job_data.description[:200]
                    logger.info(f"\n📝 Descripción (preview):\n   {desc_preview}...")
            
            if result.error_message:
                logger.info(f"\n❌ Error: {result.error_message}")
        
        # Estadísticas de BD
        logger.info("\n" + "="*80)
        logger.info("📊 ESTADÍSTICAS DE BASE DE DATOS")
        logger.info("="*80)
        db_stats = db_manager.get_stats()
        for key, value in db_stats.items():
            logger.info(f"   {key}: {value}")
        
        logger.info("\n" + "="*80)
        logger.info("✅ TEST COMPLETADO")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n✗ ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        logger.info("\n🧹 Limpiando recursos...")
        await scraper.close()
        logger.info("✓ Recursos liberados")


if __name__ == "__main__":
    asyncio.run(main())
