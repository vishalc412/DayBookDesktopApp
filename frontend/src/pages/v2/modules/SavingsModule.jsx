/**
 * Savings & Investments Module
 * Manage FD, RD, PPF, Mutual Funds, and other savings accounts
 */

import React, { useState } from 'react';
import '../../../styles/Modules.css';

const SavingsModule = () => {
  const [view, setView] = useState('dashboard');

  return (
    <div className="module-content">
      <div className="module-header">
        <h2>💰 Savings & Investments</h2>
        <p>Manage your savings accounts, fixed deposits, and investments</p>
      </div>

      <div className="module-actions">
        <button className="btn-primary">
          ➕ Add Savings Account
        </button>
        <button className="btn-secondary">
          📊 View Reports
        </button>
      </div>

      <div className="placeholder-message">
        <div className="placeholder-icon">💰</div>
        <h3>Savings Module</h3>
        <p>Track your savings accounts including:</p>
        <ul>
          <li>Fixed Deposits (FD)</li>
          <li>Recurring Deposits (RD)</li>
          <li>Public Provident Fund (PPF)</li>
          <li>National Savings Certificate (NSC)</li>
          <li>Mutual Funds & SIP</li>
          <li>Sukanya Samriddhi, NPS, and more</li>
        </ul>
        <p className="coming-soon">🚧 UI Implementation in progress...</p>
      </div>
    </div>
  );
};

export default SavingsModule;
