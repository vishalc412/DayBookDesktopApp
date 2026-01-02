/**
 * Reports Module - COMPLETE UI
 * Generate financial reports and export to Excel
 */

import React, { useState } from 'react';
import { reportsAPI } from '../../../services/api/reportsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import '../../../styles/Reports.css';

const ReportsModule = () => {
  const [reportType, setReportType] = useState('savings');
  const [timePeriod, setTimePeriod] = useState('current_month');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reportData, setReportData] = useState(null);

  const reportTypes = [
    { id: 'savings', label: 'Savings Summary', icon: '💰', endpoint: 'savings' },
    { id: 'metals', label: 'Precious Metals Portfolio', icon: '🥇', endpoint: 'precious-metals' },
    { id: 'expenses', label: 'Expense Summary', icon: '💳', endpoint: 'expenses' },
    { id: 'budgets', label: 'Budget Analysis', icon: '📊', endpoint: 'budgets' }
  ];

  const timePeriods = [
    { id: 'current_month', label: 'Current Month' },
    { id: 'last_month', label: 'Last Month' },
    { id: 'current_quarter', label: 'Current Quarter' },
    { id: 'last_quarter', label: 'Last Quarter' },
    { id: 'current_year', label: 'Current Year' },
    { id: 'last_year', label: 'Last Year' },
    { id: 'custom', label: 'Custom Date Range' },
    { id: 'all_time', label: 'All Time' }
  ];

  const generateReport = async () => {
    setError(null);
    setLoading(true);

    try {
      const payload = {
        time_period: timePeriod
      };

      if (timePeriod === 'custom') {
        if (!customStartDate || !customEndDate) {
          setError('Please select both start and end dates for custom range');
          setLoading(false);
          return;
        }
        payload.start_date = customStartDate;
        payload.end_date = customEndDate;
      }

      let data;
      const selectedReport = reportTypes.find(r => r.id === reportType);

      switch (reportType) {
        case 'savings':
          data = await reportsAPI.generateSavingsSummary(payload);
          break;
        case 'metals':
          data = await reportsAPI.generateMetalsSummary(payload);
          break;
        case 'expenses':
          data = await reportsAPI.generateExpensesSummary(payload);
          break;
        case 'budgets':
          data = await reportsAPI.generateBudgetAnalysis(payload);
          break;
        default:
          throw new Error('Unknown report type');
      }

      setReportData(data);
    } catch (err) {
      setError(formatErrorMessage(err));
      setReportData(null);
    } finally {
      setLoading(false);
    }
  };

  const exportToExcel = async () => {
    setError(null);
    setLoading(true);

    try {
      const payload = {
        time_period: timePeriod
      };

      if (timePeriod === 'custom') {
        if (!customStartDate || !customEndDate) {
          setError('Please select both start and end dates for custom range');
          setLoading(false);
          return;
        }
        payload.start_date = customStartDate;
        payload.end_date = customEndDate;
      }

      const blob = await reportsAPI.exportToExcel(reportType, payload);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `${reportType}_report_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const renderReportData = () => {
    if (!reportData) return null;

    return (
      <div className="report-display">
        <div className="report-header">
          <h3>{reportTypes.find(r => r.id === reportType)?.label}</h3>
          <p className="report-period">
            Period: {timePeriods.find(p => p.id === timePeriod)?.label}
          </p>
        </div>

        <div className="report-data">
          <pre>{JSON.stringify(reportData, null, 2)}</pre>
        </div>
      </div>
    );
  };

  return (
    <div className="module-content reports-module">
      <div className="module-header">
        <h2>📊 Reports & Analytics</h2>
        <p>Generate comprehensive financial reports and export to Excel</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="reports-config-section">
        {/* Report Type Selection */}
        <div className="config-group">
          <label>Report Type</label>
          <div className="report-type-grid">
            {reportTypes.map(type => (
              <button
                key={type.id}
                className={`report-type-card ${reportType === type.id ? 'active' : ''}`}
                onClick={() => setReportType(type.id)}
              >
                <span className="report-icon">{type.icon}</span>
                <span className="report-label">{type.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Time Period Selection */}
        <div className="config-group">
          <label>Time Period</label>
          <div className="time-period-grid">
            {timePeriods.map(period => (
              <button
                key={period.id}
                className={`period-button ${timePeriod === period.id ? 'active' : ''}`}
                onClick={() => setTimePeriod(period.id)}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom Date Range */}
        {timePeriod === 'custom' && (
          <div className="config-group custom-date-range">
            <div className="date-input-group">
              <label>Start Date</label>
              <input
                type="date"
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
              />
            </div>
            <div className="date-input-group">
              <label>End Date</label>
              <input
                type="date"
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="report-actions">
          <button
            className="btn-primary"
            onClick={generateReport}
            disabled={loading}
          >
            {loading ? '⏳ Generating...' : '📄 Generate Report'}
          </button>
          <button
            className="btn-secondary"
            onClick={exportToExcel}
            disabled={loading}
          >
            {loading ? '⏳ Exporting...' : '📥 Export to Excel'}
          </button>
        </div>
      </div>

      {/* Report Display */}
      {renderReportData()}

      {!reportData && !loading && !error && (
        <div className="placeholder-message">
          <div className="placeholder-icon">📊</div>
          <h3>Ready to Generate Reports</h3>
          <p>Select a report type and time period, then click "Generate Report"</p>
        </div>
      )}
    </div>
  );
};

export default ReportsModule;
