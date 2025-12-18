# 📚 Ejemplos de Uso - Labortrovilo UI

## 🎯 Casos de Uso Comunes

### 1. Crear un Nuevo Componente con Card

```jsx
import React from 'react';

const MyComponent = () => {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-dark-text mb-4">
        Mi Componente
      </h2>
      <p className="text-gray-400">
        Contenido del componente...
      </p>
    </div>
  );
};

export default MyComponent;
```

### 2. Usar Custom Hooks

```jsx
import React from 'react';
import { useToast, useResponsive } from '../hooks/useCustomHooks';

const ExampleComponent = () => {
  const { addToast } = useToast();
  const { isMobile } = useResponsive();

  const handleClick = () => {
    addToast('¡Operación exitosa!', 'success', 3000);
  };

  return (
    <div>
      <p>{isMobile ? 'Vista móvil' : 'Vista desktop'}</p>
      <button onClick={handleClick} className="btn-primary">
        Mostrar Toast
      </button>
    </div>
  );
};
```

### 3. Fetch de Datos con Servicio

```jsx
import React, { useState, useEffect } from 'react';
import { jobService } from '../services/api';
import { CardSkeleton } from '../components/UIComponents';

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await jobService.getAll();
        setJobs(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map(i => <CardSkeleton key={i} />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {jobs.map(job => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
};
```

### 4. Filtros con Debounce

```jsx
import React, { useState } from 'react';
import { useDebounce } from '../hooks/useCustomHooks';

const SearchComponent = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearch) {
      // Realizar búsqueda
      console.log('Buscando:', debouncedSearch);
    }
  }, [debouncedSearch]);

  return (
    <input
      type="text"
      placeholder="Buscar..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      className="input w-full"
    />
  );
};
```

### 5. Modal con Estado

```jsx
import React from 'react';
import { useModal } from '../hooks/useCustomHooks';
import { Modal } from '../components/UIComponents';

const ModalExample = () => {
  const { isOpen, open, close } = useModal();

  return (
    <>
      <button onClick={open} className="btn-primary">
        Abrir Modal
      </button>

      <Modal
        isOpen={isOpen}
        onClose={close}
        title="Mi Modal"
        footer={
          <div className="flex justify-end space-x-3">
            <button onClick={close} className="btn-secondary">
              Cancelar
            </button>
            <button onClick={close} className="btn-primary">
              Confirmar
            </button>
          </div>
        }
      >
        <p className="text-gray-400">
          Contenido del modal...
        </p>
      </Modal>
    </>
  );
};
```

### 6. Gestión de Favoritos

```jsx
import React from 'react';
import { useFavorites } from '../hooks/useCustomHooks';

const FavoriteButton = ({ job }) => {
  const { isFavorite, toggleFavorite } = useFavorites('job-favorites');

  return (
    <button
      onClick={() => toggleFavorite(job)}
      className={`p-2 rounded-lg transition-all ${
        isFavorite(job.id)
          ? 'bg-red-500/20 text-red-400'
          : 'bg-dark-bg text-gray-400 hover:text-red-400'
      }`}
    >
      <svg className="w-6 h-6" fill={isFavorite(job.id) ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    </button>
  );
};
```

### 7. Exportar Datos

```jsx
import React from 'react';
import { exportService } from '../services/api';
import { helpers } from '../utils/constants';

const ExportButton = ({ data }) => {
  const handleExportCSV = async () => {
    try {
      const csv = convertToCSV(data);
      helpers.downloadFile(csv, 'data.csv', 'text/csv');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleExportJSON = () => {
    const json = JSON.stringify(data, null, 2);
    helpers.downloadFile(json, 'data.json', 'application/json');
  };

  const convertToCSV = (arr) => {
    const headers = Object.keys(arr[0]).join(',');
    const rows = arr.map(obj => Object.values(obj).join(','));
    return [headers, ...rows].join('\n');
  };

  return (
    <div className="flex space-x-3">
      <button onClick={handleExportCSV} className="btn-secondary">
        Exportar CSV
      </button>
      <button onClick={handleExportJSON} className="btn-primary">
        Exportar JSON
      </button>
    </div>
  );
};
```

### 8. Crear Gráfico con Recharts

```jsx
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { chartConfig } from '../utils/constants';

const ChartExample = ({ data }) => {
  return (
    <div className="card">
      <h2 className="text-xl font-bold text-dark-text mb-6">
        Ejemplo de Gráfico
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid {...chartConfig.gridStyle} />
          <XAxis dataKey="name" {...chartConfig.axisStyle} />
          <YAxis {...chartConfig.axisStyle} />
          <Tooltip contentStyle={chartConfig.tooltipStyle} />
          <Bar 
            dataKey="value" 
            fill={chartConfig.colors.primary} 
            radius={[8, 8, 0, 0]} 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### 9. Sistema de Notificaciones

```jsx
import React, { useState } from 'react';
import { Toast } from '../components/UIComponents';

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    
    setTimeout(() => {
      removeNotification(id);
    }, 3000);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div>
      <div className="fixed top-4 right-4 space-y-2 z-50">
        {notifications.map(notif => (
          <Toast
            key={notif.id}
            message={notif.message}
            type={notif.type}
            onClose={() => removeNotification(notif.id)}
          />
        ))}
      </div>

      <div className="space-x-2">
        <button 
          onClick={() => addNotification('Éxito!', 'success')}
          className="btn-primary"
        >
          Success
        </button>
        <button 
          onClick={() => addNotification('Error!', 'error')}
          className="btn-primary"
        >
          Error
        </button>
      </div>
    </div>
  );
};
```

### 10. Paginación

```jsx
import React, { useState, useEffect } from 'react';
import { jobService } from '../services/api';

const PaginatedList = () => {
  const [jobs, setJobs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJobs(page);
  }, [page]);

  const fetchJobs = async (pageNum) => {
    setLoading(true);
    try {
      const response = await jobService.getAll({ 
        page: pageNum, 
        limit: 10 
      });
      setJobs(response.data);
      setTotalPages(response.totalPages);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Lista */}
      <div className="space-y-6">
        {jobs.map(job => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>

      {/* Paginación */}
      <div className="flex justify-center items-center space-x-2 mt-8">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="btn-secondary"
        >
          Anterior
        </button>
        
        <span className="text-dark-text">
          Página {page} de {totalPages}
        </span>
        
        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          className="btn-secondary"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
};
```

### 11. Formulario con Validación

```jsx
import React, { useState } from 'react';
import { validators } from '../utils/constants';

const FormExample = () => {
  const [formData, setFormData] = useState({
    email: '',
    url: '',
    name: '',
  });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};

    if (!validators.notEmpty(formData.name)) {
      newErrors.name = 'El nombre es requerido';
    }

    if (!validators.email(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!validators.url(formData.url)) {
      newErrors.url = 'URL inválida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      console.log('Form válido:', formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-4">
      <div>
        <label className="block text-sm font-medium text-dark-text mb-2">
          Nombre
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={`input w-full ${errors.name ? 'border-red-500' : ''}`}
        />
        {errors.name && (
          <p className="text-red-400 text-sm mt-1">{errors.name}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-dark-text mb-2">
          Email
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className={`input w-full ${errors.email ? 'border-red-500' : ''}`}
        />
        {errors.email && (
          <p className="text-red-400 text-sm mt-1">{errors.email}</p>
        )}
      </div>

      <button type="submit" className="btn-primary w-full">
        Enviar
      </button>
    </form>
  );
};
```

### 12. Copiar al Portapapeles

```jsx
import React from 'react';
import { useClipboard } from '../hooks/useCustomHooks';

const CopyButton = ({ text }) => {
  const { copied, copyToClipboard } = useClipboard();

  return (
    <button
      onClick={() => copyToClipboard(text)}
      className="btn-secondary flex items-center space-x-2"
    >
      {copied ? (
        <>
          <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>¡Copiado!</span>
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span>Copiar</span>
        </>
      )}
    </button>
  );
};
```

## 🎨 Patrones de Diseño Comunes

### Estado Loading + Error + Data

```jsx
const DataComponent = () => {
  const { data, loading, error } = useFetch('/api/endpoint');

  if (loading) return <Spinner />;
  if (error) return <EmptyState title="Error" description={error} />;
  if (!data) return <EmptyState title="Sin datos" />;

  return <div>{/* Renderizar data */}</div>;
};
```

### Layout de Dos Columnas

```jsx
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
  <aside className="lg:col-span-1">
    {/* Sidebar */}
  </aside>
  <main className="lg:col-span-3">
    {/* Contenido principal */}
  </main>
</div>
```

### Card con Hover

```jsx
<div className="card hover:scale-[1.02] cursor-pointer">
  {/* Contenido */}
</div>
```

---

**Para más ejemplos, consulta el código fuente de los componentes existentes.**
