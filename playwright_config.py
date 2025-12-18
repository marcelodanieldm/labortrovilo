# Configuración de Playwright para Python / Playwright-agordado por Python
# Playwright Configuration for Python

"""
Este archivo documenta la configuración de Playwright para Python.
Ĉi tiu dosiero dokumentas la agordon de Playwright por Python.
This file documents the Playwright configuration for Python.

NOTA IMPORTANTE / GRAVA NOTO / IMPORTANT NOTE:
===============================================
Este proyecto usa Playwright para PYTHON, no para Node.js/JavaScript.
Ĉi tiu projekto uzas Playwright por PYTHON, ne por Node.js/JavaScript.
This project uses Playwright for PYTHON, not for Node.js/JavaScript.

La configuración de Playwright se maneja en Python a través de:
- config.py: Configuración general
- engine.py: Implementación del scraper

Instalación / Instalado / Installation:
---------------------------------------
1. Instalar dependencias Python:
   pip install -r requirements.txt

2. Instalar navegadores Playwright:
   playwright install chromium

Uso / Uzo / Usage:
------------------
python engine.py

Configuración avanzada / Altnivela agordado / Advanced configuration:
---------------------------------------------------------------------
Edita config.py para cambiar:
- PLAYWRIGHT_HEADLESS: True/False (ejecutar con/sin interfaz gráfica)
- PLAYWRIGHT_TIMEOUT: tiempo de espera en milisegundos
- USER_AGENT: agente de usuario para las peticiones
"""

# Configuración de ejemplo para Playwright Python
# Ekzempla agordado por Playwright Python
# Example configuration for Playwright Python

PLAYWRIGHT_CONFIG = {
    # Ejecutar en modo headless (sin interfaz gráfica) / Plenumi en headless reĝimo
    "headless": True,
    
    # Tiempo de espera para navegación (ms) / Atenditempo por navigado (ms)
    "timeout": 30000,
    
    # Tamaño de ventana / Fenestra grandeco / Window size
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    
    # User Agent personalizado / Personecigita User Agent
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    
    # Navegador a usar / Retumilo por uzi / Browser to use
    "browser": "chromium",  # Opciones: chromium, firefox, webkit
    
    # Argumentos adicionales para el navegador / Aldonaj argumentoj por la retumilo
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    ],
    
    # Configuración de red / Reta agordado / Network configuration
    "ignore_https_errors": False,
    "java_script_enabled": True,
}

# Para usar esta configuración en engine.py:
# Por uzi ĉi tiun agordon en engine.py:
# To use this configuration in engine.py:
"""
from playwright.async_api import async_playwright

async def initialize_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=PLAYWRIGHT_CONFIG["headless"],
        args=PLAYWRIGHT_CONFIG["args"]
    )
    context = await browser.new_context(
        viewport=PLAYWRIGHT_CONFIG["viewport"],
        user_agent=PLAYWRIGHT_CONFIG["user_agent"]
    )
    page = await context.new_page()
    page.set_default_timeout(PLAYWRIGHT_CONFIG["timeout"])
    return browser, page
"""
