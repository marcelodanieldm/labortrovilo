# 🏗️ Arquitectura de UI - Labortrovilo

## 📋 Resumen Ejecutivo

Sistema de interfaz moderna para plataforma de scraping de ofertas laborales, construido con React y Tailwind CSS. Implementa navegación dinámica basada en roles, dark mode por defecto, y sistema de componentes reutilizables.

## 🎯 Características Principales

### ✅ Implementado
- ✨ Sistema de navegación dinámica por roles (CANDIDATO, HR_PRO, ADMIN, SUPERUSER)
- 🌙 Dark mode activado por defecto con toggle
- 📱 100% Responsive con breakpoints de Tailwind
- 🎨 Sistema de diseño coherente con componentes reutilizables
- ⏳ Estados de carga con skeletons animados
- 📊 Dashboard con gráficos interactivos (Recharts)
- 🔍 Sistema de filtros avanzados
- 💾 Exportación de datos (CSV/JSON)
- 🎭 Animaciones y transiciones suaves

## 📁 Estructura del Proyecto

```
labortrovilo/
├── public/
│   └── index.html                 # HTML base con dark mode
│
├── src/
│   ├── App.js                     # Router principal + lógica de roles
│   ├── index.js                   # Entry point
│   ├── index.css                  # Estilos globales + Tailwind
│   │
│   ├── components/                # Componentes React
│   │   ├── Navbar.jsx            # ✅ Navegación dinámica
│   │   ├── JobCard.jsx           # ✅ Tarjeta de oferta
│   │   ├── MainFeed.jsx          # ✅ Feed principal (CANDIDATO)
│   │   ├── IntelligenceDashboard.jsx  # ✅ Dashboard (HR_PRO)
│   │   ├── B2BPortal.jsx         # ✅ Portal B2B (HR_PRO)
│   │   ├── AdminPanel.jsx        # ✅ Panel admin
│   │   └── UIComponents.jsx      # ✅ Componentes reutilizables
│   │
│   ├── hooks/                     # Custom React Hooks
│   │   └── useCustomHooks.js     # ✅ useToast, useResponsive, etc.
│   │
│   ├── services/                  # Servicios de API
│   │   └── api.js                # ✅ Cliente HTTP + servicios
│   │
│   └── utils/                     # Utilidades
│       └── constants.js          # ✅ Constantes + helpers
│
├── tailwind.config.js            # ✅ Configuración Tailwind
├── postcss.config.js             # ✅ PostCSS
├── package.json                  # ✅ Dependencias
│
└── Documentación/
    ├── FRONTEND_README.md        # ✅ Documentación completa
    └── QUICKSTART_UI.md          # ✅ Guía rápida
```

## 🎨 Sistema de Componentes

### Componentes por Rol

#### 1. CANDIDATO (Vista por Defecto)
- **MainFeed**: Layout de dos columnas (filtros + resultados)
- **JobCard**: Tarjeta de oferta con tech stack colorido
- **Filtros**: Búsqueda, tech stack, modalidad, ubicación

#### 2. HR_PRO (Profesionales de RRHH)
- **B2BPortal**: Portal completo con tabs
- **IntelligenceDashboard**: Dashboard con 4 gráficos:
  - Bar Chart: Top 5 tecnologías
  - Bar Chart horizontal: Hiring velocity
  - Line Chart: Tendencias salariales
  - Pie Chart: Distribución de modalidades
- **Export**: Botones CSV/JSON

#### 3. ADMIN / SUPERUSER
- **AdminPanel**: Tabla densa de scrapers
- **Stats Cards**: 4 métricas principales
- **Controles**: Ejecutar, detener, ver logs
- **Filtros**: Por nombre, URL y estado

### Componentes Reutilizables

```javascript
// UIComponents.jsx
- Skeleton           // Loading skeleton
- CardSkeleton       // Skeleton para cards
- Badge              // Etiquetas de colores
- EmptyState         // Estado vacío
- Spinner            // Loading spinner
- StatsCard          // Tarjeta de estadísticas
- Modal              // Modal genérico
- Toast              // Notificación toast
```

## 🎨 Sistema de Diseño

### Paleta de Colores

```css
/* Principales */
primary: #0ea5e9 (Cyan/Blue)
success: #10b981 (Green)
warning: #f59e0b (Orange)
error: #ef4444 (Red)

/* Dark Theme */
dark-bg: #0f172a      /* Slate 900 - Background */
dark-surface: #1e293b /* Slate 800 - Cards */
dark-border: #334155  /* Slate 700 - Bordes */
dark-text: #e2e8f0    /* Slate 200 - Texto */
```

### Clases CSS Personalizadas

```css
/* Botones */
.btn-primary       /* Botón principal con hover */
.btn-secondary     /* Botón secundario outline */

/* Contenedores */
.card              /* Card con sombra y animación */
.input             /* Input con focus ring */

/* Loading */
.skeleton          /* Skeleton con pulse animation */
```

### Animaciones

```css
/* Definidas en tailwind.config.js */
.animate-fade-in       /* 0.3s ease-in-out */
.animate-slide-up      /* 0.3s ease-out */
.animate-pulse-soft    /* 2s infinite */
```

## 🔌 Integración con Backend

### Servicios API

```javascript
// services/api.js
jobService          // CRUD de ofertas
scraperService      // Gestión de scrapers
analyticsService    // Métricas y analytics
exportService       // Exportación CSV/JSON
authService         // Autenticación (futuro)
```

### Ejemplo de Uso

```javascript
import { jobService } from './services/api';

// Obtener ofertas
const jobs = await jobService.getAll({ 
  modality: 'Remoto',
  techStack: ['React', 'Node.js']
});

// Buscar
const results = await jobService.search('Senior Developer');
```

## 🪝 Custom Hooks

```javascript
// hooks/useCustomHooks.js
useToast()          // Notificaciones
useResponsive()     // Detección de tamaño de pantalla
useInfiniteScroll() // Scroll infinito
useDebounce()       // Debounce de valores
useFavorites()      // Gestión de favoritos
useFetch()          // Fetch con estados
useTheme()          // Dark/Light mode
useClipboard()      // Copiar al portapapeles
useModal()          // Gestión de modales
```

## 🛣️ Rutas y Navegación

### Rutas Principales

```javascript
/ → Redirige según rol del usuario
/jobs → MainFeed (todos los roles)
/dashboard → B2BPortal (HR_PRO, ADMIN, SUPERUSER)
/admin → AdminPanel (ADMIN, SUPERUSER)
```

### Protección de Rutas

Las rutas están protegidas mediante el componente `Navigate` de React Router, redirigiendo a usuarios sin permisos.

## 📊 Visualización de Datos

### Recharts Configuration

```javascript
// utils/constants.js → chartConfig
tooltipStyle      // Estilo consistente
colors            // Paleta de colores
gridStyle         // Grid con dash
axisStyle         // Ejes con color
```

### Tipos de Gráficos

- **BarChart**: Tecnologías, Hiring Velocity
- **LineChart**: Tendencias temporales
- **PieChart**: Distribución porcentual

## 🚀 Performance

### Optimizaciones Implementadas

- ✅ Lazy loading de imágenes
- ✅ Memoización de callbacks con useCallback
- ✅ Estados de carga progresivos
- ✅ Transiciones CSS en lugar de JS

### Futuras Optimizaciones

- [ ] Code splitting con React.lazy
- [ ] Virtualización de listas largas
- [ ] Service Worker para PWA
- [ ] Optimización de bundle size

## 🔐 Seguridad

### Implementado

- ✅ Validación de URLs
- ✅ Sanitización de inputs
- ✅ Protección de rutas por rol

### Por Implementar

- [ ] JWT Authentication
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Content Security Policy

## 📱 Responsive Design

### Breakpoints

```javascript
sm: 640px   // Móviles grandes
md: 768px   // Tablets
lg: 1024px  // Laptops
xl: 1280px  // Desktops
2xl: 1536px // Pantallas grandes
```

### Testing

- ✅ iPhone SE (375px)
- ✅ iPad (768px)
- ✅ MacBook (1440px)
- ✅ Desktop 4K (2560px)

## 🧪 Testing (Futuro)

### Stack Recomendado

```javascript
Jest              // Test runner
React Testing Library  // Testing de componentes
Cypress           // E2E tests
MSW               // Mock Service Worker
```

## 📦 Dependencias Clave

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "recharts": "^2.10.0",
  "axios": "^1.6.0",
  "tailwindcss": "^3.3.0"
}
```

## 🔄 Estado Global (Futuro)

### Opciones Evaluadas

- **Context API**: Para estado simple
- **Zustand**: Ligero y moderno
- **Redux Toolkit**: Para apps complejas
- **Jotai**: Atomic state management

### Recomendación

Iniciar con Context API y migrar a Zustand si crece la complejidad.

## 🚀 Deployment

### Build

```bash
npm run build
# Output: build/
```

### Opciones de Hosting

- **Vercel**: Deploy automático con Git
- **Netlify**: CI/CD integrado
- **AWS S3 + CloudFront**: Escalable
- **Docker**: Containerización

## 📈 Roadmap

### Fase 1 (Actual) ✅
- [x] Componentes base
- [x] Navegación por roles
- [x] Dark mode
- [x] Responsive design

### Fase 2 (Próxima)
- [ ] Integración con FastAPI
- [ ] Autenticación JWT
- [ ] WebSockets para updates
- [ ] Testing completo

### Fase 3 (Futuro)
- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push
- [ ] Internacionalización (i18n)
- [ ] Analytics avanzados

## 👥 Equipo y Roles

### Frontend Developer
- Implementación de componentes
- Integración con API
- Testing y QA

### UX/UI Designer
- Sistema de diseño
- Wireframes y prototipos
- Validación con usuarios

### Backend Developer
- API REST con FastAPI
- WebSockets
- Optimización de queries

## 📚 Recursos y Referencias

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org)
- [React Router](https://reactrouter.com)
- [Labortrovilo Figma](# Agregar link)

## 📞 Soporte

Para preguntas o issues:
- GitHub Issues: [Crear Issue](# Agregar link)
- Documentación: Ver `FRONTEND_README.md`
- Guía rápida: Ver `QUICKSTART_UI.md`

---

**Última actualización**: Diciembre 2024  
**Versión**: 2.0.0  
**Estado**: ✅ Producción Ready
