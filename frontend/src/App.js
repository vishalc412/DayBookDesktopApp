/**
 * Main Application Component
 * DayBookKeeper v2.0 by WarryWorks
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import './styles/App.css';

// V1 Pages (Existing)
import Dashboard from './pages/Dashboard';
import ReportsPage from './pages/ReportsPage';

// V2 Auth Pages
import MasterPasswordSetup from './pages/v2/MasterPasswordSetup';
import LoginScreen from './pages/v2/LoginScreen';
import LockScreen from './pages/v2/LockScreen';

// V2 Main App (will be created)
import MainApp from './pages/v2/MainApp';

/**
 * Protected Route Component
 * Redirects to login/setup if not authenticated
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLocked, isSetup } = useAuth();

  // Still checking setup status
  if (isSetup === null) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Needs setup
  if (isSetup === false) {
    return <Navigate to="/setup" replace />;
  }

  // Locked
  if (isLocked) {
    return <Navigate to="/locked" replace />;
  }

  // Not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Authenticated and unlocked
  return children;
};

/**
 * App Router
 * Handles all routing logic
 */
const AppRouter = () => {
  const { isAuthenticated, isLocked, isSetup } = useAuth();

  return (
    <Routes>
      {/* Setup Route */}
      <Route
        path="/setup"
        element={
          isSetup === false ? (
            <MasterPasswordSetup />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      {/* Login Route */}
      <Route
        path="/login"
        element={
          !isAuthenticated && isSetup ? (
            <LoginScreen />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      {/* Lock Screen Route */}
      <Route
        path="/locked"
        element={
          isLocked ? (
            <LockScreen />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      {/* Protected Routes - V2 Main App */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainApp />
          </ProtectedRoute>
        }
      />

      {/* Legacy V1 Routes (can be removed or kept for compatibility) */}
      <Route
        path="/v1/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/v1/reports"
        element={
          <ProtectedRoute>
            <ReportsPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

/**
 * Main App Component
 */
function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <AppRouter />
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
