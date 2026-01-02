/**
 * Main Application Component
 * DayBookKeeper v2.0 by WarryWorks
 */

import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider } from './context/AuthContext';
import './styles/App.css';

// Authentication wrapper and screens
import AuthenticatedApp from './pages/v2/AuthenticatedApp';

/**
 * Main App Component - With Authentication
 */
function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <AuthenticatedApp />
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
