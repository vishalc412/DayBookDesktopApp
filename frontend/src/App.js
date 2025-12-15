/**
 * Main Application Component
 * DayBookKeeper by WarryWorks v1.1
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/App.css';
import Dashboard from './pages/Dashboard';
import ReportsPage from './pages/ReportsPage';

function App() {
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    // Login flow is removed, so we just clear data.
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard onLogout={handleLogout} />} />
          <Route path="/reports" element={<ReportsPage onLogout={handleLogout} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
