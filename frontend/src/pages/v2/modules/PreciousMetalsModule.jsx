/**
 * Precious Metals Portfolio Module
 * Track gold, silver, and other precious metals investments
 */

import React from 'react';
import '../../../styles/Modules.css';

const PreciousMetalsModule = () => {
  return (
    <div className="module-content">
      <div className="module-header">
        <h2>🥇 Precious Metals Portfolio</h2>
        <p>Track your gold, silver, and precious metals investments</p>
      </div>

      <div className="module-actions">
        <button className="btn-primary">
          ➕ Add Transaction
        </button>
        <button className="btn-secondary">
          💰 Indian Gold Calculator
        </button>
        <button className="btn-secondary">
          📊 Portfolio Value
        </button>
      </div>

      <div className="placeholder-message">
        <div className="placeholder-icon">🥇</div>
        <h3>Precious Metals Portfolio</h3>
        <p>Manage your precious metals investments:</p>
        <ul>
          <li><strong>Gold:</strong> Jewelry, Coins, Bars, SGБ, Digital Gold</li>
          <li><strong>Silver:</strong> Coins, Bars, Jewelry</li>
          <li><strong>Indian Market:</strong> GST @ 3%, Hallmark charges</li>
          <li><strong>International Bullion:</strong> Import duty @ 10.75%</li>
          <li><strong>SGB:</strong> Sovereign Gold Bonds tracking</li>
          <li><strong>Portfolio Analytics:</strong> P/L tracking, current valuation</li>
        </ul>
        <p className="coming-soon">🚧 UI Implementation in progress...</p>
      </div>
    </div>
  );
};

export default PreciousMetalsModule;
