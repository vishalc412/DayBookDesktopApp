/**
 * Expenses & Budgeting Module
 * Track expenses and manage budgets
 */

import React from 'react';
import '../../../styles/Modules.css';

const ExpensesModule = () => {
  return (
    <div className="module-content">
      <div className="module-header">
        <h2>💳 Expenses & Budgeting</h2>
        <p>Track your expenses and manage monthly budgets</p>
      </div>

      <div className="module-actions">
        <button className="btn-primary">
          ➕ Add Expense
        </button>
        <button className="btn-secondary">
          💰 Manage Budgets
        </button>
        <button className="btn-secondary">
          📊 View Analytics
        </button>
      </div>

      <div className="placeholder-message">
        <div className="placeholder-icon">💳</div>
        <h3>Expenses & Budgeting</h3>
        <p>Comprehensive expense tracking features:</p>
        <ul>
          <li><strong>18 Categories:</strong> Food, Transport, Healthcare, Education, etc.</li>
          <li><strong>9 Payment Methods:</strong> Cash, UPI, Cards, Net Banking, etc.</li>
          <li><strong>Budget Management:</strong> Set monthly/yearly budgets per category</li>
          <li><strong>Budget Alerts:</strong> Notification at 80% utilization</li>
          <li><strong>Analytics:</strong> Category breakdown, trends, top expenses</li>
          <li><strong>Recurring Expenses:</strong> Track subscriptions and EMIs</li>
        </ul>
        <p className="coming-soon">🚧 UI Implementation in progress...</p>
      </div>
    </div>
  );
};

export default ExpensesModule;
