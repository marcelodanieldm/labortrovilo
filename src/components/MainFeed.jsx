import React, { useState, useEffect } from 'react';
import JobCard from './JobCard';

const MainFeed = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [jobs, setJobs] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    techStack: [],
    modality: '',
    salaryMin: '',
    location: '',
  });

  // Simulación de carga de datos
  useEffect(() => {
    setTimeout(() => {
      setJobs(mockJobs);
      setIsLoading(false);
    }, 1500);
  }, []);

  const techOptions = ['React', 'Python', 'Java', 'Node.js', 'TypeScript', 'Docker', 'AWS', 'PostgreSQL'];
  const modalityOptions = ['Remoto', 'Híbrido', 'Presencial'];

  const toggleTechFilter = (tech) => {
    setFilters(prev => ({
      ...prev,
      techStack: prev.techStack.includes(tech)
        ? prev.techStack.filter(t => t !== tech)
        : [...prev.techStack, tech]
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      techStack: [],
      modality: '',
      salaryMin: '',
      location: '',
    });
  };

  const filteredJobs = jobs.filter(job => {
    if (filters.search && !job.title.toLowerCase().includes(filters.search.toLowerCase()) &&
        !job.company.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    if (filters.techStack.length > 0 && !filters.techStack.some(tech => job.techStack.includes(tech))) {
      return false;
    }
    if (filters.modality && job.modality !== filters.modality) {
      return false;
    }
    if (filters.location && !job.location.toLowerCase().includes(filters.location.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar de Filtros */}
      <aside className="lg:col-span-1 space-y-6">
        <div className="card sticky top-24">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-dark-text flex items-center">
              <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filtros
            </h2>
            <button
              onClick={clearFilters}
              className="text-sm text-primary-400 hover:text-primary-300 font-medium"
            >
              Limpiar
            </button>
          </div>

          {/* Búsqueda */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-dark-text mb-2">Buscar</label>
            <input
              type="text"
              placeholder="Título o empresa..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="input w-full"
            />
          </div>

          {/* Tech Stack */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-dark-text mb-3">Tech Stack</label>
            <div className="flex flex-wrap gap-2">
              {techOptions.map((tech) => (
                <button
                  key={tech}
                  onClick={() => toggleTechFilter(tech)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    filters.techStack.includes(tech)
                      ? 'bg-primary-600 text-white'
                      : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                  }`}
                >
                  {tech}
                </button>
              ))}
            </div>
          </div>

          {/* Modalidad */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-dark-text mb-3">Modalidad</label>
            <div className="space-y-2">
              {modalityOptions.map((mod) => (
                <label key={mod} className="flex items-center cursor-pointer group">
                  <input
                    type="radio"
                    name="modality"
                    checked={filters.modality === mod}
                    onChange={() => setFilters({ ...filters, modality: mod })}
                    className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-400 group-hover:text-dark-text transition-colors">
                    {mod}
                  </span>
                </label>
              ))}
              <label className="flex items-center cursor-pointer group">
                <input
                  type="radio"
                  name="modality"
                  checked={filters.modality === ''}
                  onChange={() => setFilters({ ...filters, modality: '' })}
                  className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-400 group-hover:text-dark-text transition-colors">
                  Todas
                </span>
              </label>
            </div>
          </div>

          {/* Ubicación */}
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">Ubicación</label>
            <input
              type="text"
              placeholder="Ciudad, país..."
              value={filters.location}
              onChange={(e) => setFilters({ ...filters, location: e.target.value })}
              className="input w-full"
            />
          </div>
        </div>
      </aside>

      {/* Listado de Empleos */}
      <main className="lg:col-span-3 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-dark-text">
            Ofertas de Empleo
            <span className="text-primary-500 ml-3">
              {isLoading ? '...' : `(${filteredJobs.length})`}
            </span>
          </h1>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Ordenar por:</span>
            <select className="input text-sm py-2">
              <option>Más recientes</option>
              <option>Salario alto</option>
              <option>Relevancia</option>
            </select>
          </div>
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-6">
            {[1, 2, 3, 4].map((i) => (
              <JobCard key={i} isLoading={true} />
            ))}
          </div>
        ) : (
          <>
            {/* No Results */}
            {filteredJobs.length === 0 ? (
              <div className="card text-center py-12">
                <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-xl font-bold text-dark-text mb-2">No se encontraron ofertas</h3>
                <p className="text-gray-400 mb-4">Intenta ajustar tus filtros de búsqueda</p>
                <button onClick={clearFilters} className="btn-primary">
                  Limpiar Filtros
                </button>
              </div>
            ) : (
              /* Job Cards */
              <div className="space-y-6">
                {filteredJobs.map((job, index) => (
                  <JobCard key={index} job={job} />
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

// Mock data
const mockJobs = [
  {
    title: 'Senior Full Stack Developer',
    company: 'TechCorp SA',
    location: 'Buenos Aires, Argentina',
    modality: 'Remoto',
    techStack: ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker', 'AWS'],
    salaryRange: '$150k - $180k USD',
    description: 'Buscamos un desarrollador full stack con experiencia en arquitecturas modernas y cloud computing. Trabajarás en proyectos innovadores con tecnologías de vanguardia.',
    postedDate: 'Hace 1 día',
    url: '#',
  },
  {
    title: 'Python Backend Engineer',
    company: 'DataFlow Inc',
    location: 'Madrid, España',
    modality: 'Híbrido',
    techStack: ['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker'],
    salaryRange: '€60k - €80k',
    description: 'Únete a nuestro equipo para desarrollar APIs escalables y sistemas de procesamiento de datos en tiempo real.',
    postedDate: 'Hace 2 días',
    url: '#',
  },
  {
    title: 'React Native Developer',
    company: 'MobileFirst',
    location: 'Ciudad de México, México',
    modality: 'Remoto',
    techStack: ['React Native', 'TypeScript', 'Redux', 'Firebase'],
    salaryRange: '$80k - $100k USD',
    description: 'Desarrolla aplicaciones móviles innovadoras para iOS y Android. Experiencia con animaciones y performance es un plus.',
    postedDate: 'Hace 3 días',
    url: '#',
  },
  {
    title: 'DevOps Engineer',
    company: 'CloudSolutions',
    location: 'Santiago, Chile',
    modality: 'Híbrido',
    techStack: ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'Python'],
    salaryRange: '$90k - $120k USD',
    description: 'Gestiona infraestructura cloud y automatiza procesos de deployment. Experiencia con CI/CD es esencial.',
    postedDate: 'Hace 5 días',
    url: '#',
  },
  {
    title: 'Java Backend Developer',
    company: 'Enterprise Systems',
    location: 'Bogotá, Colombia',
    modality: 'Presencial',
    techStack: ['Java', 'Spring Boot', 'Microservices', 'PostgreSQL', 'Kafka'],
    salaryRange: '$70k - $90k USD',
    description: 'Desarrolla microservicios escalables para aplicaciones enterprise. Conocimientos en arquitectura hexagonal preferidos.',
    postedDate: 'Hace 1 semana',
    url: '#',
  },
];

export default MainFeed;
