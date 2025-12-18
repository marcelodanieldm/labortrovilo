import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const IntelligenceDashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  // Mock data para gráficos
  const topTechnologies = [
    { name: 'React', count: 245, percentage: 28 },
    { name: 'Python', count: 198, percentage: 23 },
    { name: 'Node.js', count: 175, percentage: 20 },
    { name: 'TypeScript', count: 142, percentage: 16 },
    { name: 'AWS', count: 98, percentage: 13 },
  ];

  const hiringVelocity = [
    { company: 'TechCorp SA', velocity: 34, openings: 45 },
    { company: 'DataFlow Inc', velocity: 28, openings: 32 },
    { company: 'CloudSolutions', velocity: 25, openings: 28 },
    { company: 'MobileFirst', velocity: 22, openings: 25 },
    { company: 'Enterprise Systems', velocity: 19, openings: 21 },
  ];

  const salaryTrends = [
    { month: 'Jul', avg: 95000, median: 85000 },
    { month: 'Ago', avg: 97000, median: 87000 },
    { month: 'Sep', avg: 99000, median: 89000 },
    { month: 'Oct', avg: 102000, median: 92000 },
    { month: 'Nov', avg: 105000, median: 95000 },
    { month: 'Dic', avg: 108000, median: 98000 },
  ];

  const modalityDistribution = [
    { name: 'Remoto', value: 45, color: '#10b981' },
    { name: 'Híbrido', value: 35, color: '#3b82f6' },
    { name: 'Presencial', value: 20, color: '#f59e0b' },
  ];

  const COLORS = ['#0ea5e9', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card h-64 skeleton"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-dark-text">Intelligence Dashboard</h1>
          <p className="text-gray-400 mt-2">Análisis del mercado laboral en tiempo real</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="input"
        >
          <option value="7d">Últimos 7 días</option>
          <option value="30d">Últimos 30 días</option>
          <option value="90d">Últimos 90 días</option>
          <option value="1y">Último año</option>
        </select>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Total Ofertas</p>
              <p className="text-3xl font-bold text-dark-text mt-2">1,847</p>
              <p className="text-green-400 text-sm mt-2">+12% vs mes anterior</p>
            </div>
            <div className="bg-primary-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Empresas Activas</p>
              <p className="text-3xl font-bold text-dark-text mt-2">342</p>
              <p className="text-green-400 text-sm mt-2">+8% vs mes anterior</p>
            </div>
            <div className="bg-purple-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Salario Promedio</p>
              <p className="text-3xl font-bold text-dark-text mt-2">$108k</p>
              <p className="text-green-400 text-sm mt-2">+5% vs mes anterior</p>
            </div>
            <div className="bg-emerald-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Tech Stack Trends</p>
              <p className="text-3xl font-bold text-dark-text mt-2">127</p>
              <p className="text-blue-400 text-sm mt-2">Tecnologías rastreadas</p>
            </div>
            <div className="bg-cyan-500/20 p-3 rounded-lg">
              <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Tecnologías */}
        <div className="card">
          <h2 className="text-xl font-bold text-dark-text mb-6 flex items-center">
            <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Top 5 Tecnologías Más Demandadas
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topTechnologies}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {topTechnologies.map((tech, index) => (
              <div key={tech.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index] }}
                  ></span>
                  <span className="text-sm text-gray-400">{tech.name}</span>
                </div>
                <span className="text-sm font-semibold text-dark-text">
                  {tech.count} ofertas ({tech.percentage}%)
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Hiring Velocity */}
        <div className="card">
          <h2 className="text-xl font-bold text-dark-text mb-6 flex items-center">
            <svg className="w-5 h-5 mr-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Empresas con Mayor Hiring Velocity
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hiringVelocity} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis dataKey="company" type="category" stroke="#94a3b8" width={120} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="velocity" fill="#10b981" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-4">
            * Hiring Velocity: nuevas posiciones publicadas por semana
          </p>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Salary Trends */}
        <div className="card lg:col-span-2">
          <h2 className="text-xl font-bold text-dark-text mb-6 flex items-center">
            <svg className="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            Tendencia de Salarios (USD)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={salaryTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="avg"
                stroke="#8b5cf6"
                strokeWidth={3}
                name="Promedio"
                dot={{ fill: '#8b5cf6', r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="median"
                stroke="#ec4899"
                strokeWidth={3}
                name="Mediana"
                dot={{ fill: '#ec4899', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Modality Distribution */}
        <div className="card">
          <h2 className="text-xl font-bold text-dark-text mb-6 flex items-center">
            <svg className="w-5 h-5 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </svg>
            Modalidad
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={modalityDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {modalityDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {modalityDistribution.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  ></span>
                  <span className="text-sm text-gray-400">{item.name}</span>
                </div>
                <span className="text-sm font-semibold text-dark-text">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligenceDashboard;
