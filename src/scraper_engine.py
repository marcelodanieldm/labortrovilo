"""
Motor de Scraping Labortrovilo / Labortrovilo Skrapada Motoro
Senior Data Engineer Architecture - Scraping Engine with Error Handling & Logging
"""
import asyncio
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.database import get_db, db_manager
from src.models import Job, Company
from src.schemas import JobCreate, ScrapingResult, ScrapingStats, SourcePlatform
from config import settings

# Configurar logging robusto / Agordi robustan registradon / Configure robust logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LabortroviloScraper:
    """
    Motor principal de scraping con arquitectura profesional
    Ĉefa skrapada motoro kun profesia arkitekturo
    Main scraping engine with professional architecture
    
    Características / Trajtoj / Features:
    - Manejo robusto de errores / Robusta erartraktado / Robust error handling
    - Logging detallado / Detala registrado / Detailed logging
    - Validación con Pydantic / Validigo kun Pydantic / Pydantic validation
    - Prevención de duplicados / Malebligo de duobloj / Duplicate prevention
    - Detección inteligente de ATS / Inteligenta ATS-detekto / Smart ATS detection
    """
    
    def __init__(self, headless: bool = True):
        """
        Inicializa el scraper / Ekigas la skrapilon
        
        Args:
            headless: Ejecutar navegador sin interfaz gráfica
        """
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.headless = headless
        self.stats = ScrapingStats(start_time=datetime.utcnow())
        
        logger.info(f"🚀 Inicializando LabortroviloScraper (headless={headless})")
    
    async def initialize(self):
        """
        Inicializa el navegador Playwright con configuración optimizada
        Ekigas la Playwright retumilon kun optimigita agordado
        """
        try:
            logger.info("Iniciando Playwright...")
            playwright = await async_playwright().start()
            
            # Lanzar navegador con configuración / Lanĉi retumilon kun agordado
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Crear contexto con User-Agent real / Krei kuntekston kun reala User-Agent
            context = await self.browser.new_context(
                user_agent=settings.USER_AGENT,
                viewport={'width': 1920, 'height': 1080},
                locale='es-ES',
                timezone_id='America/New_York'
            )
            
            # Crear página / Krei paĝon
            self.page = await context.new_page()
            
            # Configurar timeout por defecto / Agordi defaŭltan tempo-limigon
            self.page.set_default_timeout(settings.PLAYWRIGHT_TIMEOUT)
            
            logger.info("✓ Navegador Playwright inicializado correctamente")
            
        except Exception as e:
            logger.error(f"✗ Error inicializando Playwright: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def close(self):
        """
        Cierra el navegador y limpia recursos
        Fermas la retumilon kaj purigas rimedojn
        """
        try:
            if self.browser:
                await self.browser.close()
                logger.info("✓ Navegador cerrado correctamente")
                
            # Calcular duración de la sesión / Kalkuli daŭron de la seanco
            self.stats.end_time = datetime.utcnow()
            self.stats.duration_seconds = (
                self.stats.end_time - self.stats.start_time
            ).total_seconds()
            
            # Log de estadísticas finales / Registri finajn statistikojn
            logger.info(f"📊 Estadísticas de scraping: {self.stats.model_dump()}")
            
        except Exception as e:
            logger.error(f"Error cerrando navegador: {e}")
    
    def _detect_source_platform(self, url: str) -> SourcePlatform:
        """
        Detecta la plataforma ATS basándose en la URL
        Detektas la ATS-platformon bazite sur la URL
        """
        domain = urlparse(url).netloc.lower()
        
        platform_mapping = {
            'greenhouse.io': SourcePlatform.GREENHOUSE,
            'lever.co': SourcePlatform.LEVER,
            'myworkdayjobs.com': SourcePlatform.WORKDAY,
            'smartrecruiters.com': SourcePlatform.SMARTRECRUITERS,
            'workable.com': SourcePlatform.WORKABLE,
            'bamboohr.com': SourcePlatform.BAMBOOHR,
            'jobvite.com': SourcePlatform.JOBVITE,
            'icims.com': SourcePlatform.ICIMS,
            'linkedin.com': SourcePlatform.LINKEDIN,
            'indeed.com': SourcePlatform.INDEED,
        }
        
        for key, platform in platform_mapping.items():
            if key in domain:
                return platform
        
        return SourcePlatform.CUSTOM
    
    def _calculate_hiring_urgency(self, job_data: dict) -> float:
        """
        Calcula score de urgencia de contratación basado en señales
        Kalkulas urĝeco-poentaron bazite sur signaloj
        
        Señales consideradas:
        - Palabras clave como "urgent", "immediate", "ASAP"
        - Fecha de publicación reciente
        - Múltiples posiciones abiertas
        """
        score = 50.0  # Score base / Baza poentaro
        
        description = (job_data.get('description', '') or '').lower()
        title = (job_data.get('title', '') or '').lower()
        
        # Palabras de urgencia / Urĝaj vortoj
        urgency_keywords = ['urgent', 'immediate', 'asap', 'urgente', 'inmediato']
        for keyword in urgency_keywords:
            if keyword in description or keyword in title:
                score += 15.0
                break
        
        # Fecha de publicación reciente / Freŝa publikigdata
        posted_date = job_data.get('posted_date')
        if posted_date:
            days_old = (datetime.utcnow() - posted_date).days
            if days_old < 3:
                score += 20.0
            elif days_old < 7:
                score += 10.0
        
        # Indicadores en el título / Indikatoroj en la titolo
        if 'senior' in title or 'lead' in title:
            score += 5.0
        
        return min(score, 100.0)  # Máximo 100 / Maksimume 100
    
    def _detect_it_niche(self, job_data: dict) -> bool:
        """
        Detecta si es un nicho especializado de IT
        Detektas ĉu ĝi estas specialigita IT-niĉo
        """
        text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        niche_keywords = [
            'blockchain', 'web3', 'crypto', 'quantum',
            'machine learning', 'deep learning', 'ai engineer',
            'computer vision', 'nlp', 'bioinformatics',
            'embedded systems', 'iot', 'edge computing',
            'game engine', 'graphics programming', 'shader'
        ]
        
        return any(keyword in text for keyword in niche_keywords)
    
    async def navigate_to_url(self, url: str) -> bool:
        """
        Navega a una URL con manejo de errores robusto
        Navigas al URL kun robusta erartraktado
        """
        try:
            logger.info(f"🌐 Navegando a: {url}")
            
            response = await self.page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=settings.PLAYWRIGHT_TIMEOUT
            )
            
            if response and response.ok:
                logger.info(f"✓ Navegación exitosa: {response.status}")
                return True
            else:
                status = response.status if response else 'Unknown'
                logger.warning(f"⚠️ Respuesta no OK: Status {status}")
                return False
                
        except PlaywrightTimeout:
            logger.error(f"✗ Timeout navegando a {url}")
            return False
        except Exception as e:
            logger.error(f"✗ Error navegando a {url}: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def extract_job_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de trabajo de la página actual con selectores genéricos
        Ekstraktas labordatumojn de la nuna paĝo kun ĝeneralaj elektiloj
        
        NOTA: Los selectores son genéricos y deben personalizarse por ATS
        """
        try:
            logger.info("📊 Extrayendo datos de la página...")
            
            # Esperar a que cargue el contenido / Atendi ke la enhavo ŝarĝiĝu
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Selectores mejorados para múltiples ATS / Plibonigitaj elektiloj por multaj ATS
            job_data = {}
            
            # Extraer título / Ekstraki titolon
            # Soporta: Work at a Startup, Greenhouse, Lever, Workday, genéricos
            try:
                title_selectors = [
                    'h1',  # Genérico
                    '.job-title',
                    '[data-qa="job-title"]',
                    '.app-title',  # Greenhouse
                    '.posting-headline',  # Lever
                    '[data-automation-id="jobPostingHeader"]',  # Workday
                    '.job-post-title',  # Work at a Startup
                ]
                title = None
                for selector in title_selectors:
                    try:
                        elem = await self.page.locator(selector).first.text_content(timeout=2000)
                        if elem and elem.strip():
                            title = elem.strip()
                            break
                    except:
                        continue
                
                job_data['title'] = title if title else "Unknown Position"
                if not title:
                    logger.warning("⚠️ No se pudo extraer el título")
            except:
                job_data['title'] = "Unknown Position"
                logger.warning("⚠️ Error extrayendo título")
            
            # Extraer empresa / Ekstraki kompanion
            try:
                company_selectors = [
                    '.company-name',
                    '[data-qa="company-name"]',
                    '.hiring-company',
                    '.company',  # Greenhouse
                    '.posting-categories-value',  # Lever
                    '[data-automation-id="jobPostingCompanyLocation"]',  # Workday
                    'a[href*="/companies/"]',  # Work at a Startup
                ]
                company = None
                for selector in company_selectors:
                    try:
                        elem = await self.page.locator(selector).first.text_content(timeout=2000)
                        if elem and elem.strip():
                            company = elem.strip()
                            break
                    except:
                        continue
                
                job_data['company_name'] = company if company else "Unknown Company"
                if not company:
                    logger.warning("⚠️ No se pudo extraer la empresa")
            except:
                job_data['company_name'] = "Unknown Company"
                logger.warning("⚠️ Error extrayendo empresa")
            
            # Extraer descripción / Ekstraki priskribon
            try:
                desc_selectors = [
                    '.description',
                    '.job-description',
                    'article',
                    '[data-qa="job-description"]',
                    '#content',  # Greenhouse
                    '.section-wrapper',  # Lever
                    '[data-automation-id="jobPostingDescription"]',  # Workday
                    '.job-post-content',  # Work at a Startup
                ]
                description = None
                for selector in desc_selectors:
                    try:
                        elem = await self.page.locator(selector).first.text_content(timeout=3000)
                        if elem and len(elem.strip()) > 100:  # Al menos 100 caracteres
                            description = elem.strip()
                            break
                    except:
                        continue
                
                job_data['description'] = description
                job_data['raw_description'] = description
                if not description:
                    logger.warning("⚠️ No se pudo extraer descripción completa")
            except:
                job_data['description'] = None
                job_data['raw_description'] = None
                logger.warning("⚠️ Error extrayendo descripción")
            
            # Extraer ubicación / Ekstraki lokon
            try:
                location_selectors = [
                    '.location',
                    '[data-qa="location"]',
                    '.job-location',
                    '.location-name',  # Greenhouse
                    '.posting-categories:has-text("Location")',  # Lever
                    '[data-automation-id="locations"]',  # Workday
                    '.job-post-location',  # Work at a Startup
                ]
                location = None
                for selector in location_selectors:
                    try:
                        elem = await self.page.locator(selector).first.text_content(timeout=2000)
                        if elem and elem.strip():
                            location = elem.strip()
                            break
                    except:
                        continue
                
                job_data['location'] = location
                if not location:
                    logger.warning("⚠️ No se pudo extraer ubicación")
            except:
                job_data['location'] = None
            
            # Detectar trabajo remoto / Detekti foran laboron
            location_text = (job_data.get('location') or '').lower()
            description_text = (job_data.get('description') or '').lower()
            job_data['is_remote'] = 'remote' in location_text or 'remoto' in location_text or 'remote' in description_text
            
            # Extraer salario si disponible / Ekstraki salajron se disponeblas
            try:
                salary = await self.page.locator('.salary, [data-qa="salary"], .compensation').first.text_content(timeout=5000)
                job_data['salary_range'] = salary.strip() if salary else None
            except:
                job_data['salary_range'] = None
            
            # Datos fijos y calculados / Fiksaj kaj kalkulitaj datumoj
            job_data['url'] = url
            job_data['source_platform'] = self._detect_source_platform(url).value
            job_data['posted_date'] = datetime.utcnow()  # Por defecto, fecha actual
            job_data['date_scraped'] = datetime.utcnow()
            
            # 🎯 CAMPOS DIFERENCIADORES / DISTINGAJ KAMPOJ
            job_data['hiring_urgency_score'] = self._calculate_hiring_urgency(job_data)
            job_data['is_it_niche'] = self._detect_it_niche(job_data)
            
            logger.info(f"✓ Datos extraídos: {job_data['title']} @ {job_data['company_name']}")
            logger.info(f"   📈 Urgency Score: {job_data['hiring_urgency_score']:.1f}")
            logger.info(f"   🎯 IT Niche: {job_data['is_it_niche']}")
            
            return job_data
            
        except Exception as e:
            logger.error(f"✗ Error extrayendo datos: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def save_to_db(self, job_data: Dict[str, Any]) -> bool:
        """
        Guarda datos validados en la base de datos con manejo robusto de errores
        Stokas validigitajn datumojn en la datumbazo kun robusta erartraktado
        """
        try:
            # Validar con Pydantic / Validigi kun Pydantic
            logger.info("✓ Validando datos con Pydantic...")
            validated_job = JobCreate(**job_data)
            
            with get_db() as db:
                # Verificar duplicados / Kontroli duoblojn
                existing = db.query(Job).filter(Job.url == validated_job.url).first()
                
                if existing:
                    logger.warning(f"⚠️ Trabajo duplicado encontrado: {validated_job.url}")
                    self.stats.duplicates_found += 1
                    return False
                
                # Obtener o crear empresa / Akiri aŭ krei kompanion
                company = db.query(Company).filter(
                    Company.name == validated_job.company_name
                ).first()
                
                if not company:
                    logger.info(f"📝 Creando nueva empresa: {validated_job.company_name}")
                    company = Company(
                        name=validated_job.company_name,
                        last_scraped_at=datetime.utcnow()
                    )
                    db.add(company)
                    db.flush()
                
                # Crear registro de trabajo / Krei laborregistron
                job = Job(
                    external_id=validated_job.external_id,
                    title=validated_job.title,
                    company_id=company.id,
                    company_name=validated_job.company_name,
                    description=validated_job.description,
                    raw_description=validated_job.raw_description,
                    stack=validated_job.stack,
                    required_skills=validated_job.required_skills,
                    nice_to_have_skills=validated_job.nice_to_have_skills,
                    salary_range=validated_job.salary_range,
                    salary_min=validated_job.salary_min,
                    salary_max=validated_job.salary_max,
                    salary_currency=validated_job.salary_currency,
                    location=validated_job.location,
                    is_remote=validated_job.is_remote,
                    remote_policy=validated_job.remote_policy,
                    country=validated_job.country,
                    city=validated_job.city,
                    url=validated_job.url,
                    source_platform=validated_job.source_platform,
                    hiring_urgency_score=validated_job.hiring_urgency_score,
                    is_it_niche=validated_job.is_it_niche,
                    posted_date=validated_job.posted_date,
                    is_active=validated_job.is_active,
                )
                
                db.add(job)
                db.commit()
                
                logger.info(f"✅ Trabajo guardado en BD: {job.title} (ID: {job.id})")
                self.stats.saved_to_db += 1
                return True
                
        except ValidationError as e:
            logger.error(f"✗ Error de validación Pydantic: {e}")
            logger.error(f"   Datos: {job_data}")
            return False
            
        except IntegrityError as e:
            logger.error(f"✗ Error de integridad (duplicado?): {e}")
            return False
            
        except SQLAlchemyError as e:
            logger.error(f"✗ Error de base de datos: {e}")
            logger.error(traceback.format_exc())
            return False
            
        except Exception as e:
            logger.error(f"✗ Error inesperado guardando en BD: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def scrape_job(self, url: str) -> ScrapingResult:
        """
        Método principal para scrapear una oferta de trabajo
        Ĉefa metodo por skrapi laboroferton
        
        Returns:
            ScrapingResult con el resultado de la operación
        """
        result = ScrapingResult(success=False, url=url)
        self.stats.total_urls += 1
        
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"🎯 Iniciando scraping: {url}")
            logger.info(f"{'='*80}")
            
            # Paso 1: Navegar / Paŝo 1: Navigi
            if not await self.navigate_to_url(url):
                result.error_message = "Failed to navigate to URL"
                self.stats.failed_scrapes += 1
                return result
            
            # Paso 2: Extraer datos / Paŝo 2: Ekstraki datumojn
            job_data = await self.extract_job_data(url)
            if not job_data:
                result.error_message = "Failed to extract job data"
                self.stats.failed_scrapes += 1
                return result
            
            # Paso 3: Guardar en BD / Paŝo 3: Stoki en datumbazon
            if self.save_to_db(job_data):
                result.success = True
                result.job_data = JobCreate(**job_data)
                self.stats.successful_scrapes += 1
                logger.info(f"✅ Scraping completado exitosamente")
            else:
                result.error_message = "Failed to save to database"
                self.stats.failed_scrapes += 1
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Error en scrape_job: {e}")
            logger.error(traceback.format_exc())
            result.error_message = str(e)
            self.stats.failed_scrapes += 1
            return result
    
    async def scrape_multiple_jobs(self, urls: List[str]) -> List[ScrapingResult]:
        """
        Scrapea múltiples URLs con manejo de errores individual
        Skrapas multajn URL-ojn kun individua erartraktado
        """
        results = []
        
        logger.info(f"📋 Iniciando scraping de {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\n🔄 Procesando {i}/{len(urls)}")
            
            try:
                result = await self.scrape_job(url)
                results.append(result)
                
                # Pequeña pausa entre requests / Malgranda paŭzo inter petoj
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"✗ Error procesando {url}: {e}")
                results.append(ScrapingResult(
                    success=False,
                    url=url,
                    error_message=str(e)
                ))
        
        # Resumen final / Fina resumo
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN DE SCRAPING:")
        logger.info(f"   Total URLs: {self.stats.total_urls}")
        logger.info(f"   Exitosos: {self.stats.successful_scrapes}")
        logger.info(f"   Fallidos: {self.stats.failed_scrapes}")
        logger.info(f"   Duplicados: {self.stats.duplicates_found}")
        logger.info(f"   Guardados en BD: {self.stats.saved_to_db}")
        logger.info(f"   Tasa de éxito: {self.stats.calculate_success_rate()}%")
        logger.info(f"{'='*80}\n")
        
        return results


# ============================================================
# FUNCIÓN MAIN PARA TEST / ĈEFA FUNKCIO POR TESTO
# ============================================================

async def main():
    """
    Función principal para ejecutar test básico del scraper
    Ĉefa funkcio por plenumi bazan teston de la skrapilo
    """
    logger.info("🚀 Iniciando Labortrovilo Scraper Engine - TEST MODE")
    
    # Inicializar base de datos / Ekigi datumbazon
    from src.database import init_db
    init_db()
    
    # Crear instancia del scraper / Krei ekzempleron de la skrapilo
    scraper = LabortroviloScraper(headless=True)
    
    try:
        # Inicializar navegador / Ekigi retumilon
        await scraper.initialize()
        
        # URLs de prueba (reemplazar con URLs reales)
        # Provaj URL-oj (anstataŭigi per realaj URL-oj)
        test_urls = [
            "https://boards.greenhouse.io/embed/job_app?token=example",
            # Agregar más URLs aquí / Aldoni pli da URL-oj ĉi tie
        ]
        
        logger.warning("⚠️ NOTA: Usar URLs reales de ATS para pruebas reales")
        logger.warning("⚠️ Los selectores genéricos deben personalizarse por ATS")
        
        # Scrapear trabajos / Skrapi laborojn
        results = await scraper.scrape_multiple_jobs(test_urls)
        
        # Mostrar estadísticas de BD / Montri datumbazajn statistikojn
        db_stats = db_manager.get_stats()
        logger.info(f"\n📊 Estadísticas de Base de Datos:")
        logger.info(f"   {db_stats}")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
