/**
 * Savings & Investments Module - COMPLETE UI
 * Manage FD, RD, PPF, Mutual Funds, and other savings accounts
 */

import React, { useState, useEffect } from 'react';
import { savingsAPI } from '../../../services/api/savingsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import '../../../styles/Savings.css';

const SavingsModule = () => {
  const [view, setView] = useState('dashboard');
  const [dashboard, setDashboard] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [maturities, setMaturities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dashData, accountsData, maturitiesData] = await Promise.all([
        savingsAPI.getDashboard(),
        savingsAPI.getAccounts(),
        savingsAPI.getMaturities(60)
      ]);
      setDashboard(dashData);
      setAccounts(accountsData);
      setMaturities(maturitiesData);
    } catch (error) {
      console.error('Error loading savings data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = () => {
    setSelectedAccount(null);
    setShowAddForm(true);
  };

  const handleEditAccount = (account) => {
    setSelectedAccount(account);
    setShowAddForm(true);
  };

  const handleDeleteAccount = async (id) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return;

    try {
      await savingsAPI.deleteAccount(id);
      loadData();
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account');
    }
  };

  const handleFormSubmit = async (formData) => {
    try {
      if (selectedAccount) {
        await savingsAPI.updateAccount(selectedAccount.id, formData);
      } else {
        await savingsAPI.createAccount(formData);
      }
      setShowAddForm(false);
      loadData();
    } catch (error) {
      console.error('Error saving account:', error);
      throw error;
    }
  };

  if (loading && !dashboard) {
    return <div className="loading">Loading savings data...</div>;
  }

  return (
    <div className="savings-module">
      {/* Header */}
      <div className="module-header">
        <h2>💰 Savings & Investments</h2>
        <p>Manage your savings accounts, fixed deposits, and investments</p>
      </div>

      {/* Actions */}
      <div className="module-actions">
        <button className="btn-primary" onClick={handleAddAccount}>
          ➕ Add Savings Account
        </button>
        <button className="btn-secondary" onClick={() => setView('calculator')}>
          🧮 Calculator
        </button>
        <button className="btn-secondary" onClick={loadData}>
          🔄 Refresh
        </button>
      </div>

      {/* Dashboard Stats */}
      {dashboard && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Total Accounts</div>
              <div className="stat-value">{dashboard.total_accounts}</div>
              <div className="stat-sub">
                {dashboard.active_accounts} active
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💵</div>
            <div className="stat-content">
              <div className="stat-label">Total Invested</div>
              <div className="stat-value">₹{dashboard.total_savings?.toLocaleString('en-IN')}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-label">Interest Earned</div>
              <div className="stat-value success">
                ₹{dashboard.total_interest_earned?.toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⏰</div>
            <div className="stat-content">
              <div className="stat-label">Maturing Soon</div>
              <div className="stat-value">{dashboard.maturing_soon_count}</div>
              <div className="stat-sub">
                ₹{dashboard.maturing_soon_amount?.toLocaleString('en-IN')}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Accounts Table */}
      <div className="accounts-section">
        <h3>📋 Savings Accounts</h3>

        {accounts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💰</div>
            <p>No savings accounts yet</p>
            <button className="btn-primary" onClick={handleAddAccount}>
              Add Your First Account
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Account Name</th>
                  <th>Type</th>
                  <th>Bank</th>
                  <th>Amount</th>
                  <th>Interest Rate</th>
                  <th>Maturity Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map(account => (
                  <tr key={account.id}>
                    <td>
                      <strong>{account.account_name}</strong>
                    </td>
                    <td>{account.account_type}</td>
                    <td>{account.bank_or_institution}</td>
                    <td>₹{account.current_balance?.toLocaleString('en-IN')}</td>
                    <td>{account.interest_rate}%</td>
                    <td>
                      {account.maturity_date || 'N/A'}
                    </td>
                    <td>
                      <span className={`status-badge ${account.status?.toLowerCase()}`}>
                        {account.status}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-icon-small"
                        onClick={() => handleEditAccount(account)}
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon-small"
                        onClick={() => handleDeleteAccount(account.id)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upcoming Maturities */}
      {maturities.length > 0 && (
        <div className="maturities-section">
          <h3>⏰ Upcoming Maturities (Next 60 Days)</h3>
          <div className="maturities-list">
            {maturities.map((maturity, index) => (
              <div key={index} className="maturity-card">
                <div className="maturity-name">{maturity.account_name}</div>
                <div className="maturity-date">{maturity.maturity_date}</div>
                <div className="maturity-amount">
                  ₹{maturity.expected_amount?.toLocaleString('en-IN')}
                </div>
                <div className="maturity-days">{maturity.days_remaining} days</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add/Edit Form Modal */}
      {showAddForm && (
        <AccountFormModal
          account={selectedAccount}
          onSubmit={handleFormSubmit}
          onClose={() => setShowAddForm(false)}
        />
      )}
    </div>
  );
};

// Account Form Modal Component
const AccountFormModal = ({ account, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    account_name: account?.account_name || '',
    account_type: account?.account_type || 'Savings Account',
    bank_or_institution: account?.bank_or_institution || '',
    account_number: account?.account_number || '',
    opening_date: account?.opening_date || new Date().toISOString().split('T')[0],
    initial_amount: account?.initial_amount || '',
    interest_rate: account?.interest_rate || '',
    tenure_months: account?.tenure_months || '',
    compounding_frequency: account?.compounding_frequency || 'Quarterly'
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const accountTypes = [
    'Savings Account',
    'Fixed Deposit',
    'Recurring Deposit',
    'PPF',
    'NSC',
    'Mutual Fund SIP',
    'Bonds',
    'Precious Metals',
    'Digital Gold',
    'Stocks',
    'Other'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(formatErrorMessage(err));
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{account ? 'Edit Account' : 'Add New Account'}</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="account-form">
          <div className="form-row">
            <div className="form-group">
              <label>Account Name *</label>
              <input
                type="text"
                value={formData.account_name}
                onChange={e => setFormData({...formData, account_name: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Account Type *</label>
              <select
                value={formData.account_type}
                onChange={e => setFormData({...formData, account_type: e.target.value})}
                required
              >
                {accountTypes.map(type => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Bank/Institution *</label>
              <input
                type="text"
                value={formData.bank_or_institution}
                onChange={e => setFormData({...formData, bank_or_institution: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Account Number</label>
              <input
                type="text"
                value={formData.account_number}
                onChange={e => setFormData({...formData, account_number: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Opening Date *</label>
              <input
                type="date"
                value={formData.opening_date}
                onChange={e => setFormData({...formData, opening_date: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Initial Amount *</label>
              <input
                type="number"
                step="0.01"
                value={formData.initial_amount}
                onChange={e => setFormData({...formData, initial_amount: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Interest Rate (%) *</label>
              <input
                type="number"
                step="0.01"
                value={formData.interest_rate}
                onChange={e => setFormData({...formData, interest_rate: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Tenure (Months)</label>
              <input
                type="number"
                value={formData.tenure_months}
                onChange={e => setFormData({...formData, tenure_months: e.target.value})}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Compounding Frequency</label>
            <select
              value={formData.compounding_frequency}
              onChange={e => setFormData({...formData, compounding_frequency: e.target.value})}
            >
              <option value="Daily">Daily</option>
              <option value="Monthly">Monthly</option>
              <option value="Quarterly">Quarterly</option>
              <option value="Half-Yearly">Half-Yearly</option>
              <option value="Yearly">Yearly</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Saving...' : (account ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SavingsModule;
