/**
 * Main App Container
 * DayBookKeeper v2.0 - Tab Navigation and Module Container
 */

import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
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
        <button
          onClick={toggleLanguage}
          className="language-toggle"
          title="Switch Language"
        >
          <span style={{ marginRight: '6px' }}>🌐</span>
          {language === 'en' ? 'हिन्दी' : 'English'}
        </button>
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
