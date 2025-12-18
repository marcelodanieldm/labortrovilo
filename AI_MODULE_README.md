# 🤖 Módulo de Inteligencia Artificial - Labortrovilo

## 📋 Descripción

El módulo de IA de Labortrovilo procesa descripciones de trabajos extraídas mediante web scraping y las enriquece con información estructurada usando **Large Language Models (LLMs)**.

### 🎯 Arquitectura: Senior AI Engineer

**Versión:** 2.1.0  
**Autor:** Daniel - Senior AI Engineer

---

## 🚀 Características Principales

### ✅ Extracción Estructurada con IA

El módulo procesa descripciones brutas y extrae:

1. **`tech_stack`** - Lista limpia de tecnologías
   - Ejemplo: `['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker']`
   - Normalización automática de nombres

2. **`seniority_level`** - Clasificación de nivel
   - Valores: `Intern`, `Junior`, `Mid`, `Senior`, `Lead`, `C-Level`
   - Basado en años de experiencia y palabras clave

3. **`is_remote`** - Trabajo remoto (Boolean)
   - Detecta: "remote", "work from home", "anywhere"
   - Actualiza el campo existente en la BD

4. **`salary_estimate`** - Estimación salarial
   - Si está explícito, lo extrae
   - Si no, estima basándose en: seniority + ubicación + stack
   - Formato: `"$80k-$120k USD"` o `"€60k-€90k EUR"`

5. **`hiring_intent`** - Intención de contratación
   - `"growth"`: Expansión del equipo, nuevo proyecto
   - `"replacement"`: Reemplazo de alguien que se fue

6. **`red_flags`** - ⚠️ Problemas potenciales (Lista)
   - "Demasiadas tecnologías no relacionadas"
   - "Horarios poco claros"
   - "Salario muy bajo para el nivel"
   - "Requisitos irreales"
   - "Cultura tóxica" (ej: "ninjas", "rockstars")
   - "Descripción vaga"

---

## 🔧 Instalación

### Paso 1: Instalar dependencias

```bash
pip install openai anthropic
```

O actualiza desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Paso 2: Configurar API Keys

Edita tu archivo `.env`:

```env
# OpenAI (recomendado)
OPENAI_API_KEY=sk-proj-your-key-here

# O Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Configuración
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
AI_CACHE_ENABLED=true
```

**¿Dónde obtener las API keys?**

- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/

### Paso 3: Actualizar la base de datos

El módulo de IA agrega nuevos campos a la tabla `jobs`. Necesitas actualizar tu BD:

```bash
# Opción 1: Recrear la BD (PERDERÁS DATOS)
rm labortrovilo.db
python -c "from src.database import init_db; init_db()"

# Opción 2: Usar Alembic para migraciones (recomendado para producción)
alembic revision --autogenerate -m "Add AI fields"
alembic upgrade head
```

---

## 💻 Uso

### Opción 1: Script Interactivo (RECOMENDADO)

```bash
python test_ai_processor.py
```

Menú con opciones:
1. Crear trabajos de ejemplo
2. Test de procesamiento individual
3. Test de procesamiento en lote
4. Test de sistema de caché
5. Ver trabajos procesados
6. Salir

### Opción 2: Uso Programático

```python
from src.ai_processor import get_ai_processor
from src.database import init_db

# Inicializar BD
init_db()

# Crear procesador
processor = get_ai_processor(provider="openai")

# Opción A: Enriquecer todos los trabajos no procesados
stats = processor.enrich_job_data(limit=10)
print(f"Procesados: {stats['processed']}")

# Opción B: Procesar un trabajo específico
stats = processor.enrich_job_data(job_id=1)

# Opción C: Forzar reprocesamiento
stats = processor.enrich_job_data(limit=5, force_reprocess=True)
```

### Opción 3: Procesamiento Individual

```python
from src.ai_processor import get_ai_processor

processor = get_ai_processor()

job_data = {
    'title': 'Senior Backend Engineer',
    'company_name': 'TechCorp',
    'location': 'San Francisco, CA',
    'description': '''
    We're looking for a Senior Backend Engineer with 5+ years experience.
    Requirements: Python, Django, PostgreSQL, AWS, Docker.
    Salary: $120k-$160k. Remote OK.
    '''
}

result = processor.process_description(job_data)

print(result)
# Output:
# {
#   "tech_stack": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
#   "seniority_level": "Senior",
#   "is_remote": true,
#   "salary_estimate": "$120k-$160k USD",
#   "hiring_intent": "growth",
#   "red_flags": []
# }
```

---

## 🎯 Sistema de Caché

### ¿Por qué es importante?

Cada llamada a la API de OpenAI/Claude tiene un costo en tokens. El sistema de caché **evita procesar descripciones idénticas múltiples veces**.

### ¿Cómo funciona?

1. Calcula un **hash SHA256** de la descripción
2. Busca el hash en `cache_ai_processing.json`
3. Si existe → **usa el resultado cacheado** (gratis!)
4. Si no existe → llama a la API y guarda el resultado

### Estadísticas de caché

```python
stats = processor.enrich_job_data(limit=100)

print(f"Procesados: {stats['processed']}")
print(f"Desde caché: {stats['cached']}")  # ¡Ahorros!
print(f"Fallidos: {stats['failed']}")
```

### Gestión del caché

```python
# Ver tamaño del caché
import json
with open('cache_ai_processing.json') as f:
    cache = json.load(f)
    print(f"Entradas en caché: {len(cache)}")

# Limpiar caché (si necesitas reprocesar todo)
import os
os.remove('cache_ai_processing.json')
```

---

## 💰 Optimización de Costos

### Modelos Recomendados

| Provider | Modelo | Costo (aprox) | Velocidad | Calidad |
|----------|--------|---------------|-----------|---------|
| OpenAI | `gpt-4o-mini` | $0.15/1M tokens | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| OpenAI | `gpt-4o` | $2.50/1M tokens | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| Anthropic | `claude-3-haiku` | $0.25/1M tokens | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| Anthropic | `claude-3-sonnet` | $3.00/1M tokens | ⚡⚡ | ⭐⭐⭐⭐⭐ |

**Recomendación:** Usa `gpt-4o-mini` para producción (excelente balance costo/calidad)

### Tips para Ahorrar

1. **Usa el caché** - Activa `AI_CACHE_ENABLED=true`
2. **Trunca descripciones largas** - El código trunca a 4000 chars automáticamente
3. **Procesa en lotes pequeños** - Empieza con `limit=10` para testing
4. **Temperature baja** - Usa `temperature=0.1` para respuestas consistentes
5. **Evita reprocesar** - Filtra `WHERE ai_processed = False`

### Estimación de Costos

Ejemplo con **gpt-4o-mini** ($0.15/1M tokens):

- **Descripción promedio:** 500 tokens
- **Respuesta JSON:** 200 tokens
- **Total por trabajo:** ~700 tokens
- **Costo por trabajo:** $0.000105 (≈ $0.0001)

**1,000 trabajos = ~$0.10 USD** 💰

---

## 📊 Campos en la Base de Datos

Nuevos campos agregados a la tabla `jobs`:

```sql
-- Procesados por IA
seniority_level VARCHAR(50),          -- Intern, Junior, Mid, Senior, Lead, C-Level
salary_estimate VARCHAR(100),         -- Estimación si no está explícita
hiring_intent VARCHAR(50),            -- growth o replacement
red_flags TEXT,                       -- JSON array de problemas
ai_processed BOOLEAN DEFAULT FALSE,   -- ¿Ya procesado?
ai_processed_at DATETIME,             -- Timestamp de procesamiento
description_hash VARCHAR(64)          -- SHA256 para caché
```

### Consultas SQL Útiles

```sql
-- Trabajos procesados por IA
SELECT * FROM jobs WHERE ai_processed = TRUE;

-- Trabajos con red flags
SELECT title, company_name, red_flags 
FROM jobs 
WHERE red_flags IS NOT NULL AND red_flags != '[]';

-- Distribución por seniority
SELECT seniority_level, COUNT(*) as count 
FROM jobs 
GROUP BY seniority_level;

-- Trabajos por intención de contratación
SELECT hiring_intent, COUNT(*) as count 
FROM jobs 
GROUP BY hiring_intent;
```

---

## 🔍 Ejemplo Completo: Flujo End-to-End

```python
"""
Flujo completo: Scraping → IA → Análisis
"""
import asyncio
from src.scraper_engine import LabortroviloScraper
from src.ai_processor import get_ai_processor
from src.database import init_db, get_db
from src.models import Job

async def main():
    # 1. Inicializar BD
    init_db()
    
    # 2. Scrapear trabajos
    scraper = LabortroviloScraper(headless=True)
    await scraper.initialize()
    
    urls = [
        "https://www.workatastartup.com/jobs/70123",
        "https://boards.greenhouse.io/company/jobs/123456",
    ]
    
    results = await scraper.scrape_multiple_jobs(urls)
    await scraper.close()
    
    print(f"✓ Scrapeados: {sum(1 for r in results if r.success)} trabajos")
    
    # 3. Procesar con IA
    processor = get_ai_processor(provider="openai")
    stats = processor.enrich_job_data(limit=10)
    
    print(f"✓ Procesados con IA: {stats['processed']} trabajos")
    print(f"⚡ Desde caché: {stats['cached']}")
    
    # 4. Análizar resultados
    with get_db() as db:
        # Trabajos Senior con red flags
        senior_with_flags = db.query(Job).filter(
            Job.seniority_level == "Senior",
            Job.red_flags.isnot(None)
        ).all()
        
        print(f"\n⚠️ Trabajos Senior con Red Flags: {len(senior_with_flags)}")
        
        for job in senior_with_flags:
            print(f"\n{job.title} @ {job.company_name}")
            print(f"Flags: {job.red_flags}")

asyncio.run(main())
```

---

## 🧪 Testing

### Tests Disponibles

```bash
# Test completo con menú interactivo
python test_ai_processor.py

# O ejecuta tests individuales programáticamente
python -c "from test_ai_processor import test_single_job_processing; test_single_job_processing()"
```

### Crear Datos de Prueba

El script de test incluye función para crear trabajos de ejemplo:

```python
from test_ai_processor import create_sample_jobs
create_sample_jobs()
```

Crea 3 trabajos:
1. **Senior Backend Engineer** - Caso normal
2. **Junior Frontend Developer** - Nivel junior
3. **Full Stack Ninja Rockstar** - ⚠️ Múltiples red flags

---

## 🚨 Troubleshooting

### Error: "OPENAI_API_KEY no configurada"

**Solución:** Agrega tu API key al archivo `.env`

```env
OPENAI_API_KEY=sk-proj-your-key-here
```

### Error: "ModuleNotFoundError: No module named 'openai'"

**Solución:** Instala las dependencias

```bash
pip install openai anthropic
```

### Error: "RateLimitError" (límite de API)

**Solución:** 
- Espera unos segundos y reintenta
- Reduce el `limit` en `enrich_job_data()`
- Usa un modelo más barato como `gpt-4o-mini`

### Error: JSON parsing failed

**Causa:** La IA devolvió texto mal formateado

**Solución:** El código ya incluye manejo de errores. Verifica los logs:

```bash
tail -f logs/scraper.log
```

---

## 📈 Roadmap Futuro

### Iteración 3: Mejoras de IA (Planificado)

- [ ] **Embeddings** para búsqueda semántica de trabajos
- [ ] **Clasificación multi-label** de categorías técnicas
- [ ] **Análisis de sentimiento** en descripciones
- [ ] **Detección de bias** en ofertas de trabajo
- [ ] **Recomendación de trabajos** basada en perfil
- [ ] **Generación de cover letters** personalizadas
- [ ] **Traducción automática** a múltiples idiomas

### Iteración 4: Optimizaciones

- [ ] **Batch processing** con asyncio
- [ ] **Redis** como caché distribuido
- [ ] **Queue system** (Celery/RQ) para procesamiento asíncrono
- [ ] **Monitoring** de costos de API
- [ ] **A/B testing** entre modelos (GPT vs Claude)

---

## 📚 Referencias

- [Documentación OpenAI](https://platform.openai.com/docs/guides/text-generation)
- [Documentación Anthropic](https://docs.anthropic.com/claude/docs)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)

---

## 🙋 Soporte

Si encuentras problemas:

1. Revisa los logs: `logs/scraper.log`
2. Verifica tu API key en `.env`
3. Asegúrate de tener créditos en tu cuenta de OpenAI/Anthropic
4. Consulta esta documentación

---

**¡Módulo de IA listo para usar!** 🚀🤖

*Desarrollado por Daniel - Senior AI Engineer*  
*Versión 2.1.0 - Diciembre 2025*
