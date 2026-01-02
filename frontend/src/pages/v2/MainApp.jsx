/**
 * Main App Container
 * DayBookKeeper v2.0 - Tab Navigation and Module Container
 */

import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';
import '../../styles/MainApp.css';

// Import module components
import DaybookModule from './modules/DaybookModule';
import SavingsModule from './modules/SavingsModule';
import PreciousMetalsModule from './modules/PreciousMetalsModule';
import ExpensesModule from './modules/ExpensesModule';
import ReportsModule from './modules/ReportsModule';

const MainApp = () => {
  const [activeTab, setActiveTab] = useState('daybook');
  const { language, toggleLanguage } = useLanguage();
  const { username, lockApp, logout } = useAuth();

  const tabs = [
    { id: 'daybook', label: 'Daybook', icon: '📚' },
    { id: 'savings', label: 'Savings', icon: '💰' },
    { id: 'precious-metals', label: 'Precious Metals', icon: '🥇' },
    { id: 'expenses', label: 'Expenses', icon: '💳' },
    { id: 'reports', label: 'Reports', icon: '📊' }
  ];

  const renderModule = () => {
    switch (activeTab) {
      case 'daybook':
        return <DaybookModule />;
      case 'savings':
        return <SavingsModule />;
      case 'precious-metals':
        return <PreciousMetalsModule />;
      case 'expenses':
        return <ExpensesModule />;
      case 'reports':
        return <ReportsModule />;
      default:
        return <DaybookModule />;
    }
  };

  return (
    <div className="main-app">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="app-title">
          <span className="app-icon">📚</span>
          <div>
            <h1>DayBookKeeper v2.0</h1>
            <p>by WarryWorks</p>
          </div>
        </div>
        <div className="top-bar-actions">
          {username && <span className="username-display">👤 {username}</span>}
          <button
            onClick={toggleLanguage}
            className="icon-button"
            title="Switch Language"
          >
            <span>🌐</span>
            {language === 'en' ? 'हिन्दी' : 'English'}
          </button>
          <button
            onClick={lockApp}
            className="icon-button lock-button"
            title="Lock Application"
          >
            🔒 Lock
          </button>
          <button
            onClick={logout}
            className="icon-button logout-button"
            title="Logout"
          >
            🚪 Logout
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Module Content */}
      <div className="module-container">
        {renderModule()}
      </div>
    </div>
  );
};

export default MainApp;
