import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = ({ userRole, setUserRole, darkMode, setDarkMode }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const roles = [
    { id: 'CANDIDATO', label: 'Candidato', icon: '👤' },
    { id: 'HR_PRO', label: 'HR Professional', icon: '💼' },
    { id: 'ADMIN', label: 'Admin', icon: '⚙️' },
    { id: 'SUPERUSER', label: 'Superuser', icon: '👑' },
  ];

  const getNavigationLinks = () => {
    const links = [
      { path: '/jobs', label: 'Empleos', roles: ['CANDIDATO', 'HR_PRO', 'ADMIN', 'SUPERUSER'] },
      { path: '/dashboard', label: 'Dashboard', roles: ['HR_PRO', 'ADMIN', 'SUPERUSER'] },
      { path: '/admin', label: 'Panel Admin', roles: ['ADMIN', 'SUPERUSER'] },
    ];

    return links.filter(link => link.roles.includes(userRole));
  };

  const navigationLinks = getNavigationLinks();

  return (
    <nav className="bg-dark-surface border-b border-dark-border sticky top-0 z-50 backdrop-blur-lg bg-opacity-90">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="font-bold text-xl text-dark-text group-hover:text-primary-400 transition-colors">
              Labortrovilo
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigationLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  location.pathname === link.path
                    ? 'bg-primary-600 text-white'
                    : 'text-dark-text hover:bg-dark-bg'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right Section */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Role Selector */}
            <div className="relative group">
              <button className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-dark-bg border border-dark-border hover:border-primary-500 transition-all">
                <span className="text-xl">
                  {roles.find(r => r.id === userRole)?.icon}
                </span>
                <span className="text-sm font-medium text-dark-text">
                  {roles.find(r => r.id === userRole)?.label}
                </span>
                <svg className="w-4 h-4 text-dark-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Dropdown */}
              <div className="absolute right-0 mt-2 w-48 bg-dark-surface border border-dark-border rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    onClick={() => setUserRole(role.id)}
                    className={`w-full text-left px-4 py-3 hover:bg-dark-bg transition-colors flex items-center space-x-3 ${
                      userRole === role.id ? 'bg-primary-600 text-white' : 'text-dark-text'
                    } ${role === roles[0] ? 'rounded-t-lg' : ''} ${role === roles[roles.length - 1] ? 'rounded-b-lg' : ''}`}
                  >
                    <span className="text-xl">{role.icon}</span>
                    <span className="text-sm font-medium">{role.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg bg-dark-bg border border-dark-border hover:border-primary-500 transition-all"
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-dark-text" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-dark-text hover:bg-dark-bg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-dark-border animate-slide-up">
            <div className="space-y-2">
              {navigationLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`block px-4 py-3 rounded-lg font-medium transition-all ${
                    location.pathname === link.path
                      ? 'bg-primary-600 text-white'
                      : 'text-dark-text hover:bg-dark-bg'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              
              <div className="pt-4 border-t border-dark-border space-y-2">
                <p className="px-4 text-sm text-gray-400 font-medium">Cambiar Rol</p>
                {roles.map((role) => (
                  <button
                    key={role.id}
                    onClick={() => {
                      setUserRole(role.id);
                      setIsMenuOpen(false);
                    }}
                    className={`w-full text-left px-4 py-3 rounded-lg hover:bg-dark-bg transition-colors flex items-center space-x-3 ${
                      userRole === role.id ? 'bg-primary-600 text-white' : 'text-dark-text'
                    }`}
                  >
                    <span className="text-xl">{role.icon}</span>
                    <span className="text-sm font-medium">{role.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
