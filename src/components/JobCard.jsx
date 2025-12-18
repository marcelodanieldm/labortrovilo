import React from 'react';

const JobCard = ({ job, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-4">
          <div className="skeleton h-6 w-3/4"></div>
          <div className="skeleton h-4 w-1/2"></div>
          <div className="flex gap-2">
            <div className="skeleton h-8 w-20"></div>
            <div className="skeleton h-8 w-20"></div>
            <div className="skeleton h-8 w-20"></div>
          </div>
          <div className="skeleton h-20 w-full"></div>
          <div className="flex justify-between">
            <div className="skeleton h-6 w-24"></div>
            <div className="skeleton h-6 w-20"></div>
          </div>
        </div>
      </div>
    );
  }

  const {
    title,
    company,
    location,
    modality,
    techStack = [],
    salaryRange,
    description,
    postedDate,
    url,
  } = job;

  const getModalityColor = (mod) => {
    const colors = {
      'Remoto': 'bg-green-500/20 text-green-400 border-green-500/30',
      'Híbrido': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'Presencial': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    };
    return colors[mod] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getTechStackColor = (index) => {
    const colors = [
      'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      'bg-pink-500/20 text-pink-400 border-pink-500/30',
      'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="card hover:scale-[1.02] animate-slide-up group cursor-pointer">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-dark-text group-hover:text-primary-400 transition-colors">
              {title}
            </h3>
            <div className="flex items-center space-x-2 mt-2 text-gray-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span className="font-medium">{company}</span>
              <span className="text-dark-border">•</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{location}</span>
            </div>
          </div>
          
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getModalityColor(modality)}`}>
            {modality}
          </span>
        </div>

        {/* Tech Stack */}
        {techStack && techStack.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {techStack.slice(0, 6).map((tech, index) => (
              <span
                key={index}
                className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getTechStackColor(index)}`}
              >
                {tech}
              </span>
            ))}
            {techStack.length > 6 && (
              <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-dark-bg text-gray-400 border border-dark-border">
                +{techStack.length - 6} más
              </span>
            )}
          </div>
        )}

        {/* Description */}
        <p className="text-gray-400 text-sm line-clamp-3">
          {description}
        </p>

        {/* Footer */}
        <div className="flex justify-between items-center pt-4 border-t border-dark-border">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-lg font-bold text-primary-400">
              {salaryRange || 'A convenir'}
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              {postedDate || 'Hace 2 días'}
            </span>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-sm py-2 px-4"
              onClick={(e) => e.stopPropagation()}
            >
              Ver Oferta
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
