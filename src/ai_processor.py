"""
Módulo de Procesamiento con IA para Labortrovilo
AI-Traktada Modulo por Labortrovilo
AI Processing Module for Labortrovilo

Senior AI Engineer Architecture
Procesa descripciones de trabajo con LLMs (OpenAI/Claude) para extraer información estructurada
"""
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from src.models import Job
from src.database import get_db
from config import settings

# Configurar logging / Agordi registradon / Configure logging
logger = logging.getLogger(__name__)


class AIJobProcessor:
    """
    Procesador de ofertas de trabajo con IA
    AI-bazita laboroferta traktilo
    AI-powered job offer processor
    
    Características / Trajtoj / Features:
    - Extracción estructurada con LLMs
    - Sistema de caché para optimizar costos
    - Soporte para OpenAI y Claude/Anthropic
    - Análisis de red flags
    """
    
    def __init__(
        self, 
        provider: str = "openai",
        model: str = None,
        api_key: str = None
    ):
        """
        Inicializa el procesador de IA
        Ekigas la AI-traktilon
        Initializes the AI processor
        
        Args:
            provider: "openai" o "anthropic"
            model: Modelo específico (ej: "gpt-4", "claude-3-opus")
            api_key: API key (si no está en .env)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        
        # Seleccionar modelo / Elekti modelon / Select model
        if model:
            self.model = model
        elif self.provider == "openai":
            self.model = "gpt-4o-mini"  # Más económico que gpt-4
        elif self.provider == "anthropic":
            self.model = "claude-3-haiku-20240307"  # Más económico que opus
        else:
            raise ValueError(f"Provider no soportado: {provider}")
        
        # Inicializar cliente / Ekigi klienton / Initialize client
        self._init_client()
        
        # Sistema de caché / Kaŝmemora sistemo / Cache system
        self.cache_file = Path("cache_ai_processing.json")
        self.cache = self._load_cache()
        
        logger.info(f"🤖 AIJobProcessor inicializado: {self.provider} / {self.model}")
    
    def _get_api_key(self) -> str:
        """Obtiene la API key desde configuración"""
        if self.provider == "openai":
            key = getattr(settings, 'OPENAI_API_KEY', None)
            if not key:
                raise ValueError(
                    "OPENAI_API_KEY no configurada. "
                    "Agrégala a tu archivo .env: OPENAI_API_KEY=sk-..."
                )
            return key
        elif self.provider == "anthropic":
            key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not key:
                raise ValueError(
                    "ANTHROPIC_API_KEY no configurada. "
                    "Agrégala a tu archivo .env: ANTHROPIC_API_KEY=sk-ant-..."
                )
            return key
        else:
            raise ValueError(f"Provider desconocido: {self.provider}")
    
    def _init_client(self):
        """Inicializa el cliente de IA"""
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI no instalado. Ejecuta: pip install openai"
                )
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✓ Cliente OpenAI inicializado")
            
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError(
                    "Anthropic no instalado. Ejecuta: pip install anthropic"
                )
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("✓ Cliente Anthropic inicializado")
    
    def _load_cache(self) -> Dict[str, Dict]:
        """
        Carga el caché desde disco
        Ŝargas kaŝmemoron de disko
        Loads cache from disk
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                logger.info(f"✓ Caché cargado: {len(cache)} entradas")
                return cache
            except Exception as e:
                logger.warning(f"⚠️ Error cargando caché: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Guarda el caché en disco"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Caché guardado: {len(self.cache)} entradas")
        except Exception as e:
            logger.error(f"✗ Error guardando caché: {e}")
    
    def _compute_hash(self, text: str) -> str:
        """
        Calcula hash SHA256 de un texto
        Kalkulas SHA256-haŝon de teksto
        Computes SHA256 hash of text
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _build_system_prompt(self) -> str:
        """
        Construye el prompt del sistema para la IA
        Konstruas la sisteman instigon por la AI
        Builds the system prompt for the AI
        """
        return """Eres un AI Engineer experto en análisis de ofertas de trabajo tecnológicas.

Tu tarea es analizar descripciones de ofertas de empleo y extraer información estructurada en formato JSON.

IMPORTANTE: Tu respuesta DEBE ser ÚNICAMENTE un objeto JSON válido, sin texto adicional antes o después.

Estructura JSON requerida:
{
  "tech_stack": ["lista", "de", "tecnologías"],
  "seniority_level": "uno de: Intern, Junior, Mid, Senior, Lead, C-Level",
  "is_remote": true o false,
  "salary_estimate": "rango estimado si no está explícito, ej: '$80k-$120k USD'",
  "hiring_intent": "growth o replacement",
  "red_flags": ["lista", "de", "problemas", "potenciales"]
}

GUÍA DE EXTRACCIÓN:

1. tech_stack: 
   - Lista limpia de lenguajes, frameworks, herramientas
   - Normaliza nombres (ej: "ReactJS" → "React", "postgresql" → "PostgreSQL")
   - Solo tecnologías explícitamente mencionadas

2. seniority_level:
   - Intern: prácticas, becario, trainee
   - Junior: 0-2 años experiencia, junior
   - Mid: 2-5 años, mid-level, "solid experience"
   - Senior: 5+ años, senior, "extensive experience"
   - Lead: tech lead, staff engineer, principal
   - C-Level: CTO, VP Engineering, Director

3. is_remote:
   - true si menciona: remote, remoto, work from home, anywhere
   - false si especifica ubicación física obligatoria

4. salary_estimate:
   - Si hay rango explícito, úsalo
   - Si no, estima basándote en:
     * Seniority level
     * Ubicación (si se menciona)
     * Stack tecnológico (tecnologías premium pagan más)
   - Formato: "$80k-$120k USD" o "€60k-€90k EUR"

5. hiring_intent:
   - "growth": expansión, scaling, new team, new project
   - "replacement": backfill, replacing, maintaining current team

6. red_flags:
   - "Demasiadas tecnologías no relacionadas" (ej: pide Java, Python, Ruby, Go)
   - "Horarios poco claros" (ej: "flexibilidad" sin detalles)
   - "Salario muy bajo para el nivel" 
   - "Requisitos irreales" (ej: 10 años exp en tech de 3 años)
   - "Cultura tóxica" (ej: "work hard, play hard", "ninjas")
   - "Descripción vaga" (muy corta o sin detalles técnicos)

Responde SOLO con el objeto JSON, sin markdown, sin explicaciones."""

    def _build_user_prompt(self, job_data: Dict[str, Any]) -> str:
        """Construye el prompt del usuario con los datos del trabajo"""
        title = job_data.get('title', 'Unknown')
        company = job_data.get('company_name', 'Unknown')
        location = job_data.get('location', 'Unknown')
        description = job_data.get('description', '')
        
        # Truncar descripción si es muy larga (para ahorrar tokens)
        if len(description) > 4000:
            description = description[:4000] + "..."
        
        return f"""Analiza esta oferta de trabajo:

TÍTULO: {title}
EMPRESA: {company}
UBICACIÓN: {location}

DESCRIPCIÓN:
{description}

Responde ÚNICAMENTE con el objeto JSON estructurado."""

    def process_description(
        self, 
        job_data: Dict[str, Any],
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Procesa una descripción de trabajo con IA
        Traktas labopriskribon per AI
        Processes job description with AI
        
        Args:
            job_data: Diccionario con datos del trabajo (debe incluir 'description')
            use_cache: Si True, usa caché para evitar llamadas duplicadas
            
        Returns:
            Diccionario con campos procesados o None si falla
        """
        description = job_data.get('description', '')
        if not description or len(description.strip()) < 50:
            logger.warning("⚠️ Descripción muy corta o vacía, saltando procesamiento IA")
            return None
        
        # Verificar caché / Kontroli kaŝmemoron / Check cache
        desc_hash = self._compute_hash(description)
        
        if use_cache and desc_hash in self.cache:
            logger.info(f"✓ Datos encontrados en caché (hash: {desc_hash[:8]}...)")
            return self.cache[desc_hash]
        
        # Llamar a la IA / Voki la AI / Call the AI
        logger.info(f"🤖 Procesando con {self.provider}/{self.model}...")
        
        try:
            if self.provider == "openai":
                result = self._call_openai(job_data)
            elif self.provider == "anthropic":
                result = self._call_anthropic(job_data)
            else:
                logger.error(f"✗ Provider no soportado: {self.provider}")
                return None
            
            # Guardar en caché / Konservi en kaŝmemoron / Save to cache
            if result and use_cache:
                self.cache[desc_hash] = result
                self._save_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Error procesando con IA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _call_openai(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Llama a la API de OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(job_data)}
                ],
                temperature=0.1,  # Baja temperatura para respuestas consistentes
                response_format={"type": "json_object"}  # Forzar JSON
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info("✓ Respuesta de OpenAI recibida y parseada")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"✗ Error parseando JSON de OpenAI: {e}")
            logger.error(f"Contenido recibido: {content}")
            return None
        except Exception as e:
            logger.error(f"✗ Error llamando a OpenAI: {e}")
            return None
    
    def _call_anthropic(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Llama a la API de Anthropic (Claude)"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._build_system_prompt(),
                messages=[
                    {"role": "user", "content": self._build_user_prompt(job_data)}
                ],
                temperature=0.1
            )
            
            content = message.content[0].text
            
            # Claude a veces envuelve en ```json, limpiarlo
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            
            logger.info("✓ Respuesta de Claude recibida y parseada")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"✗ Error parseando JSON de Claude: {e}")
            logger.error(f"Contenido recibido: {content}")
            return None
        except Exception as e:
            logger.error(f"✗ Error llamando a Claude: {e}")
            return None
    
    def enrich_job_data(
        self, 
        job_id: int = None,
        limit: int = 10,
        force_reprocess: bool = False
    ) -> Dict[str, int]:
        """
        Enriquece trabajos en la BD con datos procesados por IA
        Pliriĉigas laborojn en la datumbazo per AI-traktitaj datumoj
        Enriches jobs in DB with AI-processed data
        
        Args:
            job_id: ID específico de trabajo (si None, procesa múltiples)
            limit: Cantidad máxima de trabajos a procesar
            force_reprocess: Si True, reprocesa incluso si ya fue procesado
            
        Returns:
            Diccionario con estadísticas: {processed, failed, skipped}
        """
        stats = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'cached': 0
        }
        
        logger.info("="*80)
        logger.info("🚀 INICIANDO ENRIQUECIMIENTO CON IA")
        logger.info("="*80)
        
        with get_db() as db:
            # Construir query / Konstrui peton / Build query
            if job_id:
                jobs = db.query(Job).filter(Job.id == job_id).all()
            else:
                # Trabajos no procesados o a reprocesar
                if force_reprocess:
                    jobs = db.query(Job).limit(limit).all()
                else:
                    jobs = db.query(Job).filter(
                        and_(
                            Job.ai_processed == False,
                            Job.description.isnot(None)
                        )
                    ).limit(limit).all()
            
            total_jobs = len(jobs)
            logger.info(f"📊 Trabajos a procesar: {total_jobs}")
            
            if total_jobs == 0:
                logger.info("✓ No hay trabajos pendientes de procesar")
                return stats
            
            # Procesar cada trabajo / Trakti ĉiun laboron / Process each job
            for i, job in enumerate(jobs, 1):
                logger.info(f"\n🔄 Procesando {i}/{total_jobs}: {job.title}")
                
                # Verificar si ya está en caché por hash
                desc_hash = self._compute_hash(job.description or "")
                cached = desc_hash in self.cache
                
                if cached:
                    logger.info(f"   ⚡ Usando datos cacheados")
                    stats['cached'] += 1
                
                # Procesar con IA
                ai_result = self.process_description({
                    'title': job.title,
                    'company_name': job.company_name,
                    'location': job.location,
                    'description': job.description
                })
                
                if not ai_result:
                    logger.warning(f"   ✗ Fallo al procesar")
                    stats['failed'] += 1
                    continue
                
                # Actualizar el trabajo con los datos de IA
                try:
                    # Tech stack (como JSON string)
                    if 'tech_stack' in ai_result:
                        job.stack = json.dumps(ai_result['tech_stack'])
                    
                    # Seniority level
                    if 'seniority_level' in ai_result:
                        job.seniority_level = ai_result['seniority_level']
                    
                    # Remote
                    if 'is_remote' in ai_result:
                        job.is_remote = ai_result['is_remote']
                    
                    # Salary estimate
                    if 'salary_estimate' in ai_result:
                        job.salary_estimate = ai_result['salary_estimate']
                    
                    # Hiring intent
                    if 'hiring_intent' in ai_result:
                        job.hiring_intent = ai_result['hiring_intent']
                    
                    # Red flags (como JSON string)
                    if 'red_flags' in ai_result:
                        job.red_flags = json.dumps(ai_result['red_flags'])
                    
                    # Metadatos de procesamiento
                    job.ai_processed = True
                    job.ai_processed_at = datetime.utcnow()
                    job.description_hash = desc_hash
                    
                    db.commit()
                    
                    logger.info(f"   ✓ Trabajo actualizado")
                    logger.info(f"      Seniority: {job.seniority_level}")
                    logger.info(f"      Stack: {len(ai_result.get('tech_stack', []))} techs")
                    logger.info(f"      Red Flags: {len(ai_result.get('red_flags', []))}")
                    
                    stats['processed'] += 1
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"   ✗ Error actualizando BD: {e}")
                    stats['failed'] += 1
        
        # Resumen final
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMEN DE PROCESAMIENTO")
        logger.info("="*80)
        logger.info(f"✓ Procesados: {stats['processed']}")
        logger.info(f"⚡ Desde caché: {stats['cached']}")
        logger.info(f"✗ Fallidos: {stats['failed']}")
        logger.info(f"⏭️  Saltados: {stats['skipped']}")
        logger.info("="*80)
        
        return stats


def get_ai_processor(provider: str = "openai") -> AIJobProcessor:
    """
    Factory function para obtener un procesador de IA
    Fabrika funkcio por akiri AI-traktilon
    Factory function to get an AI processor
    """
    return AIJobProcessor(provider=provider)


# Ejemplo de uso / Ekzemplo de uzo / Usage example
if __name__ == "__main__":
    # Configurar logging para test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🤖 AI Processor Module - Test Mode")
    print("="*80)
    print("\nPara usar este módulo:")
    print("1. Configura OPENAI_API_KEY o ANTHROPIC_API_KEY en tu .env")
    print("2. Importa: from src.ai_processor import get_ai_processor")
    print("3. Usa: processor = get_ai_processor()")
    print("4. Ejecuta: processor.enrich_job_data(limit=10)")
    print("\nVer: test_ai_processor.py para ejemplos completos")
