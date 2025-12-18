# Labortrovilo UI - React + Tailwind CSS

## 🎨 Arquitectura de UI

Sistema de interfaz moderno con navegación dinámica basada en roles de usuario y dark mode por defecto.

## 🚀 Instalación y Ejecución

### 1. Instalar Dependencias

```bash
npm install
```

### 2. Ejecutar en Desarrollo

```bash
npm start
```

La aplicación se abrirá en [http://localhost:3000](http://localhost:3000)

### 3. Build para Producción

```bash
npm run build
```

## 👥 Roles de Usuario

La aplicación soporta 4 roles con vistas específicas:

### 1. **CANDIDATO** (Vista por Defecto)
- 🔍 Búsqueda de empleos con filtros avanzados
- 🏷️ Tech Stack destacado con etiquetas de colores
- 💰 Rango salarial y modalidad (Remoto/Híbrido/Presencial)
- 📱 Layout responsive de dos columnas

**Componentes:**
- `JobCard.jsx` - Tarjeta individual de oferta
- `MainFeed.jsx` - Feed principal con filtros laterales

### 2. **HR_PRO** (Profesionales de RRHH)
- 📊 Intelligence Dashboard con gráficos interactivos
- 📈 Top 5 tecnologías más demandadas
- 🚀 Empresas con mayor Hiring Velocity
- 💾 Exportar datasets a CSV/JSON (Modelo Bright Data)

**Componentes:**
- `IntelligenceDashboard.jsx` - Dashboard con Recharts
- `B2BPortal.jsx` - Portal completo para HR

### 3. **ADMIN** / **SUPERUSER**
- ⚙️ Panel de administración de scrapers
- 📋 Tabla densa con estado de scrapers
- ⏱️ Última ejecución y registros procesados
- 🔧 Controles para ejecutar/detener scrapers

**Componentes:**
- `AdminPanel.jsx` - Panel administrativo completo

## 🎨 Características UX/UI

### ✨ Dark Mode
- Activado por defecto (muy valorado en IT)
- Toggle en navbar para cambiar entre temas
- Paleta de colores optimizada para legibilidad

### 📱 100% Responsive
- Sistema de rejillas de Tailwind CSS
- Breakpoints: mobile, tablet, desktop
- Menú hamburguesa en móvil

### 🎭 Animaciones y Transiciones
- **Fade-in**: Animación de entrada suave
- **Slide-up**: Deslizamiento desde abajo
- **Pulse-soft**: Pulsación suave para skeletons
- Transiciones entre vistas de 200ms

### ⏳ Estados de Carga
- Skeletons animados para tarjetas
- Loading states para gráficos
- Feedback visual inmediato

## 📁 Estructura de Archivos

```
src/
├── App.js                          # Router y lógica principal
├── index.js                        # Entry point
├── index.css                       # Estilos globales con Tailwind
└── components/
    ├── Navbar.jsx                  # Navegación dinámica por rol
    ├── JobCard.jsx                 # Tarjeta de oferta (CANDIDATO)
    ├── MainFeed.jsx                # Feed principal (CANDIDATO)
    ├── IntelligenceDashboard.jsx   # Dashboard con gráficos (HR_PRO)
    ├── B2BPortal.jsx               # Portal B2B (HR_PRO)
    └── AdminPanel.jsx              # Panel admin (ADMIN/SUPERUSER)
```

## 🎨 Sistema de Diseño

### Colores Principales
- **Primary**: `#0ea5e9` (Cyan/Blue)
- **Dark BG**: `#0f172a` (Slate 900)
- **Dark Surface**: `#1e293b` (Slate 800)
- **Dark Border**: `#334155` (Slate 700)
- **Dark Text**: `#e2e8f0` (Slate 200)

### Componentes Reutilizables (CSS)
```css
.btn-primary      # Botón primario con gradiente
.btn-secondary    # Botón secundario outline
.card            # Tarjeta base con sombra
.input           # Input con focus ring
.skeleton        # Loading skeleton animado
```

## 📊 Gráficos (Recharts)

La aplicación utiliza **Recharts** para visualización de datos:

- **BarChart**: Top tecnologías y Hiring Velocity
- **LineChart**: Tendencias salariales
- **PieChart**: Distribución de modalidades

## 🔄 Navegación Dinámica

El sistema de navegación se adapta automáticamente según el rol:

| Ruta | CANDIDATO | HR_PRO | ADMIN | SUPERUSER |
|------|-----------|--------|-------|-----------|
| `/jobs` | ✅ | ✅ | ✅ | ✅ |
| `/dashboard` | ❌ | ✅ | ✅ | ✅ |
| `/admin` | ❌ | ❌ | ✅ | ✅ |

## 🎯 Características Técnicas

### Hooks Personalizados
- `useUserRole`: Gestión de rol con localStorage
- Estados de carga asíncronos
- Filtros reactivos con useState

### Optimizaciones
- Lazy loading de componentes (futuro)
- Memoización de cálculos pesados (futuro)
- Debounce en búsquedas (futuro)

## 🔌 Integración con Backend

Para conectar con tu API de Python:

```javascript
// Ejemplo en MainFeed.jsx
useEffect(() => {
  fetch('http://localhost:8000/api/jobs')
    .then(res => res.json())
    .then(data => setJobs(data))
    .catch(err => console.error(err));
}, []);
```

## 📝 Próximos Pasos

1. **Integración con FastAPI**: Conectar componentes con endpoints reales
2. **Autenticación**: Sistema de login/registro
3. **WebSockets**: Updates en tiempo real de scrapers
4. **Testing**: Jest + React Testing Library
5. **Storybook**: Documentación de componentes

## 🛠️ Tecnologías

- ⚛️ React 18.2.0
- 🎨 Tailwind CSS 3.3.0
- 📊 Recharts 2.10.0
- 🛣️ React Router 6.20.0
- 🔄 Axios 1.6.0

## 💡 Tips de Desarrollo

### Cambiar Rol Rápidamente
Usa el dropdown en la navbar para alternar entre roles y ver diferentes vistas.

### Personalizar Colores
Edita `tailwind.config.js` para modificar la paleta de colores.

### Agregar Nuevos Componentes
Crea componentes en `src/components/` y sigue el patrón de diseño establecido.

---

**Desarrollado con ❤️ por el equipo de Labortrovilo**
