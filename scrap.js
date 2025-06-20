
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWebsite(url) {
    let browser;
    try {
        browser = await chromium.launch({ headless: true }); // headless: true para no mostrar el navegador
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'domcontentloaded' }); // Esperar a que el DOM esté cargado

        // Ejemplo 1: Scrapear títulos y enlaces de artículos (ajusta los selectores según la web real)
        const articles = await page.evaluate(() => {
            const results = [];
            // Ejemplo de selectores para un blog común
            const articleElements = document.querySelectorAll('h3 a, .post-title a, .article-title a'); // Ajusta estos selectores
            articleElements.forEach(element => {
                results.push({
                    title: element.innerText.trim(),
                    url: element.href
                });
            });
            return results;
        });

        console.log('Artículos encontrados:', articles);

        // Ejemplo 2: Scrapear un elemento específico (por ejemplo, el título principal de la página)
        const pageTitle = await page.evaluate(() => {
            const h1Element = document.querySelector('h1');
            return h1Element ? h1Element.innerText.trim() : 'No se encontró el título H1';
        });

        console.log('Título principal de la página:', pageTitle);

        // Guardar los datos en un archivo JSON para que el frontend pueda leerlos
        const dataToSave = {
            pageTitle: pageTitle,
            articles: articles
        };

        const outputPath = path.join(__dirname, 'scraped_data.json');
        fs.writeFileSync(outputPath, JSON.stringify(dataToSave, null, 2), 'utf-8');
        console.log(`Datos guardados en ${outputPath}`);

        return dataToSave;

    } catch (error) {
        console.error('Error durante el scraping:', error);
        return null;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Para ejecutar el scraper
const targetUrl = 'www.google.com'; // Reemplaza con la URL que quieres scrapear
scrapeWebsite(targetUrl).then(data => {
    if (data) {
        console.log('Scraping completado con éxito.');
    } else {
        console.log('El scraping falló.');
    }
});