/**
 * Summary Component
 * Displays summary statistics of daybook entries
 */

import React from 'react';

const Summary = ({ summary }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  if (!summary) {
    return null;
  }

  return (
    <div className="summary-section">
      <div className="summary-card">
        <h3>Total Entries</h3>
        <div className="value">{summary.total_entries || 0}</div>
      </div>

      <div className="summary-card debit">
        <h3>Total Debit</h3>
        <div className="value">{formatCurrency(summary.total_debit || 0)}</div>
      </div>

      <div className="summary-card credit">
        <h3>Total Credit</h3>
        <div className="value">{formatCurrency(summary.total_credit || 0)}</div>
      </div>

      <div className="summary-card balance">
        <h3>Current Balance</h3>
        <div className="value">{formatCurrency(summary.current_balance || 0)}</div>
      </div>
    </div>
  );
};

export default Summary;
