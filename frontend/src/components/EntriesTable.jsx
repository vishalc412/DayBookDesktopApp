/**
 * Entries Table Component
 * Displays all daybook entries in a table format
 */

import React from 'react';
import { format } from 'date-fns';

const EntriesTable = ({ entries, onEdit, onDelete }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd/MM/yyyy');
    } catch (error) {
      return dateString;
    }
  };

  if (!entries || entries.length === 0) {
    return (
      <div className="entries-section">
        <h2>Daybook Entries</h2>
        <p style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No entries found. Add your first entry above.
        </p>
      </div>
    );
  }

  return (
    <div className="entries-section">
      <h2>Daybook Entries ({entries.length})</h2>
      <div style={{ overflowX: 'auto' }}>
        <table className="entries-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Description</th>
              <th>Category</th>
              <th>Reference</th>
              <th className="number">Debit</th>
              <th className="number">Credit</th>
              <th className="number">Balance</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.entry_id}>
                <td>{entry.entry_id}</td>
                <td>{formatDate(entry.date)}</td>
                <td>{entry.description}</td>
                <td>{entry.category}</td>
                <td>{entry.reference}</td>
                <td className="number debit">
                  {entry.debit > 0 ? formatCurrency(entry.debit) : '-'}
                </td>
                <td className="number credit">
                  {entry.credit > 0 ? formatCurrency(entry.credit) : '-'}
                </td>
                <td className="number balance">
                  {formatCurrency(entry.balance)}
                </td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-small btn-secondary"
                      onClick={() => onEdit(entry)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-small btn-danger"
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this entry?')) {
                          onDelete(entry.entry_id);
                        }
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EntriesTable;
