import { API_BASE_URL, API_ENDPOINTS } from '../utils/constants';

// Cliente HTTP base
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || `HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }
}

const apiClient = new ApiClient();

// Servicios de Jobs
export const jobService = {
  // Obtener todas las ofertas
  getAll: (filters = {}) => {
    return apiClient.get(API_ENDPOINTS.JOBS, filters);
  },

  // Obtener detalle de una oferta
  getById: (id) => {
    return apiClient.get(API_ENDPOINTS.JOB_DETAIL(id));
  },

  // Buscar ofertas
  search: (query, filters = {}) => {
    return apiClient.post(API_ENDPOINTS.SEARCH_JOBS, { query, ...filters });
  },

  // Crear nueva oferta (admin)
  create: (jobData) => {
    return apiClient.post(API_ENDPOINTS.JOBS, jobData);
  },

  // Actualizar oferta (admin)
  update: (id, jobData) => {
    return apiClient.put(API_ENDPOINTS.JOB_DETAIL(id), jobData);
  },

  // Eliminar oferta (admin)
  delete: (id) => {
    return apiClient.delete(API_ENDPOINTS.JOB_DETAIL(id));
  },
};

// Servicios de Scrapers
export const scraperService = {
  // Obtener todos los scrapers
  getAll: () => {
    return apiClient.get(API_ENDPOINTS.SCRAPERS);
  },

  // Obtener detalle de un scraper
  getById: (id) => {
    return apiClient.get(API_ENDPOINTS.SCRAPER_DETAIL(id));
  },

  // Ejecutar scraper
  run: (id) => {
    return apiClient.post(API_ENDPOINTS.RUN_SCRAPER(id));
  },

  // Detener scraper
  stop: (id) => {
    return apiClient.post(API_ENDPOINTS.STOP_SCRAPER(id));
  },

  // Obtener logs
  getLogs: (id, limit = 100) => {
    return apiClient.get(API_ENDPOINTS.SCRAPER_LOGS(id), { limit });
  },

  // Crear nuevo scraper
  create: (scraperData) => {
    return apiClient.post(API_ENDPOINTS.SCRAPERS, scraperData);
  },

  // Actualizar scraper
  update: (id, scraperData) => {
    return apiClient.put(API_ENDPOINTS.SCRAPER_DETAIL(id), scraperData);
  },

  // Eliminar scraper
  delete: (id) => {
    return apiClient.delete(API_ENDPOINTS.SCRAPER_DETAIL(id));
  },
};

// Servicios de Analytics
export const analyticsService = {
  // Obtener tendencias de tecnologías
  getTechTrends: (timeRange = '30d') => {
    return apiClient.get(API_ENDPOINTS.TECH_TRENDS, { timeRange });
  },

  // Obtener hiring velocity
  getHiringVelocity: (timeRange = '30d') => {
    return apiClient.get(API_ENDPOINTS.HIRING_VELOCITY, { timeRange });
  },

  // Obtener tendencias salariales
  getSalaryTrends: (timeRange = '30d') => {
    return apiClient.get(API_ENDPOINTS.SALARY_TRENDS, { timeRange });
  },

  // Obtener todas las métricas
  getAllMetrics: async (timeRange = '30d') => {
    try {
      const [techTrends, hiringVelocity, salaryTrends] = await Promise.all([
        analyticsService.getTechTrends(timeRange),
        analyticsService.getHiringVelocity(timeRange),
        analyticsService.getSalaryTrends(timeRange),
      ]);

      return {
        techTrends,
        hiringVelocity,
        salaryTrends,
      };
    } catch (error) {
      console.error('Error fetching metrics:', error);
      throw error;
    }
  },
};

// Servicios de Exportación
export const exportService = {
  // Exportar a CSV
  toCSV: async (data, filename = 'export.csv') => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.EXPORT_CSV, data);
      
      // Descargar archivo
      const blob = new Blob([response], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Export CSV error:', error);
      throw error;
    }
  },

  // Exportar a JSON
  toJSON: async (data, filename = 'export.json') => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.EXPORT_JSON, data);
      
      // Descargar archivo
      const blob = new Blob([JSON.stringify(response, null, 2)], { 
        type: 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Export JSON error:', error);
      throw error;
    }
  },
};

// Servicios de Autenticación (futuro)
export const authService = {
  login: async (email, password) => {
    return apiClient.post('/api/auth/login', { email, password });
  },

  logout: async () => {
    return apiClient.post('/api/auth/logout');
  },

  register: async (userData) => {
    return apiClient.post('/api/auth/register', userData);
  },

  getCurrentUser: async () => {
    return apiClient.get('/api/auth/me');
  },

  updateProfile: async (userData) => {
    return apiClient.put('/api/auth/profile', userData);
  },
};

// Mock data helper (para desarrollo sin backend)
export const useMockData = () => {
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  return {
    getJobs: async () => {
      await delay(500);
      return {
        data: [
          {
            id: 1,
            title: 'Senior Full Stack Developer',
            company: 'TechCorp SA',
            location: 'Buenos Aires, Argentina',
            modality: 'Remoto',
            techStack: ['React', 'Node.js', 'TypeScript', 'PostgreSQL'],
            salaryRange: '$150k - $180k USD',
            description: 'Buscamos un desarrollador full stack...',
            postedDate: new Date(Date.now() - 86400000).toISOString(),
            url: '#',
          },
          // ... más ofertas
        ],
        total: 1847,
      };
    },

    getScrapers: async () => {
      await delay(300);
      return {
        data: [
          {
            id: 1,
            name: 'LinkedIn Jobs',
            type: 'Job Board',
            url: 'https://www.linkedin.com/jobs',
            status: 'Activo',
            lastRun: new Date(Date.now() - 300000).toISOString(),
            duration: 135,
            records: 1234,
          },
          // ... más scrapers
        ],
      };
    },

    getTechTrends: async () => {
      await delay(400);
      return [
        { name: 'React', count: 245, percentage: 28 },
        { name: 'Python', count: 198, percentage: 23 },
        { name: 'Node.js', count: 175, percentage: 20 },
        { name: 'TypeScript', count: 142, percentage: 16 },
        { name: 'AWS', count: 98, percentage: 13 },
      ];
    },
  };
};

export default apiClient;
