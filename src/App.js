import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import MainFeed from './components/MainFeed';
import B2BPortal from './components/B2BPortal';
import AdminPanel from './components/AdminPanel';

// Hook personalizado para gestionar el rol del usuario
const useUserRole = () => {
  const [userRole, setUserRole] = useState(() => {
    return localStorage.getItem('userRole') || 'CANDIDATO';
  });

  useEffect(() => {
    localStorage.setItem('userRole', userRole);
  }, [userRole]);

  return [userRole, setUserRole];
};

function App() {
  const [userRole, setUserRole] = useUserRole();
  const [darkMode, setDarkMode] = useState(true); // Dark mode por defecto

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <Router>
      <div className="min-h-screen bg-dark-bg dark:bg-dark-bg">
        <Navbar 
          userRole={userRole} 
          setUserRole={setUserRole}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />
        
        <main className="container mx-auto px-4 py-8 animate-fade-in">
          <Routes>
            {/* Ruta principal según rol */}
            <Route 
              path="/" 
              element={
                userRole === 'CANDIDATO' ? (
                  <MainFeed />
                ) : userRole === 'HR_PRO' ? (
                  <B2BPortal />
                ) : (
                  <AdminPanel />
                )
              } 
            />
            
            {/* Rutas específicas */}
            <Route path="/jobs" element={<MainFeed />} />
            <Route 
              path="/dashboard" 
              element={
                userRole === 'HR_PRO' || userRole === 'ADMIN' || userRole === 'SUPERUSER' ? (
                  <B2BPortal />
                ) : (
                  <Navigate to="/" replace />
                )
              } 
            />
            <Route 
              path="/admin" 
              element={
                userRole === 'ADMIN' || userRole === 'SUPERUSER' ? (
                  <AdminPanel />
                ) : (
                  <Navigate to="/" replace />
                )
              } 
            />
            
            {/* Ruta 404 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
