/**
 * Professional Dashboard for BookKeep
 * Day-by-day accounting with balance carry-forward
 */

import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

const Dashboard = ({ onLogout }) => {
  const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0]);
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddEntry, setShowAddEntry] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    description: '',
    debit_amount: '',
    credit_amount: '',
    reference: '',
    transactionType: 'debit' // debit or credit
  });

  const username = localStorage.getItem('username') || 'Admin';

  useEffect(() => {
    loadPage(currentDate);
  }, [currentDate]);

  const loadPage = async (date) => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://127.0.0.1:5000/api/daybook/pages/${date}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPage(data);
      } else if (response.status === 401) {
        // Token expired
        onLogout();
      } else {
        setError('Failed to load daybook page');
      }
    } catch (err) {
      setError('Connection error. Please ensure the server is running.');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEntry = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const token = localStorage.getItem('access_token');

      const payload = {
        description: formData.description,
        debit_amount: formData.transactionType === 'debit' ? parseFloat(formData.debit_amount || 0) : 0,
        credit_amount: formData.transactionType === 'credit' ? parseFloat(formData.credit_amount || 0) : 0,
        reference: formData.reference || null
      };

      const response = await fetch(`http://127.0.0.1:5000/api/daybook/pages/${currentDate}/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        // Reload page
        await loadPage(currentDate);

        // Reset form
        setFormData({
          description: '',
          debit_amount: '',
          credit_amount: '',
          reference: '',
          transactionType: 'debit'
        });
        setShowAddEntry(false);
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to add entry');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
      console.error('Add entry error:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    onLogout();
  };

  const changeDate = (days) => {
    const date = new Date(currentDate);
    date.setDate(date.getDate() + days);
    setCurrentDate(date.toISOString().split('T')[0]);
  };

  const formatAmount = (amount) => {
    return parseFloat(amount).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo-section">
            <svg className="header-logo" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <div>
              <h1 className="app-title">BookKeep</h1>
              <p className="app-subtitle">by WarryWorks</p>
            </div>
          </div>
        </div>

        <div className="header-right">
          <div className="user-info">
            <svg className="user-icon" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
            <span>{username}</span>
          </div>
          <button onClick={handleLogout} className="logout-button">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
            </svg>
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Date Navigation */}
        <div className="date-section">
          <button onClick={() => changeDate(-1)} className="date-nav-button">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Previous Day
          </button>

          <div className="current-date">
            <h2>{formatDate(currentDate)}</h2>
            <input
              type="date"
              value={currentDate}
              onChange={(e) => setCurrentDate(e.target.value)}
              className="date-picker"
            />
          </div>

          <button onClick={() => changeDate(1)} className="date-nav-button">
            Next Day
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        {loading ? (
          <div className="loading-state">
            <div className="spinner-large"></div>
            <p>Loading daybook page...</p>
          </div>
        ) : page ? (
          <>
            {/* Balance Cards */}
            <div className="balance-cards">
              <div className="balance-card opening">
                <div className="card-icon">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="card-content">
                  <h3>Opening Balance</h3>
                  <p className="amount">₹ {formatAmount(page.opening_balance)}</p>
                </div>
              </div>

              <div className="balance-card closing">
                <div className="card-icon">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="card-content">
                  <h3>Closing Balance</h3>
                  <p className="amount">₹ {formatAmount(page.closing_balance)}</p>
                </div>
              </div>

              <div className="balance-card entries">
                <div className="card-icon">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="card-content">
                  <h3>Total Entries</h3>
                  <p className="amount">{page.entries.length}</p>
                </div>
              </div>
            </div>

            {/* Entries Section */}
            <div className="entries-section">
              <div className="section-header">
                <h3>
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                  </svg>
                  Entries
                </h3>
                <button onClick={() => setShowAddEntry(!showAddEntry)} className="add-entry-button">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                  Add Entry
                </button>
              </div>

              {showAddEntry && (
                <form onSubmit={handleAddEntry} className="add-entry-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label>Description *</label>
                      <input
                        type="text"
                        value={formData.description}
                        onChange={(e) => setFormData({...formData, description: e.target.value})}
                        placeholder="Enter description"
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label>Type *</label>
                      <select
                        value={formData.transactionType}
                        onChange={(e) => setFormData({...formData, transactionType: e.target.value})}
                      >
                        <option value="debit">Debit (Money In)</option>
                        <option value="credit">Credit (Money Out)</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Amount *</label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.transactionType === 'debit' ? formData.debit_amount : formData.credit_amount}
                        onChange={(e) => setFormData({
                          ...formData,
                          debit_amount: formData.transactionType === 'debit' ? e.target.value : '',
                          credit_amount: formData.transactionType === 'credit' ? e.target.value : ''
                        })}
                        placeholder="0.00"
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label>Reference</label>
                      <input
                        type="text"
                        value={formData.reference}
                        onChange={(e) => setFormData({...formData, reference: e.target.value})}
                        placeholder="Receipt/voucher number"
                      />
                    </div>
                  </div>

                  <div className="form-actions">
                    <button type="button" onClick={() => setShowAddEntry(false)} className="cancel-button">
                      Cancel
                    </button>
                    <button type="submit" className="submit-button">
                      Add Entry
                    </button>
                  </div>
                </form>
              )}

              {page.entries.length > 0 ? (
                <div className="entries-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Entry No.</th>
                        <th>Description</th>
                        <th>Reference</th>
                        <th className="amount-col">Debit</th>
                        <th className="amount-col">Credit</th>
                        <th className="amount-col">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {page.entries.map((entry) => (
                        <tr key={entry.id}>
                          <td className="entry-number">{entry.entry_number}</td>
                          <td>{entry.description}</td>
                          <td className="reference">{entry.reference || '-'}</td>
                          <td className="amount-col debit">
                            {parseFloat(entry.debit_amount) > 0 ? `₹ ${formatAmount(entry.debit_amount)}` : '-'}
                          </td>
                          <td className="amount-col credit">
                            {parseFloat(entry.credit_amount) > 0 ? `₹ ${formatAmount(entry.credit_amount)}` : '-'}
                          </td>
                          <td className="amount-col balance">₹ {formatAmount(entry.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h4>No Entries Yet</h4>
                  <p>Click "Add Entry" to create your first entry for this date</p>
                </div>
              )}
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
};

export default Dashboard;
