/**
 * Reports Module
 * Generate financial reports and export to Excel
 */

import React from 'react';
import '../../../styles/Modules.css';

const ReportsModule = () => {
  return (
    <div className="module-content">
      <div className="module-header">
        <h2>📊 Reports & Analytics</h2>
        <p>Generate comprehensive financial reports and export data</p>
      </div>

      <div className="module-actions">
        <button className="btn-primary">
          📄 Generate Report
        </button>
        <button className="btn-secondary">
          📥 Export to Excel
        </button>
      </div>

      <div className="placeholder-message">
        <div className="placeholder-icon">📊</div>
        <h3>Reports & Analytics</h3>
        <p>Available reports:</p>
        <ul>
          <li><strong>Savings Summary:</strong> All accounts, ROI, upcoming maturities</li>
          <li><strong>Precious Metals Portfolio:</strong> Holdings, P/L analysis</li>
          <li><strong>Expense Summary:</strong> Category breakdown, trends</li>
          <li><strong>Budget Analysis:</strong> Utilization, exceeded budgets</li>
          <li><strong>Excel Export:</strong> Multi-sheet workbooks with formatting</li>
          <li><strong>Time Periods:</strong> Monthly, Quarterly, Yearly, Custom</li>
        </ul>
        <p className="coming-soon">🚧 UI Implementation in progress...</p>
      </div>
    </div>
  );
};

export default ReportsModule;
