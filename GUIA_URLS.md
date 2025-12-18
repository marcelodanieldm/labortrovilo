# 🔗 Guía para Obtener URLs de Prueba / Gvidilo por Akiri Provajn URL-ojn / Guide to Get Test URLs

## 📋 URLs Recomendadas para Pruebas / Rekomendataj URL-oj por Testoj

### 1. **Work at a Startup (YCombinator)** ⭐ RECOMENDADO
- **Sitio:** https://www.workatastartup.com/
- **Estructura HTML:** Muy limpia y estandarizada
- **Cómo obtener URLs:**
  1. Visita https://www.workatastartup.com/companies
  2. Busca empresas que te interesen
  3. Haz clic en "View Jobs"
  4. Copia la URL de cada trabajo (ej: `https://www.workatastartup.com/jobs/[ID]`)

**Ejemplo de URL válida:**
```
https://www.workatastartup.com/jobs/70123
```

---

### 2. **Greenhouse** (Sistema ATS Popular)
- **Estructura:** `https://boards.greenhouse.io/[company]/jobs/[job_id]`
- **Empresas ejemplo:**
  - Coinbase: https://boards.greenhouse.io/coinbase/jobs/
  - Stripe: https://boards.greenhouse.io/stripe/jobs/
  - Airbnb: https://boards.greenhouse.io/airbnb/jobs/

**Ejemplo de URL válida:**
```
https://boards.greenhouse.io/stripe/jobs/7129875
```

---

### 3. **Lever** (Sistema ATS)
- **Estructura:** `https://jobs.lever.co/[company]/[job_id]`
- **Empresas ejemplo:**
  - Netflix: https://jobs.lever.co/netflix
  - Spotify: https://jobs.lever.co/spotify

**Ejemplo de URL válida:**
```
https://jobs.lever.co/netflix/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

### 4. **LinkedIn Jobs**
- **Sitio:** https://www.linkedin.com/jobs/
- **Estructura:** `https://www.linkedin.com/jobs/view/[job_id]`

**Ejemplo de URL válida:**
```
https://www.linkedin.com/jobs/view/3789456123/
```

---

### 5. **Indeed**
- **Sitio:** https://www.indeed.com/
- **Estructura:** `https://www.indeed.com/viewjob?jk=[job_key]`

**Ejemplo de URL válida:**
```
https://www.indeed.com/viewjob?jk=a1b2c3d4e5f67890
```

---

## 🧪 Cómo Usar las URLs en el Test / Kiel Uzi la URL-ojn en la Testo

### Opción 1: Editar `test_quick.py`

```python
test_urls = [
    "https://www.workatastartup.com/jobs/70123",  # ← Reemplaza con URL real
    "https://boards.greenhouse.io/stripe/jobs/7129875",
]
```

### Opción 2: Editar `test_scraper.py`

```python
test_urls = [
    # YCombinator Work at a Startup
    "https://www.workatastartup.com/jobs/70123",
    
    # Greenhouse
    "https://boards.greenhouse.io/coinbase/jobs/123456",
    
    # Lever
    "https://jobs.lever.co/netflix/job-id",
]
```

---

## ⚠️ IMPORTANTE: Selectores CSS Personalizados

Cada plataforma ATS tiene diferentes selectores CSS. El scraper actual tiene selectores **genéricos** que intentan cubrir múltiples plataformas, pero puede que necesites personalizarlos.

### Ubicación del código de selectores:
**Archivo:** `src/scraper_engine.py`  
**Función:** `extract_job_data()`

### Selectores actuales implementados:

```python
# Título / Title
title_selectors = [
    'h1',  # Genérico
    '.job-title',
    '[data-qa="job-title"]',
    '.app-title',  # Greenhouse
    '.posting-headline',  # Lever
    '[data-automation-id="jobPostingHeader"]',  # Workday
    '.job-post-title',  # Work at a Startup
]

# Empresa / Company
company_selectors = [
    '.company-name',
    '[data-qa="company-name"]',
    '.company',  # Greenhouse
    '.posting-categories-value',  # Lever
    'a[href*="/companies/"]',  # Work at a Startup
]

# Descripción / Description
desc_selectors = [
    '.description',
    '.job-description',
    'article',
    '#content',  # Greenhouse
    '.section-wrapper',  # Lever
    '.job-post-content',  # Work at a Startup
]
```

---

## 🔍 Cómo Encontrar Selectores CSS para una Nueva Plataforma

### Paso 1: Abrir DevTools en el navegador
- **Chrome/Edge:** F12 o Ctrl+Shift+I
- **Firefox:** F12 o Ctrl+Shift+C

### Paso 2: Usar la herramienta "Selector"
1. Haz clic en el ícono de selector (flecha) en DevTools
2. Haz clic en el elemento que quieres scrapear (título, empresa, descripción, etc.)
3. DevTools te mostrará el HTML del elemento

### Paso 3: Identificar el selector
Busca:
- **Clases CSS:** `.job-title`, `.company-name`
- **IDs:** `#job-description`
- **Data attributes:** `[data-qa="title"]`

### Paso 4: Agregar al código
Edita `src/scraper_engine.py` y agrega tu selector a la lista correspondiente.

---

## 🚀 Ejecución Rápida del Test

```bash
# Test automatizado (no interactivo)
python test_quick.py

# Test interactivo con menú
python test_scraper.py
# Selecciona opción 1
```

---

## 📊 Resultado Esperado

Si todo funciona correctamente, verás:

```
✓ Exitosos: 1/1
✗ Fallidos: 0/1

--- Resultado #1 ---
URL: https://www.workatastartup.com/jobs/70123
Status: ✓ ÉXITO

📋 Datos Extraídos:
   Título: Senior Backend Engineer
   Empresa: Example Startup Inc.
   Ubicación: San Francisco, CA
   Remoto: True
   Platform: other

🎯 Campos Diferenciadores:
   Urgency Score: 65.0/100
   IT Niche: NO
```

---

## 🆘 Troubleshooting

### Error 404 (URL no encontrada)
- **Causa:** La URL de prueba no existe o expiró
- **Solución:** Obtén URLs frescas del sitio web

### Error "No se pudo extraer el título"
- **Causa:** Los selectores CSS no coinciden con la estructura de la página
- **Solución:** Inspecciona la página y actualiza los selectores en `src/scraper_engine.py`

### Timeout en navegación
- **Causa:** La página tarda mucho en cargar
- **Solución:** Ajusta `PLAYWRIGHT_TIMEOUT` en `config.py` (default: 60000ms)

---

## 📝 Notas Adicionales

- **Rate Limiting:** El scraper incluye delays configurables para no saturar los servidores
- **Headless Mode:** Cambia `headless=True` para que el navegador no se vea
- **Logs:** Todos los logs se guardan en `logs/scraper.log`

---

## 💡 Tips para Personalización

1. **Prioriza plataformas específicas:** Si sabes que usarás principalmente Greenhouse, mueve sus selectores al principio de la lista
2. **Agrega selectores fallback:** Siempre ten un selector genérico como `h1` al final
3. **Prueba con múltiples URLs:** Usa al menos 3-5 URLs de diferentes plataformas para validar
