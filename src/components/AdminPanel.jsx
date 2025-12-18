import React, { useState, useEffect } from 'react';

const AdminPanel = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [scrapers, setScrapers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    setTimeout(() => {
      setScrapers(mockScrapers);
      setIsLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      'Activo': 'bg-green-500/20 text-green-400 border-green-500/30',
      'Error': 'bg-red-500/20 text-red-400 border-red-500/30',
      'Pausado': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      'Mantenimiento': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getStatusIcon = (status) => {
    if (status === 'Activo') {
      return (
        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (status === 'Error') {
      return (
        <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (status === 'Pausado') {
      return (
        <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    );
  };

  const filteredScrapers = scrapers.filter(scraper => {
    const matchesSearch = scraper.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scraper.url.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || scraper.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: scrapers.length,
    active: scrapers.filter(s => s.status === 'Activo').length,
    error: scrapers.filter(s => s.status === 'Error').length,
    paused: scrapers.filter(s => s.status === 'Pausado').length,
  };

  const runScraper = (id) => {
    alert(`Ejecutando scraper ${id}... (Implementar con API real)`);
  };

  const stopScraper = (id) => {
    alert(`Deteniendo scraper ${id}... (Implementar con API real)`);
  };

  const viewLogs = (id) => {
    alert(`Ver logs del scraper ${id}... (Implementar con API real)`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-dark-text">Panel de Administración</h1>
          <p className="text-gray-400 mt-2">Gestión y monitoreo de scrapers</p>
        </div>
        
        <button className="btn-primary flex items-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span>Nuevo Scraper</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Total Scrapers</p>
              <p className="text-3xl font-bold text-dark-text mt-2">{stats.total}</p>
            </div>
            <div className="bg-primary-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Activos</p>
              <p className="text-3xl font-bold text-green-400 mt-2">{stats.active}</p>
            </div>
            <div className="bg-green-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Con Errores</p>
              <p className="text-3xl font-bold text-red-400 mt-2">{stats.error}</p>
            </div>
            <div className="bg-red-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Pausados</p>
              <p className="text-3xl font-bold text-yellow-400 mt-2">{stats.paused}</p>
            </div>
            <div className="bg-yellow-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Buscar por nombre o URL..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input w-full"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                statusFilter === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setStatusFilter('Activo')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                statusFilter === 'Activo'
                  ? 'bg-green-600 text-white'
                  : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
              }`}
            >
              Activos
            </button>
            <button
              onClick={() => setStatusFilter('Error')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                statusFilter === 'Error'
                  ? 'bg-red-600 text-white'
                  : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
              }`}
            >
              Errores
            </button>
          </div>
        </div>
      </div>

      {/* Scrapers Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton h-16"></div>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-dark-bg">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Scraper
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    URL
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Última Corrida
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Registros
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border">
                {filteredScrapers.map((scraper) => (
                  <tr key={scraper.id} className="hover:bg-dark-bg transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(scraper.status)}
                        <div>
                          <div className="font-medium text-dark-text">{scraper.name}</div>
                          <div className="text-sm text-gray-500">{scraper.type}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <a
                        href={scraper.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-400 hover:text-primary-300 text-sm truncate max-w-xs block"
                      >
                        {scraper.url}
                      </a>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(scraper.status)}`}>
                        {scraper.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-400">{scraper.lastRun}</div>
                      <div className="text-xs text-gray-500">{scraper.duration}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-dark-text">{scraper.records}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {scraper.status === 'Activo' || scraper.status === 'Pausado' ? (
                          <button
                            onClick={() => runScraper(scraper.id)}
                            className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-all"
                            title="Ejecutar"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                        ) : null}
                        
                        <button
                          onClick={() => stopScraper(scraper.id)}
                          className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all"
                          title="Detener"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                          </svg>
                        </button>
                        
                        <button
                          onClick={() => viewLogs(scraper.id)}
                          className="p-2 rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-all"
                          title="Ver logs"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {!isLoading && filteredScrapers.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-xl font-bold text-dark-text mb-2">No se encontraron scrapers</h3>
            <p className="text-gray-400">Intenta ajustar los filtros de búsqueda</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Mock data
const mockScrapers = [
  {
    id: 1,
    name: 'LinkedIn Jobs',
    type: 'Job Board',
    url: 'https://www.linkedin.com/jobs',
    status: 'Activo',
    lastRun: 'Hace 5 min',
    duration: '2m 15s',
    records: '1,234',
  },
  {
    id: 2,
    name: 'Indeed Argentina',
    type: 'Job Board',
    url: 'https://ar.indeed.com',
    status: 'Activo',
    lastRun: 'Hace 12 min',
    duration: '1m 45s',
    records: '892',
  },
  {
    id: 3,
    name: 'Computrabajo',
    type: 'Job Board',
    url: 'https://www.computrabajo.com.ar',
    status: 'Error',
    lastRun: 'Hace 2 horas',
    duration: 'N/A',
    records: '0',
  },
  {
    id: 4,
    name: 'ZonaJobs',
    type: 'Job Board',
    url: 'https://www.zonajobs.com.ar',
    status: 'Activo',
    lastRun: 'Hace 8 min',
    duration: '3m 22s',
    records: '567',
  },
  {
    id: 5,
    name: 'Bumeran',
    type: 'Job Board',
    url: 'https://www.bumeran.com.ar',
    status: 'Pausado',
    lastRun: 'Hace 1 día',
    duration: '2m 50s',
    records: '1,045',
  },
  {
    id: 6,
    name: 'Get On Board',
    type: 'Tech-Focused',
    url: 'https://www.getonbrd.com',
    status: 'Activo',
    lastRun: 'Hace 15 min',
    duration: '1m 30s',
    records: '345',
  },
  {
    id: 7,
    name: 'Torre',
    type: 'Tech-Focused',
    url: 'https://torre.ai',
    status: 'Mantenimiento',
    lastRun: 'Hace 3 días',
    duration: 'N/A',
    records: '0',
  },
  {
    id: 8,
    name: 'Empleos Clarin',
    type: 'Job Board',
    url: 'https://empleos.clarin.com',
    status: 'Activo',
    lastRun: 'Hace 20 min',
    duration: '2m 05s',
    records: '423',
  },
];

export default AdminPanel;
