# 🚀 Guía de Inicio Rápido - Labortrovilo Backend
# Rapida Starta Gvidilo - Labortrovilo Backend
# Quick Start Guide - Labortrovilo Backend

## 📁 Estructura del Proyecto / Projekta Strukturo

```
labortrovilo/
├── src/                       # 🎯 CÓDIGO PRINCIPAL / ĈEFA KODO
│   ├── __init__.py           # Inicialización del paquete
│   ├── models.py             # 🗄️ Modelos SQLAlchemy (Jobs, Companies)
│   ├── schemas.py            # ✅ Esquemas Pydantic (validación)
│   ├── database.py           # 💾 Configuración de base de datos
│   └── scraper_engine.py     # 🤖 Motor de scraping principal
│
├── logs/                      # 📝 Logs del scraper
├── config.py                  # ⚙️ Configuración centralizada
├── test_scraper.py            # 🧪 Script de pruebas
└── labortrovilo.db            # 🗄️ Base de datos SQLite
```

## 🚀 Instalación y Setup

### 1. Activar entorno virtual
```bash
venv\Scripts\activate
```

### 2. Verificar dependencias
```bash
pip list | findstr "playwright pydantic sqlalchemy"
```

### 3. Ejecutar test básico
```bash
python test_scraper.py
```

## 🎯 Uso del Scraper

### Opción 1: Usar el script de test
```python
python test_scraper.py
# Selecciona opción 1 para test completo
```

### Opción 2: Importar y usar directamente
```python
import asyncio
from src.scraper_engine import LabortroviloScraper
from src.database import init_db

async def main():
    # Inicializar BD
    init_db()
    
    # Crear scraper
    scraper = LabortroviloScraper(headless=True)
    
    try:
        await scraper.initialize()
        
        # Scrapear una URL
        result = await scraper.scrape_job("https://example.com/job")
        
        print(f"Success: {result.success}")
        if result.job_data:
            print(f"Title: {result.job_data.title}")
            print(f"Urgency: {result.job_data.hiring_urgency_score}")
        
    finally:
        await scraper.close()

asyncio.run(main())
```

## 🔧 Personalización por ATS

Los selectores CSS en `scraper_engine.py` son genéricos. Para cada ATS, personaliza:

```python
# En extract_job_data():

# Para Greenhouse:
title = await page.locator('.app-title').text_content()
company = await page.locator('.company-name').text_content()

# Para Lever:
title = await page.locator('h2[data-qa="job-title"]').text_content()
company = await page.locator('.main-footer-text a').text_content()

# Para Workday:
title = await page.locator('h3[data-automation-id="jobTitle"]').text_content()
```

## 📊 Campos Diferenciadores

### 🎯 hiring_urgency_score (0-100)
Calcula automáticamente basándose en:
- Palabras clave de urgencia (urgent, immediate, ASAP)
- Fecha de publicación reciente
- Indicadores en título (senior, lead)

### 🎯 is_it_niche (boolean)
Detecta nichos especializados:
- blockchain, web3, crypto
- quantum computing
- machine learning, AI
- bioinformatics
- embedded systems, IoT

## 🛠️ Comandos Útiles

### Ver estadísticas de BD
```python
from src.database import db_manager
stats = db_manager.get_stats()
print(stats)
```

### Verificar salud de BD
```python
from src.database import db_manager
health = db_manager.health_check()
print(f"DB Health: {health}")
```

### Ver logs en tiempo real
```bash
Get-Content -Path "logs\scraper.log" -Tail 20 -Wait
```

## 📝 Logging

Los logs se guardan en:
- `logs/scraper.log` - Todos los eventos
- También se muestran en consola

Niveles de log:
- INFO: Operaciones normales
- WARNING: Situaciones que requieren atención
- ERROR: Errores capturados pero manejados
- CRITICAL: Errores graves

## ⚠️ Notas Importantes

1. **URLs de Prueba**: Los selectores genéricos necesitan personalización por ATS
2. **Rate Limiting**: Incluye delays entre requests (configurable en config.py)
3. **Duplicados**: El sistema previene automáticamente duplicados por URL
4. **Errores**: Los errores se registran pero NO detienen el scraper

## 🔍 Siguiente Paso

Edita `test_scraper.py` y agrega URLs reales de ATS para probar:
```python
test_urls = [
    "https://boards.greenhouse.io/company/jobs/123456",
    "https://jobs.lever.co/company/job-id",
]
```

## 📚 Documentación Adicional

- `src/models.py`: Esquema completo de base de datos
- `src/schemas.py`: Todos los esquemas de validación
- `config.py`: Todas las opciones configurables
