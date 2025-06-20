document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const jobListingsContainer = document.getElementById('jobListings'); // Contenedor de resultados de trabajos
    const jobCountElement = document.getElementById('jobCount'); // Elemento para mostrar el conteo total
    const searchInput = document.getElementById('searchInput'); // Input de búsqueda
    const searchButton = document.getElementById('searchButton'); // Botón de búsqueda
    const modalityCheckboxes = document.querySelectorAll('input[name="modality"]'); // Checkboxes de modalidad
    const relocationRadios = document.querySelectorAll('input[name="relocation"]'); // Radios de relocalización
    const regionCheckboxes = document.querySelectorAll('input[name="region"]'); // Checkboxes de región
    const clearFiltersButton = document.getElementById('clearFiltersButton'); // Botón para limpiar filtros
    const themeToggle = document.getElementById('theme-toggle'); // Botón de cambio de tema
    const languageSwitcher = document.getElementById('language-switcher'); // Selector de idioma
    const subscribeForm = document.getElementById('subscribeForm'); // Formulario de suscripción

    // --- Datos de Ejemplo (En un escenario real, esto vendría de una API o de un backend de web scraping) ---
    // Este array simula la información que obtendrías de las búsquedas laborales.
    let allJobs = [
        {
            id: 1,
            company: 'Tech Solutions Inc.',
            image: 'https://placehold.co/60x60/FF5733/FFFFFF?text=TS', // Imagen de placeholder para la empresa
            title: 'QA Automation Engineer',
            seniority: 'Senior',
            salary: '$80,000 - $100,000 USD',
            date: 'Hace 3 días',
            modality: 'remote', // Puede ser 'remote' o 'hybrid'
            relocation: 'no',   // Puede ser 'yes' o 'no'
            region: 'LATAM',    // Puede ser 'LATAM', 'EMEA', 'Europe'
            keywords: 'Selenium, Cypress, API Testing, Python, Automation' // Palabras clave para la búsqueda
        },
        {
            id: 2,
            company: 'Innovate Systems',
            image: 'https://placehold.co/60x60/33FF57/FFFFFF?text=IS',
            title: 'Manual QA Tester',
            seniority: 'Junior',
            salary: '$45,000 - $60,000 USD',
            date: 'Hace 1 semana',
            modality: 'hybrid',
            relocation: 'no',
            region: 'Europe',
            keywords: 'Manual Testing, UAT, Jira, Exploratory'
        },
        {
            id: 3,
            company: 'Global Software',
            image: 'https://placehold.co/60x60/3357FF/FFFFFF?text=GS',
            title: 'Lead QA Engineer',
            seniority: 'Lead',
            salary: '$110,000 - $140,000 USD',
            date: 'Hace 2 días',
            modality: 'remote',
            relocation: 'yes',
            region: 'EMEA',
            keywords: 'Leadership, Performance Testing, CI/CD, Agile, DevOps'
        },
        {
            id: 4,
            company: 'NextGen Tech',
            image: 'https://placehold.co/60x60/FFC300/FFFFFF?text=NT',
            title: 'QA Analyst',
            seniority: 'Mid-level',
            salary: '$60,000 - $75,000 USD',
            date: 'Hace 5 días',
            modality: 'remote',
            relocation: 'no',
            region: 'LATAM',
            keywords: 'Agile, SQL, Mobile Testing, Functional'
        },
        {
            id: 5,
            company: 'Web Solutions Co.',
            image: 'https://placehold.co/60x60/DAF7A6/FFFFFF?text=WS',
            title: 'QA Engineer',
            seniority: 'Junior',
            salary: '$40,000 - $55,000 USD',
            date: 'Hace 10 días',
            modality: 'hybrid',
            relocation: 'yes',
            region: 'Europe',
            keywords: 'Web Testing, Frontend, JavaScript, API'
        },
        {
            id: 6,
            company: 'Enterprise Apps',
            image: 'https://placehold.co/60x60/C70039/FFFFFF?text=EA',
            title: 'Senior SDET',
            seniority: 'Senior',
            salary: '$95,000 - $120,000 USD',
            date: 'Hace 1 día',
            modality: 'remote',
            relocation: 'no',
            region: 'EMEA',
            keywords: 'SDET, Java, Selenium, Backend Testing, Microservices'
        },
        {
            id: 7,
            company: 'Startup X',
            image: 'https://placehold.co/60x60/581845/FFFFFF?text=SX',
            title: 'QA Tester',
            seniority: 'Junior',
            salary: '$40,000 - $50,000 USD',
            date: 'Hace 2 semanas',
            modality: 'remote',
            relocation: 'no',
            region: 'LATAM',
            keywords: 'Exploratory Testing, Startups, Manual'
        },
        {
            id: 8,
            company: 'Fintech Innovations',
            image: 'https://placehold.co/60x60/FF5733/FFFFFF?text=FI',
            title: 'QA Automation Lead',
            seniority: 'Lead',
            salary: '$120,000 - $150,000 USD',
            date: 'Hace 4 días',
            modality: 'hybrid',
            relocation: 'yes',
            region: 'Europe',
            keywords: 'Fintech, Leadership, Python, Playwright, Cloud'
        },
        {
            id: 9,
            company: 'HealthTech Solutions',
            image: 'https://placehold.co/60x60/33FF57/FFFFFF?text=HS',
            title: 'Manual QA Specialist',
            seniority: 'Mid-level',
            salary: '$55,000 - $70,000 USD',
            date: 'Hace 6 días',
            modality: 'remote',
            relocation: 'no',
            region: 'EMEA',
            keywords: 'Healthcare, Manual, Regression Testing, Performance'
        },
        {
            id: 10,
            company: 'Gaming Studios',
            image: 'https://placehold.co/60x60/3357FF/FFFFFF?text=GS',
            title: 'Game QA Tester',
            seniority: 'Junior',
            salary: '$35,000 - $45,000 USD',
            date: 'Hace 1 día',
            modality: 'hybrid',
            relocation: 'yes',
            region: 'LATAM',
            keywords: 'Gaming, Console Testing, Bug Reporting, Jira'
        }
    ];

    let currentJobs = [...allJobs]; // Una copia de todos los trabajos para aplicar filtros

    // --- Objeto de traducciones para múltiples idiomas ---
    const translations = {
        es: {
            title: "Encuentra tu Trabajo QA Ideal 🚀",
            headerTitle: "QA Job Finder 🔎✨",
            themeToggle: "Cambiar Tema",
            searchPlaceholder: "Buscar por palabra clave...",
            searchButton: "Buscar",
            modalityTitle: "Modalidad 📍",
            remote: "Remoto 🏠",
            hybrid: "Híbrido 🏢",
            relocationTitle: "Relocalización ✈️",
            relocationYes: "Sí ✅",
            relocationNo: "No ❌",
            regionTitle: "Región del Puesto 🌎",
            latam: "LATAM 🇧🇷🇲🇽🇦🇷",
            emea: "EMEA 🇪🇺🇦🇪",
            europe: "Europa 🇪🇺",
            clearFilters: "Limpiar Filtros 🗑️",
            jobCountText: "Total de Posiciones Encontradas: ",
            noResults: "¡Anímate a buscar! 🕵️‍♀️ No hay resultados aún o prueba otros filtros.",
            subscribeSectionTitle: "¿No encuentras lo que buscas? 🧐 ¡Suscríbete!",
            subscribeSectionText: "Te enviaremos las últimas y mejores oportunidades de QA directamente a tu bandeja de entrada. 📩",
            subscribeEmailPlaceholder: "Tu correo electrónico",
            subscribeButton: "Suscribirme 👍",
            blogSectionTitle: "Artículos Recientes del Blog 📚",
            blog1Title: "Las Habilidades Clave del QA Moderno 🧠",
            blog1Text: "Descubre qué necesitas para destacar en el mundo del aseguramiento de calidad hoy. ✨",
            blog1Link: "Leer más...",
            blog2Title: "Automatización vs. Testing Manual: ¿Dónde Invertir? 🤖✍️",
            blog2Text: "Un análisis profundo sobre las tendencias actuales en testing y cómo impactan tu carrera.",
            blog2Link: "Leer más...",
            blog3Title: "Guía Definitiva para Entrevistas de QA 🗣️🚀",
            blog3Text: "Consejos y trucos para superar cualquier entrevista técnica o de comportamiento.",
            blog3Link: "Leer más...",
            footerText: "&copy; 2025 QA Job Finder. Todos los derechos reservados. 💼",
            // Prefijos para las tarjetas de trabajo
            seniorityPrefix: "Seniority: ",
            salaryPrefix: "Salario Aprox: ",
            datePrefix: "Publicado: "
        },
        en: {
            title: "Find Your Ideal QA Job 🚀",
            headerTitle: "QA Job Finder 🔎✨",
            themeToggle: "Toggle Theme",
            searchPlaceholder: "Search by keyword...",
            searchButton: "Search",
            modalityTitle: "Modality 📍",
            remote: "Remote 🏠",
            hybrid: "Hybrid 🏢",
            relocationTitle: "Relocation ✈️",
            relocationYes: "Yes ✅",
            relocationNo: "No ❌",
            regionTitle: "Job Region 🌎",
            latam: "LATAM 🇧🇷🇲🇽🇦🇷",
            emea: "EMEA 🇪🇺🇦🇪",
            europe: "Europe 🇪🇺",
            clearFilters: "Clear Filters 🗑️",
            jobCountText: "Total Positions Found: ",
            noResults: "Go search! 🕵️‍♀️ No results yet or try other filters.",
            subscribeSectionTitle: "Can't find what you're looking for? 🧐 Subscribe!",
            subscribeSectionText: "We'll send you the latest and best QA opportunities directly to your inbox. 📩",
            subscribeEmailPlaceholder: "Your email address",
            subscribeButton: "Subscribe 👍",
            blogSectionTitle: "Recent Blog Articles 📚",
            blog1Title: "Key Skills for Modern QA 🧠",
            blog1Text: "Discover what you need to stand out in today's quality assurance world. ✨",
            blog1Link: "Read more...",
            blog2Title: "Automation vs. Manual Testing: Where to Invest? 🤖✍️",
            blog2Text: "A deep dive into current testing trends and how they impact your career.",
            blog2Link: "Read more...",
            blog3Title: "Ultimate Guide to QA Interviews 🗣️🚀",
            blog3Text: "Tips and tricks to ace any technical or behavioral interview.",
            blog3Link: "Read more...",
            footerText: "&copy; 2025 QA Job Finder. All rights reserved. 💼",
            seniorityPrefix: "Seniority: ",
            salaryPrefix: "Approx. Salary: ",
            datePrefix: "Published: "
        },
        eo: {
            title: "Trovi Vian Idealan QA-Laboron 🚀",
            headerTitle: "QA Laboro-Trovilo 🔎✨",
            themeToggle: "Ŝanĝi Temon",
            searchPlaceholder: "Serĉi per ŝlosilvorto...",
            searchButton: "Serĉi",
            modalityTitle: "Modo 📍",
            remote: "Malproksima 🏠",
            hybrid: "Hibrida 🏢",
            relocationTitle: "Relokado ✈️",
            relocationYes: "Jes ✅",
            relocationNo: "Ne ❌",
            regionTitle: "Labor-Regiono 🌎",
            latam: "LATAM 🇧🇷🇲🇽🇦🇷",
            emea: "EMEA 🇪🇺🇦🇪",
            europe: "Eŭropo 🇪🇺",
            clearFilters: "Malplenigi Filtrilojn 🗑️",
            jobCountText: "Totalo de Troviĝintaj Pozicioj: ",
            noResults: "Kuraĝu serĉi! 🕵️‍♀️ Neniuj rezultoj ankoraŭ aŭ provu aliajn filtrilojn.",
            subscribeSectionTitle: "Ĉu vi ne trovas tion, kion vi serĉas? 🧐 Abonu!",
            subscribeSectionText: "Ni sendos al vi la plej novajn kaj plej bonajn QA-oportunojn rekte al via enirkesto. 📩",
            subscribeEmailPlaceholder: "Via retpoŝtadreso",
            subscribeButton: "Aboni 👍",
            blogSectionTitle: "Lastatempaj Blogaj Artikoloj 📚",
            blog1Title: "La Ŝlosilaj Kapabloj de Moderna QA 🧠",
            blog1Text: "Eksciu, kion vi bezonas por elstari en la mondo de kvalito-certigo hodiaŭ. ✨",
            blog1Link: "Legu pli...",
            blog2Title: "Aŭtomatigo kontraŭ Mana Testado: Kien Investi? 🤖✍️",
            blog2Text: "Profunda analizo pri la nunaj testado-tendencoj kaj kiel ili influas vian karieron.",
            blog2Link: "Legu pli...",
            blog3Title: "Finfinaj Gvidiloj por QA-Intervjuoj 🗣️🚀",
            blog3Text: "Konsiloj kaj trukoj por sukcese trairi ajnan teknikan aŭ kondutan intervjuon.",
            blog3Link: "Legu pli...",
            footerText: "&copy; 2025 QA Laboro-Trovilo. Ĉiuj rajtoj rezervitaj. 💼",
            seniorityPrefix: "Senioreco: ",
            salaryPrefix: "Proks. Salajro: ",
            datePrefix: "Publikigita: "
        }
    };

    // --- Funciones de Utilidad ---

    /**
     * Actualiza el contenido de la página según el idioma seleccionado.
     * @param {string} lang - El código del idioma (ej. 'es', 'en', 'eo').
     */
    function updateContent(lang) {
        const t = translations[lang];

        document.title = t.title;
        document.querySelector('header h1').innerHTML = t.headerTitle;
        document.getElementById('theme-toggle').title = t.themeToggle;
        document.getElementById('searchInput').placeholder = t.searchPlaceholder;
        document.getElementById('searchButton').textContent = t.searchButton;

        // Actualizar textos de los filtros
        document.querySelector('.filter-group:nth-of-type(1) h3').textContent = t.modalityTitle;
        // Se usa nextSibling para obtener el nodo de texto después del input, que es donde está el texto del label
        document.querySelector('label input[value="remote"]').nextSibling.textContent = ` ${t.remote}`;
        document.querySelector('label input[value="hybrid"]').nextSibling.textContent = ` ${t.hybrid}`;

        document.querySelector('.filter-group:nth-of-type(2) h3').textContent = t.relocationTitle;
        document.querySelector('label input[value="yes"]').nextSibling.textContent = ` ${t.relocationYes}`;
        document.querySelector('label input[value="no"]').nextSibling.textContent = ` ${t.relocationNo}`;

        document.querySelector('.filter-group:nth-of-type(3) h3').textContent = t.regionTitle;
        document.querySelector('label input[value="LATAM"]').nextSibling.textContent = ` ${t.latam}`;
        document.querySelector('label input[value="EMEA"]').nextSibling.textContent = ` ${t.emea}`;
        document.querySelector('label input[value="Europe"]').nextSibling.textContent = ` ${t.europe}`;

        document.getElementById('clearFiltersButton').textContent = t.clearFilters;

        // Actualizar textos de la sección de resultados
        jobCountElement.innerHTML = `${t.jobCountText}${currentJobs.length} 📊`;
        document.querySelector('.no-results').textContent = t.noResults;

        // Actualizar textos de la sección de suscripción
        document.querySelector('.subscribe-section h2').innerHTML = t.subscribeSectionTitle;
        document.querySelector('.subscribe-section p').innerHTML = t.subscribeSectionText;
        document.getElementById('subscribeEmail').placeholder = t.subscribeEmailPlaceholder;
        document.querySelector('#subscribeForm button[type="submit"]').textContent = t.subscribeButton;

        // Actualizar textos de la sección del blog
        document.querySelector('.blog-section h2').innerHTML = t.blogSectionTitle;
        document.querySelector('.blog-post:nth-of-type(1) h3').innerHTML = t.blog1Title;
        document.querySelector('.blog-post:nth-of-type(1) p').innerHTML = t.blog1Text;
        document.querySelector('.blog-post:nth-of-type(1) a').innerHTML = t.blog1Link;

        document.querySelector('.blog-post:nth-of-type(2) h3').innerHTML = t.blog2Title;
        document.querySelector('.blog-post:nth-of-type(2) p').innerHTML = t.blog2Text;
        document.querySelector('.blog-post:nth-of-type(2) a').innerHTML = t.blog2Link;

        document.querySelector('.blog-post:nth-of-type(3) h3').innerHTML = t.blog3Title;
        document.querySelector('.blog-post:nth-of-type(3) p').innerHTML = t.blog3Text;
        document.querySelector('.blog-post:nth-of-type(3) a').innerHTML = t.blog3Link;

        // Actualizar texto del pie de página
        document.querySelector('footer p').innerHTML = t.footerText;

        // Volver a renderizar los trabajos para aplicar los prefijos traducidos en las tarjetas
        renderJobs(currentJobs);
    }

    /**
     * Crea un elemento de tarjeta de trabajo (job card) a partir de un objeto de trabajo.
     * @param {object} job - El objeto con los datos del trabajo.
     * @returns {HTMLElement} El elemento div que representa la tarjeta de trabajo.
     */
    function createJobCard(job) {
        const t = translations[languageSwitcher.value]; // Obtener las traducciones actuales para los prefijos
        const card = document.createElement('div');
        card.classList.add('job-card');
        card.innerHTML = `
            <div class="job-card-header">
                <img src="${job.image}" alt="${job.company} Logo" class="company-logo" onerror="this.onerror=null;this.src='https://placehold.co/60x60/cccccc/000000?text=No+Logo';">
                <div>
                    <h3>${job.title}</h3>
                    <p>${job.company}</p>
                </div>
            </div>
            <p class="seniority">${t.seniorityPrefix}${job.seniority}</p>
            <p class="salary">${t.salaryPrefix}${job.salary}</p>
            <p class="date">${t.datePrefix}${job.date}</p>
        `;
        return card;
    }

    /**
     * Renderiza las ofertas de trabajo en el contenedor del DOM.
     * Muestra solo los primeros 3 resultados en el front, pero el conteo es del total filtrado.
     * @param {Array<object>} jobsToRender - El array de objetos de trabajo a renderizar.
     */
    function renderJobs(jobsToRender) {
        jobListingsContainer.innerHTML = ''; // Limpiar resultados anteriores
        const t = translations[languageSwitcher.value]; // Obtener traducciones para el mensaje de no resultados

        if (jobsToRender.length === 0) {
            // Mostrar mensaje si no hay resultados
            const noResultsMessage = document.createElement('p');
            noResultsMessage.classList.add('no-results');
            noResultsMessage.textContent = t.noResults;
            jobListingsContainer.appendChild(noResultsMessage);
        } else {
            // Mostrar solo los primeros 3 resultados en el front como se solicita en el feature
            jobsToRender.slice(0, 3).forEach(job => {
                jobListingsContainer.appendChild(createJobCard(job));
            });
        }
        // Actualizar el contador de trabajos con el total de trabajos filtrados
        jobCountElement.innerHTML = `${t.jobCountText}${jobsToRender.length} 📊`;
    }

    /**
     * Aplica todos los filtros seleccionados por el usuario a la lista de trabajos.
     */
    function applyFilters() {
        let filteredJobs = [...allJobs]; // Empezar con una copia de todos los trabajos

        // 1. Filtrar por búsqueda de texto (insensible a mayúsculas/minúsculas y recorta espacios)
        const searchTerm = searchInput.value.toLowerCase().trim();
        if (searchTerm) {
            filteredJobs = filteredJobs.filter(job =>
                job.title.toLowerCase().includes(searchTerm) ||
                job.company.toLowerCase().includes(searchTerm) ||
                job.keywords.toLowerCase().includes(searchTerm) // Búsqueda en palabras clave también
            );
        }

        // 2. Filtrar por modalidad (híbrido/remoto)
        const selectedModalities = Array.from(modalityCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        if (selectedModalities.length > 0) {
            filteredJobs = filteredJobs.filter(job =>
                selectedModalities.includes(job.modality)
            );
        }

        // 3. Filtrar por relocalización
        const selectedRelocation = Array.from(relocationRadios)
            .find(radio => radio.checked); // Encuentra el radio button seleccionado

        if (selectedRelocation) {
            filteredJobs = filteredJobs.filter(job =>
                job.relocation === selectedRelocation.value
            );
        }

        // 4. Filtrar por región
        const selectedRegions = Array.from(regionCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        if (selectedRegions.length > 0) {
            filteredJobs = filteredJobs.filter(job =>
                selectedRegions.includes(job.region)
            );
        }

        currentJobs = filteredJobs; // Actualizar el array de trabajos que coinciden con los filtros
        renderJobs(filteredJobs); // Volver a renderizar los trabajos filtrados
    }

    // --- Event Listeners ---

    // Evento para el botón de búsqueda
    searchButton.addEventListener('click', applyFilters);

    // Evento para el input de búsqueda (permite buscar al presionar Enter)
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            applyFilters();
        }
    });

    // Eventos para los checkboxes y radios de filtros (se aplican automáticamente al cambiar)
    modalityCheckboxes.forEach(checkbox => checkbox.addEventListener('change', applyFilters));
    relocationRadios.forEach(radio => radio.addEventListener('change', applyFilters));
    regionCheckboxes.forEach(checkbox => checkbox.addEventListener('change', applyFilters));

    // Evento para el botón de limpiar filtros
    clearFiltersButton.addEventListener('click', () => {
        // Resetear el input de búsqueda
        searchInput.value = '';
        // Desmarcar todos los checkboxes de modalidad
        modalityCheckboxes.forEach(checkbox => checkbox.checked = false);
        // Desmarcar todos los radios de relocalización
        relocationRadios.forEach(radio => radio.checked = false);
        // Desmarcar todos los checkboxes de región
        regionCheckboxes.forEach(checkbox => checkbox.checked = false);
        applyFilters(); // Volver a renderizar los trabajos sin filtros
    });

    // Evento para el botón de cambio de tema (Modo Oscuro/Claro)
    themeToggle.addEventListener('click', () => {
        // Alternar las clases 'dark-mode' y 'light-mode' en el body
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('light-mode');
        // Guardar la preferencia del tema en localStorage para que persista
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    });

    // Cargar la preferencia de tema al cargar la página
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.remove('light-mode', 'dark-mode'); // Eliminar clases por defecto
        document.body.classList.add(`${savedTheme}-mode`); // Añadir la clase guardada
    } else {
        document.body.classList.add('light-mode'); // Por defecto, modo claro si no hay preferencia
    }

    // Evento para el selector de idioma
    languageSwitcher.addEventListener('change', (event) => {
        const selectedLang = event.target.value;
        updateContent(selectedLang); // Actualizar todo el contenido de la página
        localStorage.setItem('language', selectedLang); // Guardar la preferencia de idioma
    });

    // Cargar la preferencia de idioma al cargar la página
    const savedLang = localStorage.getItem('language');
    if (savedLang) {
        languageSwitcher.value = savedLang; // Establecer el valor del selector al idioma guardado
    }
    // Inicializar el contenido de la página con el idioma actual (o guardado)
    updateContent(languageSwitcher.value);

    // Evento para el formulario de suscripción (simulado)
    subscribeForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Previene el envío por defecto del formulario (recarga de página)
        const email = document.getElementById('subscribeEmail').value;
        if (email) {
            // Se usa alert() para la demostración, en un entorno real se usaría un modal o notificación
            alert(`¡Gracias por suscribirte con ${email}! Te mantendremos informado de nuevas posiciones. 🎉`);
            subscribeForm.reset(); // Limpiar el campo del email
        }
    });

    // --- Inicialización ---
    // Renderizar los trabajos iniciales (sin filtros aplicados) al cargar la página
    renderJobs(currentJobs);
});
