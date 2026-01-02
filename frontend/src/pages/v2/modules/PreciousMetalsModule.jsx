/**
 * Investments Module - Simplified (includes Precious Metals)
 * Track all types of investments: Gold, Silver, Stocks, Crypto, etc.
 */

import React, { useState, useEffect } from 'react';
import { metalsAPI } from '../../../services/api/metalsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import '../../../styles/PreciousMetals.css';

const PreciousMetalsModule = () => {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [accountsData, transactionsData] = await Promise.all([
        metalsAPI.getAccounts().catch(() => []),
        metalsAPI.getTransactions().catch(() => [])
      ]);
      setAccounts(accountsData || []);
      setTransactions(transactionsData || []);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async (data) => {
    try {
      await metalsAPI.createAccount(data);
      setShowAccountForm(false);
      loadData();
    } catch (err) {
      setError(formatErrorMessage(err));
    }
  };

  const handleCreateTransaction = async (data) => {
    try {
      await metalsAPI.createTransaction(data);
      setShowTransactionForm(false);
      loadData();
    } catch (err) {
      setError(formatErrorMessage(err));
    }
  };

  // Calculate totals
  const totalInvested = accounts.reduce((sum, acc) => sum + (acc.total_invested || 0), 0);
  const totalValue = accounts.reduce((sum, acc) => sum + (acc.current_market_value || 0), 0);
  const profitLoss = totalValue - totalInvested;

  return (
    <div className="module-content">
      <div className="module-header">
        <h2>💎 Investments Portfolio</h2>
        <p>Track all your investments - Precious Metals, Stocks, Crypto, and more</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="module-actions">
        <button className="btn-primary" onClick={() => setShowAccountForm(true)}>
          ➕ Add Investment
        </button>
        <button className="btn-secondary" onClick={() => setShowTransactionForm(true)} disabled={accounts.length === 0}>
          💸 Add Transaction
        </button>
        <button className="btn-info btn-sm" onClick={loadData}>
          🔄 Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <div className="stat-card">
          <div className="stat-card-icon">💰</div>
          <div className="stat-card-label">Total Invested</div>
          <div className="stat-card-value">₹{totalInvested.toLocaleString('en-IN')}</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">📈</div>
          <div className="stat-card-label">Current Value</div>
          <div className="stat-card-value">₹{totalValue.toLocaleString('en-IN')}</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">{profitLoss >= 0 ? '✅' : '📉'}</div>
          <div className="stat-card-label">Profit/Loss</div>
          <div className="stat-card-value" style={{ color: profitLoss >= 0 ? '#4facfe' : '#ff6b6b' }}>
            {profitLoss >= 0 ? '+' : ''}₹{profitLoss.toLocaleString('en-IN')}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">📊</div>
          <div className="stat-card-label">Total Investments</div>
          <div className="stat-card-value">{accounts.length}</div>
        </div>
      </div>

      {/* Accounts List */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading your investments...</p>
        </div>
      ) : accounts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>💎</div>
          <h3>No Investments Yet</h3>
          <p style={{ color: '#718096', marginBottom: '24px' }}>
            Start tracking your precious metals, stocks, crypto, and other investments
          </p>
          <button className="btn-primary btn-lg" onClick={() => setShowAccountForm(true)}>
            ➕ Add Your First Investment
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '20px' }}>
          {accounts.map(account => (
            <div key={account.id} className="card">
              <div className="card-header">
                <h3>
                  {getIconForType(account.metal_type)} {account.account_name}
                  <span style={{ fontSize: '14px', fontWeight: 'normal', color: '#718096', marginLeft: '12px' }}>
                    {account.metal_type}
                  </span>
                </h3>
              </div>
              <div className="card-body">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Quantity</div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                      {account.total_quantity_grams?.toFixed(3)}g
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Invested</div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                      ₹{account.total_invested?.toLocaleString('en-IN')}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Current Value</div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                      ₹{account.current_market_value?.toLocaleString('en-IN')}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>Profit/Loss</div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: account.profit_loss >= 0 ? '#4facfe' : '#ff6b6b' }}>
                      {account.profit_loss >= 0 ? '+' : ''}₹{account.profit_loss?.toLocaleString('en-IN')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Account Form Modal */}
      {showAccountForm && (
        <AccountForm
          onSubmit={handleCreateAccount}
          onClose={() => setShowAccountForm(false)}
        />
      )}

      {/* Transaction Form Modal */}
      {showTransactionForm && accounts.length > 0 && (
        <TransactionForm
          accounts={accounts}
          onSubmit={handleCreateTransaction}
          onClose={() => setShowTransactionForm(false)}
        />
      )}
    </div>
  );
};

// Helper function to get icon for investment type
const getIconForType = (type) => {
  const icons = {
    'Gold': '🥇',
    'Silver': '🥈',
    'Platinum': '⚪',
    'Palladium': '⚫',
    'Stock': '📈',
    'Crypto': '₿',
    'Other': '💎'
  };
  return icons[type] || '💎';
};

// Simple Account Form
const AccountForm = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    account_name: '',
    metal_type: 'Gold',
    market_type: 'Indian',
    default_purchase_form: 'Physical Jewelry',
    default_purity: '22K',
    storage_location: '',
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(formData);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>➕ Add New Investment</h3>
          <button onClick={onClose} className="modal-close">&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="required">Investment Name</label>
            <input
              type="text"
              value={formData.account_name}
              onChange={e => setFormData({...formData, account_name: e.target.value})}
              placeholder="e.g., My Gold Jewelry"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="required">Type</label>
              <select
                value={formData.metal_type}
                onChange={e => setFormData({...formData, metal_type: e.target.value})}
                required
              >
                <option value="Gold">🥇 Gold</option>
                <option value="Silver">🥈 Silver</option>
                <option value="Platinum">⚪ Platinum</option>
                <option value="Palladium">⚫ Palladium</option>
              </select>
            </div>

            <div className="form-group">
              <label>Market</label>
              <select
                value={formData.market_type}
                onChange={e => setFormData({...formData, market_type: e.target.value})}
              >
                <option value="Indian">Indian</option>
                <option value="International">International</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Storage Location</label>
            <input
              type="text"
              value={formData.storage_location}
              onChange={e => setFormData({...formData, storage_location: e.target.value})}
              placeholder="e.g., Bank Locker, Home Safe"
            />
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={formData.notes}
              onChange={e => setFormData({...formData, notes: e.target.value})}
              placeholder="Any additional notes..."
              rows="3"
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : '➕ Add Investment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Simple Transaction Form
const TransactionForm = ({ accounts, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    account_id: accounts[0]?.id || '',
    transaction_type: 'Buy',
    transaction_date: new Date().toISOString().split('T')[0],
    purchase_form: 'Physical Jewelry',
    purity: '22K',
    quantity_grams: '',
    gold_rate_per_10g: '',
    making_charges: 0,
    gst_amount: 0,
    total_cost: '',
    vendor_or_buyer: '',
    bill_number: '',
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // Find the selected account to get its metal_type and market_type
      const selectedAccount = accounts.find(acc => acc.id === parseInt(formData.account_id));

      const dataToSubmit = {
        ...formData,
        quantity_grams: parseFloat(formData.quantity_grams),
        gold_rate_per_10g: parseFloat(formData.gold_rate_per_10g) || 0,
        total_cost: parseFloat(formData.total_cost),
        account_id: parseInt(formData.account_id),
        metal_type: selectedAccount?.metal_type || 'Gold',
        market_type: selectedAccount?.market_type || 'Indian'
      };
      await onSubmit(dataToSubmit);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>💸 Add Transaction</h3>
          <button onClick={onClose} className="modal-close">&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="required">Investment</label>
              <select
                value={formData.account_id}
                onChange={e => setFormData({...formData, account_id: e.target.value})}
                required
              >
                {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.account_name} ({acc.metal_type})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="required">Type</label>
              <select
                value={formData.transaction_type}
                onChange={e => setFormData({...formData, transaction_type: e.target.value})}
                required
              >
                <option value="Buy">Buy</option>
                <option value="Sell">Sell</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="required">Date</label>
              <input
                type="date"
                value={formData.transaction_date}
                onChange={e => setFormData({...formData, transaction_date: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label className="required">Quantity (grams)</label>
              <input
                type="number"
                step="0.001"
                value={formData.quantity_grams}
                onChange={e => setFormData({...formData, quantity_grams: e.target.value})}
                placeholder="10.500"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="required">Total Cost (₹)</label>
            <input
              type="number"
              step="0.01"
              value={formData.total_cost}
              onChange={e => setFormData({...formData, total_cost: e.target.value})}
              placeholder="75000"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Vendor/Buyer</label>
              <input
                type="text"
                value={formData.vendor_or_buyer}
                onChange={e => setFormData({...formData, vendor_or_buyer: e.target.value})}
                placeholder="e.g., Tanishq"
              />
            </div>

            <div className="form-group">
              <label>Bill Number</label>
              <input
                type="text"
                value={formData.bill_number}
                onChange={e => setFormData({...formData, bill_number: e.target.value})}
                placeholder="Optional"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={formData.notes}
              onChange={e => setFormData({...formData, notes: e.target.value})}
              placeholder="Additional details..."
              rows="2"
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : '💸 Add Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

/* Modal Styles */
const modalStyles = document.createElement('style');
modalStyles.textContent = `
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: slideUp 0.3s ease;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #e2e8f0;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 32px;
    color: #718096;
    cursor: pointer;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .modal-close:hover {
    background: #f7fafc;
    color: #2d3748;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(modalStyles);

export default PreciousMetalsModule;
