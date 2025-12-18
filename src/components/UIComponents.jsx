import React from 'react';

// Loading Skeleton Component
export const Skeleton = ({ width = 'w-full', height = 'h-4', className = '' }) => {
  return <div className={`skeleton ${width} ${height} ${className}`}></div>;
};

// Card Skeleton
export const CardSkeleton = () => {
  return (
    <div className="card animate-pulse">
      <div className="space-y-4">
        <Skeleton height="h-6" width="w-3/4" />
        <Skeleton height="h-4" width="w-1/2" />
        <div className="flex gap-2">
          <Skeleton height="h-8" width="w-20" />
          <Skeleton height="h-8" width="w-20" />
          <Skeleton height="h-8" width="w-20" />
        </div>
        <Skeleton height="h-20" width="w-full" />
        <div className="flex justify-between">
          <Skeleton height="h-6" width="w-24" />
          <Skeleton height="h-6" width="w-20" />
        </div>
      </div>
    </div>
  );
};

// Badge Component
export const Badge = ({ children, color = 'primary', className = '' }) => {
  const colors = {
    primary: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
    success: 'bg-green-500/20 text-green-400 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    error: 'bg-red-500/20 text-red-400 border-red-500/30',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${colors[color]} ${className}`}>
      {children}
    </span>
  );
};

// Empty State Component
export const EmptyState = ({ icon, title, description, action }) => {
  return (
    <div className="card text-center py-12 animate-fade-in">
      <div className="mx-auto mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-dark-text mb-2">{title}</h3>
      {description && <p className="text-gray-400 mb-4">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
};

// Loading Spinner
export const Spinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`inline-block ${sizes[size]} ${className}`}>
      <svg
        className="animate-spin text-primary-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>
  );
};

// Stats Card Component
export const StatsCard = ({ title, value, change, icon, color = 'primary' }) => {
  const colors = {
    primary: 'bg-primary-500/20 text-primary-400',
    purple: 'bg-purple-500/20 text-purple-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    cyan: 'bg-cyan-500/20 text-cyan-400',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-dark-text mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-2 ${change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>{icon}</div>
      </div>
    </div>
  );
};

// Modal Component
export const Modal = ({ isOpen, onClose, title, children, footer }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      ></div>

      {/* Modal Content */}
      <div className="relative bg-dark-surface border border-dark-border rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-border">
          <h2 className="text-2xl font-bold text-dark-text">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-dark-bg transition-colors"
          >
            <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">{children}</div>

        {/* Footer */}
        {footer && <div className="p-6 border-t border-dark-border">{footer}</div>}
      </div>
    </div>
  );
};

// Toast Notification Component
export const Toast = ({ message, type = 'info', onClose }) => {
  const types = {
    success: 'bg-green-500/20 border-green-500/30 text-green-400',
    error: 'bg-red-500/20 border-red-500/30 text-red-400',
    warning: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400',
    info: 'bg-blue-500/20 border-blue-500/30 text-blue-400',
  };

  const icons = {
    success: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    error: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    warning: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    info: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  };

  return (
    <div className={`flex items-center space-x-3 p-4 rounded-lg border ${types[type]} animate-slide-up`}>
      {icons[type]}
      <p className="flex-1 font-medium">{message}</p>
      <button onClick={onClose} className="p-1 hover:bg-white/10 rounded transition-colors">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};
