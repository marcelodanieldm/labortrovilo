// Roles de usuario
export const USER_ROLES = {
  CANDIDATO: 'CANDIDATO',
  HR_PRO: 'HR_PRO',
  ADMIN: 'ADMIN',
  SUPERUSER: 'SUPERUSER',
};

// Estados de scrapers
export const SCRAPER_STATUS = {
  ACTIVO: 'Activo',
  ERROR: 'Error',
  PAUSADO: 'Pausado',
  MANTENIMIENTO: 'Mantenimiento',
};

// Modalidades de trabajo
export const WORK_MODALITY = {
  REMOTO: 'Remoto',
  HIBRIDO: 'Híbrido',
  PRESENCIAL: 'Presencial',
};

// Colores para tech stack
export const TECH_STACK_COLORS = [
  'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'bg-pink-500/20 text-pink-400 border-pink-500/30',
  'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
  'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
];

// API endpoints (configurar según tu backend)
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Jobs
  JOBS: '/api/jobs',
  JOB_DETAIL: (id) => `/api/jobs/${id}`,
  SEARCH_JOBS: '/api/jobs/search',
  
  // Scrapers
  SCRAPERS: '/api/scrapers',
  SCRAPER_DETAIL: (id) => `/api/scrapers/${id}`,
  RUN_SCRAPER: (id) => `/api/scrapers/${id}/run`,
  STOP_SCRAPER: (id) => `/api/scrapers/${id}/stop`,
  SCRAPER_LOGS: (id) => `/api/scrapers/${id}/logs`,
  
  // Analytics
  TECH_TRENDS: '/api/analytics/tech-trends',
  HIRING_VELOCITY: '/api/analytics/hiring-velocity',
  SALARY_TRENDS: '/api/analytics/salary-trends',
  
  // Export
  EXPORT_CSV: '/api/export/csv',
  EXPORT_JSON: '/api/export/json',
};

// Utilidades de formato
export const formatters = {
  // Formatear fecha relativa (ej: "Hace 2 días")
  relativeTime: (date) => {
    const now = new Date();
    const past = new Date(date);
    const diffInSeconds = Math.floor((now - past) / 1000);
    
    if (diffInSeconds < 60) return 'Hace unos segundos';
    if (diffInSeconds < 3600) return `Hace ${Math.floor(diffInSeconds / 60)} min`;
    if (diffInSeconds < 86400) return `Hace ${Math.floor(diffInSeconds / 3600)} horas`;
    if (diffInSeconds < 604800) return `Hace ${Math.floor(diffInSeconds / 86400)} días`;
    return past.toLocaleDateString('es-ES');
  },

  // Formatear número con separadores
  number: (num) => {
    return new Intl.NumberFormat('es-ES').format(num);
  },

  // Formatear moneda
  currency: (amount, currency = 'USD') => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  },

  // Formatear duración (ej: "2m 30s")
  duration: (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  },

  // Truncar texto
  truncate: (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },
};

// Validaciones
export const validators = {
  email: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  url: (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  notEmpty: (value) => {
    return value && value.trim().length > 0;
  },
};

// Helpers
export const helpers = {
  // Generar ID único
  generateId: () => {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  },

  // Agrupar array por key
  groupBy: (array, key) => {
    return array.reduce((result, item) => {
      const groupKey = item[key];
      if (!result[groupKey]) {
        result[groupKey] = [];
      }
      result[groupKey].push(item);
      return result;
    }, {});
  },

  // Filtrar duplicados de array
  unique: (array, key) => {
    if (!key) return [...new Set(array)];
    
    const seen = new Set();
    return array.filter(item => {
      const k = item[key];
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  },

  // Sleep/delay
  sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  // Ordenar array por campo
  sortBy: (array, key, order = 'asc') => {
    return [...array].sort((a, b) => {
      const aVal = a[key];
      const bVal = b[key];
      
      if (order === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
  },

  // Descargar archivo
  downloadFile: (content, filename, type = 'text/plain') => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  // Convertir objeto a query string
  toQueryString: (params) => {
    return Object.keys(params)
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
  },
};

// LocalStorage helpers
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },

  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  },

  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch {
      return false;
    }
  },

  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch {
      return false;
    }
  },
};

// Configuración de gráficos (Recharts)
export const chartConfig = {
  // Estilo común para tooltips
  tooltipStyle: {
    backgroundColor: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '8px',
    color: '#e2e8f0',
  },

  // Colores para gráficos
  colors: {
    primary: '#0ea5e9',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },

  // Grid style
  gridStyle: {
    strokeDasharray: '3 3',
    stroke: '#334155',
  },

  // Axis style
  axisStyle: {
    stroke: '#94a3b8',
  },
};

// Mensajes de error comunes
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Por favor, verifica tu conexión a internet.',
  UNAUTHORIZED: 'No tienes permisos para realizar esta acción.',
  NOT_FOUND: 'El recurso solicitado no existe.',
  SERVER_ERROR: 'Error del servidor. Por favor, intenta más tarde.',
  VALIDATION_ERROR: 'Los datos proporcionados no son válidos.',
  UNKNOWN_ERROR: 'Ha ocurrido un error inesperado.',
};

// Mensajes de éxito
export const SUCCESS_MESSAGES = {
  SAVED: 'Guardado exitosamente',
  DELETED: 'Eliminado exitosamente',
  UPDATED: 'Actualizado exitosamente',
  EXPORTED: 'Exportado exitosamente',
};
