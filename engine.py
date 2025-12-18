"""
Motor de Scraping de Labortrovilo / Skrapada Motoro de Labortrovilo
Script principal para web scraping con Playwright y operaciones de base de datos
\u0108efa skripto por retpaĝa skrapado kun Playwright kaj datumbazaj operacioj
"""
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from database import get_db, init_db
from models import Job, Company
from schemas import JobCreateSchema, CompanyCreateSchema
from config import settings


class ScrapingEngine:
    """
    Motor principal de scraping usando Playwright / \u0108efa skrapada motoro uzante Playwright
    Maneja navegaci\u00f3n, extracci\u00f3n y operaciones de base de datos
    Administras navigadon, ekstraktadon kaj datumbazajn operaciojn
    """
    
    def __init__(self):
        # Navegador de Playwright / Playwright retumilo
        self.browser: Optional[Browser] = None
        # P\u00e1gina actual / Nuna pa\u011do
        self.page: Optional[Page] = None
    
    async def initialize(self):
        """Inicializa el navegador Playwright / Ekigas la Playwright retumilon"""
        # Iniciar Playwright / Starti Playwright
        playwright = await async_playwright().start()
        # Lanzar navegador Chromium / Lanĉi Chromium retumilon
        self.browser = await playwright.chromium.launch(
            headless=settings.PLAYWRIGHT_HEADLESS
        )
        # Crear nueva página / Krei novan paĝon
        self.page = await self.browser.new_page()
        # Configurar User-Agent / Agordi User-Agent
        await self.page.set_extra_http_headers({
            'User-Agent': settings.USER_AGENT
        })
        print("✓ Browser initialized")
    
    async def close(self):
        """Cierra el navegador y limpia recursos / Fermas la retumilon kaj purigas rimedojn"""
        if self.browser:
            # Cerrar navegador / Fermi retumilon
            await self.browser.close()
            print("✓ Browser closed")
    
    async def navigate_to_url(self, url: str) -> bool:
        """
        Navega a una URL / Navigi al URL
        Retorna True si tiene éxito, False en caso contrario / Resendas True se sukcesas, False alie
        """
        try:
            # Navegar a la URL con timeout / Navigi al la URL kun tempo-limigo
            response = await self.page.goto(url, timeout=settings.PLAYWRIGHT_TIMEOUT)
            if response and response.ok:
                print(f"✓ Successfully navigated to {url}")
                return True
            else:
                print(f"✗ Failed to navigate to {url}: Status {response.status if response else 'None'}")
                return False
        except Exception as e:
            print(f"✗ Error navigating to {url}: {e}")
            return False
    
    async def extract_job_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de trabajo de la página actual / Ekstraktas labordatumojn de la nuna paĝo
        Este es un método plantilla - personalizar según la estructura del sitio objetivo
        Ĉi tio estas ŝablona metodo - personecigi laŭ la strukturo de la cela retejo
        """
        try:
            # Esperar a que el contenido cargue / Atendi ke la enhavo ŝarĝiĝu
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Ejemplo de extracción - PERSONALIZAR según el sitio objetivo / Ekzemplo de ekstraktado - PERSONECIGI laŭ la cela retejo
            # Extraer título / Ekstraki titolon
            title = await self.page.locator('h1').first.text_content() or "Unknown Title"
            
            # Intentar extraer nombre de empresa / Provi ekstraki kompanian nomon
            company_name = await self.page.locator('.company-name, [data-company-name]').first.text_content() or "Unknown Company"
            
            # Extraer descripción / Ekstraki priskribon
            description_element = self.page.locator('.description, .job-description, article')
            raw_description = await description_element.first.text_content() if await description_element.count() > 0 else ""
            
            # Extraer salario si está disponible / Ekstraki salajron se disponeblas
            salary_text = await self.page.locator('.salary, [data-salary]').first.text_content() if await self.page.locator('.salary, [data-salary]').count() > 0 else ""
            
            # Crear diccionario con datos extraídos / Krei vortaron kun ekstraktitaj datumoj
            job_data = {
                'title': title.strip(),
                'company_name': company_name.strip(),
                'raw_description': raw_description.strip() if raw_description else None,
                'cleaned_stack': None,  # Para procesar después / Por procezi poste
                'salary_min': None,  # Parsear de salary_text / Analizi el salary_text
                'salary_max': None,  # Parsear de salary_text / Analizi el salary_text
                'source_url': url,
                'posted_date': datetime.utcnow()  # O parsear de la página / Aŭ analizi el la paĝo
            }
            
            print(f"✓ Extracted data from {url}")
            return job_data
            
        except Exception as e:
            print(f"✗ Error extracting data from {url}: {e}")
            return None
    
    def validate_and_save_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Valida datos de trabajo con Pydantic y guarda en base de datos / Validigas labordatumojn kun Pydantic kaj stokas en datumbazo
        Retorna True si se guarda exitosamente, False en caso contrario / Resendas True se stokas sukcese, False alie
        """
        try:
            # Validar con Pydantic / Validigi kun Pydantic
            validated_job = JobCreateSchema(**job_data)
            
            with get_db() as db:
                # Verificar si la URL ya existe (prevención de duplicados) / Kontroli ĉu la URL jam ekzistas (malebligo de duobloj)
                existing_job = db.query(Job).filter(Job.source_url == validated_job.source_url).first()
                
                if existing_job:
                    print(f"⚠ Job already exists in database: {validated_job.source_url}")
                    return False
                
                # Obtener o crear empresa / Akiri aŭ krei kompanion
                company = db.query(Company).filter(Company.name == validated_job.company_name).first()
                if not company:
                    company = Company(
                        name=validated_job.company_name,
                        growth_score=None,
                        industry=None
                    )
                    db.add(company)
                    db.flush()  # Obtener el ID de la empresa / Akiri la ID de la kompanio
                
                # Crear registro de trabajo / Krei laborregistron
                job = Job(
                    title=validated_job.title,
                    company_id=company.id,
                    company_name=validated_job.company_name,
                    raw_description=validated_job.raw_description,
                    cleaned_stack=validated_job.cleaned_stack,
                    salary_min=validated_job.salary_min,
                    salary_max=validated_job.salary_max,
                    source_url=validated_job.source_url,
                    posted_date=validated_job.posted_date
                )
                
                # Añadir a base de datos y confirmar / Aldoni al datumbazo kaj konfirmi
                db.add(job)
                db.commit()
                
                print(f"✓ Job saved to database: {job.title} at {job.company_name}")
                return True
                
        except ValidationError as e:
            print(f"✗ Validation error: {e}")
            return False
        except IntegrityError as e:
            print(f"✗ Database integrity error (duplicate URL?): {e}")
            return False
        except Exception as e:
            print(f"✗ Error saving job to database: {e}")
            return False
    
    async def scrape_job(self, url: str) -> bool:
        """
        Método principal para scrapear una oferta de trabajo / Ĉefa metodo por skrapi laboroferton
        Navega, extrae, valida y guarda / Navigas, ekstraktas, validigas kaj stokas
        """
        print(f"\n{'='*60}")
        print(f"Starting scrape for: {url}")
        print(f"{'='*60}")
        
        # Navegar a la URL / Navigi al la URL
        if not await self.navigate_to_url(url):
            return False
        
        # Extraer datos / Ekstraki datumojn
        job_data = await self.extract_job_data(url)
        if not job_data:
            return False
        
        # Validar y guardar / Validigi kaj stoki
        return self.validate_and_save_job(job_data)


async def main():
    """
    Punto de entrada principal para el motor de scraping / Ĉefa enira punkto por la skrapada motoro
    """
    # Inicializar base de datos / Ekigi datumbazon
    print("Initializing database...")
    init_db()
    
    # Crear motor de scraping / Krei skrapadan motoron
    engine = ScrapingEngine()
    
    try:
        # Inicializar navegador / Ekigi retumilon
        await engine.initialize()
        
        # Ejemplo de uso - scrapear una oferta de trabajo / Ekzemplo de uzo - skrapi laboroferton
        # REEMPLAZAR CON URL REAL DE OFERTA DE TRABAJO / ANSTATAŬIGI PER REALA URL DE LABOROFERTO
        test_url = "https://example.com/jobs/sample-job-posting"
        
        # Ejecutar scraping / Plenumi skrapadon
        result = await engine.scrape_job(test_url)
        
        if result:
            print("\n✓ Scraping completed successfully!")
        else:
            print("\n✗ Scraping failed or job already exists")
        
    finally:
        # Siempre cerrar el navegador / Ĉiam fermi la retumilon
        await engine.close()


if __name__ == "__main__":
    # Ejecutar la función principal asíncrona / Plenumi la ĉefan nesinkronan funkcion
    asyncio.run(main())
