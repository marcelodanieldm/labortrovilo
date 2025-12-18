# 🚀 Guía Rápida de Desarrollo - Labortrovilo UI

## ⚡ Inicio Rápido (5 minutos)

```bash
# 1. Instalar dependencias
npm install

# 2. Iniciar servidor de desarrollo
npm start

# 3. Abrir navegador en http://localhost:3000
```

## 🎯 Cambio de Roles (Demo)

Usa el **dropdown de roles** en la esquina superior derecha para ver las diferentes vistas:

1. **👤 CANDIDATO** - Vista de búsqueda de empleo
2. **💼 HR_PRO** - Dashboard con analytics
3. **⚙️ ADMIN** - Panel de control de scrapers
4. **👑 SUPERUSER** - Acceso total

## 📂 Estructura Rápida

```
src/
├── App.js                    # ✅ Router principal
├── components/
│   ├── Navbar.jsx           # ✅ Navegación dinámica
│   ├── JobCard.jsx          # ✅ Card de oferta
│   ├── MainFeed.jsx         # ✅ Feed de empleos
│   ├── IntelligenceDashboard.jsx  # ✅ Gráficos
│   ├── B2BPortal.jsx        # ✅ Portal HR
│   ├── AdminPanel.jsx       # ✅ Panel admin
│   └── UIComponents.jsx     # ✅ Componentes reutilizables
```

## 🎨 Componentes Principales

### 1. JobCard - Tarjeta de Oferta
```jsx
<JobCard 
  job={{
    title: "Senior Developer",
    company: "TechCorp",
    techStack: ["React", "Node.js"],
    salaryRange: "$100k - $120k",
    modality: "Remoto"
  }}
/>
```

### 2. Badge - Etiqueta
```jsx
import { Badge } from './UIComponents';
<Badge color="success">Activo</Badge>
```

### 3. StatsCard - Tarjeta de Estadísticas
```jsx
import { StatsCard } from './UIComponents';
<StatsCard 
  title="Total Ofertas"
  value="1,847"
  change="+12%"
  color="primary"
/>
```

### 4. Skeleton - Loading State
```jsx
import { CardSkeleton } from './UIComponents';
{isLoading ? <CardSkeleton /> : <JobCard job={data} />}
```

## 🎨 Clases CSS Útiles

```css
/* Botones */
.btn-primary     /* Botón principal azul */
.btn-secondary   /* Botón secundario outline */

/* Contenedores */
.card            /* Card con sombra y border */
.input           /* Input con focus ring */

/* Loading */
.skeleton        /* Skeleton animado */

/* Animaciones */
.animate-fade-in     /* Fade in suave */
.animate-slide-up    /* Slide desde abajo */
.animate-pulse-soft  /* Pulso suave */
```

## 🌈 Paleta de Colores

```javascript
// Principales
primary: #0ea5e9   // Cyan/Blue
success: #10b981   // Green
warning: #f59e0b   // Orange
error: #ef4444     // Red

// Dark Theme
dark-bg: #0f172a       // Background principal
dark-surface: #1e293b  // Cards y superficies
dark-border: #334155   // Bordes
dark-text: #e2e8f0     // Texto
```

## 🔌 Conectar con FastAPI Backend

### Ejemplo: Cargar Jobs desde API

```javascript
// En MainFeed.jsx
useEffect(() => {
  const fetchJobs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs');
      const data = await response.json();
      setJobs(data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };
  
  fetchJobs();
}, []);
```

### Ejemplo: Ejecutar Scraper

```javascript
// En AdminPanel.jsx
const runScraper = async (scraperId) => {
  try {
    await fetch(`http://localhost:8000/api/scrapers/${scraperId}/run`, {
      method: 'POST',
    });
    // Actualizar estado
  } catch (error) {
    console.error('Error running scraper:', error);
  }
};
```

## 📊 Trabajar con Recharts

### Bar Chart Básico

```jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
    <XAxis dataKey="name" stroke="#94a3b8" />
    <YAxis stroke="#94a3b8" />
    <Tooltip contentStyle={{ backgroundColor: '#1e293b' }} />
    <Bar dataKey="value" fill="#0ea5e9" />
  </BarChart>
</ResponsiveContainer>
```

## 🔍 Debug Tips

### 1. Ver rol actual
```javascript
// En cualquier componente
console.log(localStorage.getItem('userRole'));
```

### 2. Ver estado de navegación
```javascript
import { useLocation } from 'react-router-dom';
const location = useLocation();
console.log(location.pathname);
```

### 3. React DevTools
Instala la extensión de React DevTools en Chrome/Firefox para inspeccionar componentes.

## 🚀 Build para Producción

```bash
# Crear build optimizado
npm run build

# La carpeta build/ contendrá los archivos estáticos
# Servir con cualquier servidor web (nginx, apache, etc.)
```

## 📱 Testing Responsive

### Breakpoints de Tailwind
```
sm: 640px   // Móviles grandes
md: 768px   // Tablets
lg: 1024px  // Laptops
xl: 1280px  // Desktops
2xl: 1536px // Pantallas grandes
```

### Testing en navegador
- Chrome DevTools: F12 → Toggle device toolbar
- Prueba en: Mobile (375px), Tablet (768px), Desktop (1440px)

## 🎯 Próximos Pasos de Desarrollo

### Prioridad Alta
- [ ] Conectar con API de FastAPI
- [ ] Implementar autenticación JWT
- [ ] Agregar paginación en JobCards
- [ ] WebSockets para updates en tiempo real

### Prioridad Media
- [ ] Filtros avanzados (salario, experiencia)
- [ ] Sistema de favoritos
- [ ] Notificaciones push
- [ ] Exportación de datos mejorada

### Prioridad Baja
- [ ] Tests con Jest
- [ ] Storybook para componentes
- [ ] Modo claro (light theme)
- [ ] Internacionalización (i18n)

## 🐛 Troubleshooting

### Error: "Cannot find module..."
```bash
npm install
```

### Estilos de Tailwind no se aplican
```bash
# Reiniciar servidor
Ctrl+C
npm start
```

### Puerto 3000 en uso
```bash
# Cambiar puerto
PORT=3001 npm start
```

## 📚 Recursos

- [Documentación de React](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [React Router](https://reactrouter.com)

## 💡 Tips Pro

1. **Hot Module Replacement**: Los cambios se reflejan automáticamente sin recargar
2. **CSS Classes**: Usa `className` en lugar de `class` en JSX
3. **Imports**: Los imports absolutos desde `src/` funcionan out-of-the-box
4. **Console**: Usa `console.log()` sin miedo, se eliminan en producción

---

**Happy Coding! 🚀**
