
const puppeteer = require('puppeteer');

async function scrapeGoogle(query) {
    let browser;
    try {
        // 1. Iniciar el navegador
        // `headless: false` abre una ventana de navegador visible (útil para depurar)
        // `headless: true` ejecuta el navegador en segundo plano (más rápido para producción)
        browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();

        // 2. Navegar a la página de búsqueda de Google
        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        await page.goto(googleSearchUrl, { waitUntil: 'networkidle2' });
        // `waitUntil: 'networkidle2'` espera hasta que no haya más de 2 conexiones de red en 500ms,
        // asegurando que la página esté completamente cargada.

        // 3. Evaluar la página para extraer los resultados
        const results = await page.evaluate(() => {
            const data = [];
            // Selecciona todos los elementos que contienen un resultado de búsqueda
            // Esta es una selectora común, pero Google puede cambiarla.
            // Es crucial inspeccionar la página de Google para encontrar las selectoras correctas.
            const searchResults = document.querySelectorAll('div.g'); // Divs con clase 'g' suelen ser resultados

            searchResults.forEach(result => {
                const titleElement = result.querySelector('h3');
                const linkElement = result.querySelector('a');
                const snippetElement = result.querySelector('div.VwiC3b'); // Selector para el fragmento de texto (description)

                const title = titleElement ? titleElement.innerText : 'N/A';
                const link = linkElement ? linkElement.href : 'N/A';
                const snippet = snippetElement ? snippetElement.innerText : 'N/A';

                if (title !== 'N/A' && link !== 'N/A') { // Solo añade resultados válidos
                    data.push({ title, link, snippet });
                }
            });
            return data;
        });

        console.log(`Resultados de búsqueda para "${query}":`);
        results.forEach((result, index) => {
            console.log(`--- Resultado ${index + 1} ---`);
            console.log(`Título: ${result.title}`);
            console.log(`Enlace: ${result.link}`);
            console.log(`Descripción: ${result.snippet}`);
            console.log('---------------------');
        });

        return results;

    } catch (error) {
        console.error('Error durante el scraping:', error);
        return [];
    } finally {
        // 4. Cerrar el navegador
        if (browser) {
            await browser.close();
        }
    }
}

// Ejemplo de uso:
const searchQuery = 'escrapeando con Playwright';
scrapeGoogle(searchQuery);

// Se puede pasar un argumento desde la línea de comandos
// const queryFromArgs = process.argv[2];
// if (queryFromArgs) {
//     scrapeGoogle(queryFromArgs);
// } else {
//     console.log('Por favor, proporcionarn una consulta de búsqueda como argumento. Ejemplo: node scraper.js "mi busqueda"');
// }