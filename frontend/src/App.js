/**
 * Main Application Component
 * DayBookKeeper v2.0 by WarryWorks
 */

import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import './styles/App.css';
import './styles/GlobalComponents.css';

// V2 Main App
import MainApp from './pages/v2/MainApp';

/**
 * Main App Component - Simple, no authentication
 */
function App() {
  return (
    <LanguageProvider>
      <Router>
        <div className="App">
          <MainApp />
        </div>
      </Router>
    </LanguageProvider>
  );
}

export default App;
