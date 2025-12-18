import React, { useState } from 'react';
import IntelligenceDashboard from './IntelligenceDashboard';

const B2BPortal = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const exportData = (format) => {
    // Simulación de exportación
    alert(`Exportando datos en formato ${format}... (Implementar con API real)`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-dark-text">Portal B2B - HR Professionals</h1>
          <p className="text-gray-400 mt-2">
            Herramientas avanzadas de inteligencia de mercado laboral
          </p>
        </div>
        
        {/* Export Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => exportData('CSV')}
            className="btn-secondary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Exportar CSV</span>
          </button>
          
          <button
            onClick={() => exportData('JSON')}
            className="btn-primary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span>Exportar JSON</span>
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-dark-border">
        <nav className="flex space-x-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-6 py-3 font-medium transition-all relative ${
              activeTab === 'dashboard'
                ? 'text-primary-400'
                : 'text-gray-400 hover:text-dark-text'
            }`}
          >
            Dashboard
            {activeTab === 'dashboard' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('datasets')}
            className={`px-6 py-3 font-medium transition-all relative ${
              activeTab === 'datasets'
                ? 'text-primary-400'
                : 'text-gray-400 hover:text-dark-text'
            }`}
          >
            Datasets
            {activeTab === 'datasets' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-6 py-3 font-medium transition-all relative ${
              activeTab === 'insights'
                ? 'text-primary-400'
                : 'text-gray-400 hover:text-dark-text'
            }`}
          >
            Insights
            {activeTab === 'insights' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"></div>
            )}
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && <IntelligenceDashboard />}
      
      {activeTab === 'datasets' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-2xl font-bold text-dark-text mb-4">
              Datasets Disponibles
            </h2>
            <p className="text-gray-400 mb-6">
              Accede a conjuntos de datos curados y actualizados del mercado laboral tech.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Dataset Card 1 */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-6 hover:border-primary-500 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-primary-500/20 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <span className="bg-green-500/20 text-green-400 text-xs font-semibold px-3 py-1 rounded-full">
                    Actualizado
                  </span>
                </div>
                <h3 className="text-lg font-bold text-dark-text mb-2">
                  Job Postings - Completo
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  1,847 ofertas con tech stack, salarios, modalidad y más.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Última actualización: Hoy</span>
                  <button className="text-primary-400 hover:text-primary-300 font-medium">
                    Descargar →
                  </button>
                </div>
              </div>

              {/* Dataset Card 2 */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-6 hover:border-primary-500 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-purple-500/20 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <span className="bg-green-500/20 text-green-400 text-xs font-semibold px-3 py-1 rounded-full">
                    Actualizado
                  </span>
                </div>
                <h3 className="text-lg font-bold text-dark-text mb-2">
                  Tech Stack Trends
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  Análisis de 127 tecnologías con métricas de demanda.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Última actualización: Hoy</span>
                  <button className="text-primary-400 hover:text-primary-300 font-medium">
                    Descargar →
                  </button>
                </div>
              </div>

              {/* Dataset Card 3 */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-6 hover:border-primary-500 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-emerald-500/20 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <span className="bg-yellow-500/20 text-yellow-400 text-xs font-semibold px-3 py-1 rounded-full">
                    Semanal
                  </span>
                </div>
                <h3 className="text-lg font-bold text-dark-text mb-2">
                  Salary Benchmarks
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  Rangos salariales por rol, experiencia y ubicación.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Última actualización: Hace 2 días</span>
                  <button className="text-primary-400 hover:text-primary-300 font-medium">
                    Descargar →
                  </button>
                </div>
              </div>

              {/* Dataset Card 4 */}
              <div className="bg-dark-bg border border-dark-border rounded-xl p-6 hover:border-primary-500 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-cyan-500/20 p-3 rounded-lg">
                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <span className="bg-green-500/20 text-green-400 text-xs font-semibold px-3 py-1 rounded-full">
                    Actualizado
                  </span>
                </div>
                <h3 className="text-lg font-bold text-dark-text mb-2">
                  Company Insights
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  342 empresas con hiring velocity y stack tecnológico.
                </p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Última actualización: Hoy</span>
                  <button className="text-primary-400 hover:text-primary-300 font-medium">
                    Descargar →
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Bright Data Integration */}
          <div className="card bg-gradient-to-br from-primary-500/10 to-purple-500/10 border-primary-500/30">
            <div className="flex items-start space-x-4">
              <div className="bg-primary-500/20 p-4 rounded-xl">
                <svg className="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-dark-text mb-2">
                  Modelo Bright Data
                </h3>
                <p className="text-gray-400 mb-4">
                  Accede a scraping enterprise-grade con datos frescos y actualizados en tiempo real.
                  Exporta datasets personalizados según tus necesidades.
                </p>
                <div className="flex flex-wrap gap-3">
                  <button className="btn-primary">
                    Configurar Scraping
                  </button>
                  <button className="btn-secondary">
                    Ver Documentación
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-2xl font-bold text-dark-text mb-4">
              Insights del Mercado
            </h2>
            <div className="space-y-4">
              <div className="bg-dark-bg border-l-4 border-primary-500 p-4 rounded">
                <h3 className="font-bold text-dark-text mb-2">
                  📈 React sigue dominando el mercado frontend
                </h3>
                <p className="text-gray-400 text-sm">
                  Con 245 ofertas activas (+15% vs mes anterior), React se mantiene como la tecnología
                  más demandada. TypeScript aparece en el 58% de las ofertas de React.
                </p>
              </div>
              
              <div className="bg-dark-bg border-l-4 border-emerald-500 p-4 rounded">
                <h3 className="font-bold text-dark-text mb-2">
                  💰 Salarios en alza: +5% promedio
                </h3>
                <p className="text-gray-400 text-sm">
                  El salario promedio para roles tech alcanzó $108k USD, impulsado principalmente
                  por la alta demanda de perfiles con experiencia en cloud (AWS, Azure, GCP).
                </p>
              </div>
              
              <div className="bg-dark-bg border-l-4 border-purple-500 p-4 rounded">
                <h3 className="font-bold text-dark-text mb-2">
                  🏠 Trabajo remoto en el 45% de ofertas
                </h3>
                <p className="text-gray-400 text-sm">
                  El modelo remoto se consolida, especialmente en roles de desarrollo y data science.
                  Las empresas que ofrecen remoto reciben 3x más aplicaciones.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default B2BPortal;
