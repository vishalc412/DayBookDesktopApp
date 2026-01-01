/**
 * Precious Metals Portfolio Module - Simplified
 * Track gold, silver, platinum, and copper investments (manual entry, no live rates)
 */

import React, { useState, useEffect } from 'react';
import { metalsAPI } from '../../../services/api/metalsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import '../../../styles/PreciousMetals.css';

const PreciousMetalsModule = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [portfolioData, accountsData, transactionsData] = await Promise.all([
        metalsAPI.getPortfolioSummary(),
        metalsAPI.getAccounts(),
        metalsAPI.getTransactions()
      ]);
      setPortfolio(portfolioData);
      setAccounts(accountsData);
      setTransactions(transactionsData);
    } catch (error) {
      console.error('Error loading precious metals data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !portfolio) {
    return <div className="loading">Loading portfolio...</div>;
  }

  return (
    <div className="precious-metals-module">
      {/* Header */}
      <div className="module-header">
        <h2>💎 Precious Metals Portfolio</h2>
        <p>Track your gold, silver, platinum, and copper investments</p>
      </div>

      {/* Actions */}
      <div className="module-actions">
        <button className="btn-primary" onClick={() => setShowTransactionForm(true)}>
          ➕ Add Transaction
        </button>
        <button className="btn-secondary" onClick={loadData}>
          🔄 Refresh Portfolio
        </button>
      </div>

      {/* Portfolio Stats */}
      {portfolio && (
        <div className="portfolio-stats">
          <div className="stat-card gold">
            <div className="stat-icon">🥇</div>
            <div className="stat-content">
              <div className="stat-label">Total Gold</div>
              <div className="stat-value">{portfolio.total_gold_grams?.toFixed(3)}g</div>
              <div className="stat-sub">
                ₹{portfolio.gold_value?.toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          <div className="stat-card silver">
            <div className="stat-icon">🥈</div>
            <div className="stat-content">
              <div className="stat-label">Total Silver</div>
              <div className="stat-value">{portfolio.total_silver_grams?.toFixed(3)}g</div>
              <div className="stat-sub">
                ₹{portfolio.silver_value?.toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-label">Total Invested</div>
              <div className="stat-value">₹{portfolio.total_invested?.toLocaleString('en-IN')}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Total Holdings</div>
              <div className="stat-value">{portfolio.total_accounts || 0}</div>
              <div className="stat-sub">Accounts</div>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="transactions-section">
        <h3>📋 Transaction History</h3>

        {transactions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💎</div>
            <p>No transactions yet</p>
            <button className="btn-primary" onClick={() => setShowTransactionForm(true)}>
              Add Your First Transaction
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Metal</th>
                  <th>Form</th>
                  <th>Purity</th>
                  <th>Quantity</th>
                  <th>Total Cost</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(txn => (
                  <tr key={txn.id}>
                    <td>{new Date(txn.transaction_date).toLocaleDateString()}</td>
                    <td>
                      <span className={`badge ${txn.transaction_type?.toLowerCase()}`}>
                        {txn.transaction_type}
                      </span>
                    </td>
                    <td>{txn.metal_type}</td>
                    <td><small>{txn.purchase_form}</small></td>
                    <td>{txn.purity || '-'}</td>
                    <td>{txn.quantity_grams?.toFixed(3)}g</td>
                    <td>₹{txn.total_cost?.toLocaleString('en-IN')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Transaction Form Modal */}
      {showTransactionForm && (
        <TransactionFormModal
          onSubmit={async (data) => {
            await metalsAPI.createIndianGold(data);
            setShowTransactionForm(false);
            loadData();
          }}
          onClose={() => setShowTransactionForm(false)}
        />
      )}
    </div>
  );
};

// Simplified Transaction Form - Manual Entry Only
const TransactionFormModal = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    account_id: 1,
    metal_type: 'Gold',
    transaction_type: 'Buy',
    transaction_date: new Date().toISOString().split('T')[0],
    purchase_form: 'Physical Jewelry',
    purity: '22K',
    quantity_grams: '',
    gold_rate_per_10g: '',
    making_charges_type: 'percentage',
    making_charges_value: '0',
    include_gst: false,
    include_hallmark: false,
    item_count: '1'
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Metal type configurations with correct backend enum values
  const metalConfigs = {
    Gold: {
      icon: '🥇',
      purities: ['24K', '22K', '18K', '14K'],
      forms: [
        'Physical Jewelry',
        'Physical Coins',
        'Physical Bars',
        'Gold ETF',
        'Digital Gold',
        'Sovereign Gold Bonds (SGB)',
        'Gold Mutual Fund'
      ]
    },
    Silver: {
      icon: '🥈',
      purities: ['999', '925', '900'],
      forms: [
        'Physical Coins',
        'Physical Bars',
        'Silver ETF'
      ]
    },
    Platinum: {
      icon: '💍',
      purities: ['950', '900', '850'],
      forms: ['Physical Bars', 'Physical Coins']
    },
    Copper: {
      icon: '🔶',
      purities: ['Pure'],
      forms: ['Physical Bars']
    }
  };

  const currentConfig = metalConfigs[formData.metal_type];

  // Check if current form is "Physical" (contains "Physical" in name)
  const isPhysical = formData.purchase_form.includes('Physical');

  // Update purity and form when metal type changes
  useEffect(() => {
    const defaultPurity = currentConfig.purities[0];
    const defaultForm = currentConfig.forms[0];
    setFormData(prev => ({
      ...prev,
      purity: defaultPurity,
      purchase_form: defaultForm,
      quantity_grams: '',
      gold_rate_per_10g: ''
    }));
  }, [formData.metal_type]);

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
          <h3>{currentConfig.icon} Add Precious Metals Transaction</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="transaction-form">
          <div className="form-row">
            <div className="form-group">
              <label>Metal Type *</label>
              <select
                value={formData.metal_type}
                onChange={e => setFormData({...formData, metal_type: e.target.value})}
              >
                <option value="Gold">🥇 Gold</option>
                <option value="Silver">🥈 Silver</option>
                <option value="Platinum">💍 Platinum</option>
                <option value="Copper">🔶 Copper</option>
              </select>
            </div>

            <div className="form-group">
              <label>Transaction Type *</label>
              <select
                value={formData.transaction_type}
                onChange={e => setFormData({...formData, transaction_type: e.target.value})}
              >
                <option value="Buy">Buy</option>
                <option value="Sell">Sell</option>
                <option value="Gift Received">Gift Received</option>
                <option value="Gift Given">Gift Given</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Purchase Form *</label>
              <select
                value={formData.purchase_form}
                onChange={e => setFormData({...formData, purchase_form: e.target.value})}
              >
                {currentConfig.forms.map(form => (
                  <option key={form} value={form}>{form}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Date *</label>
              <input
                type="date"
                value={formData.transaction_date}
                onChange={e => setFormData({...formData, transaction_date: e.target.value})}
                required
              />
            </div>
          </div>

          {/* For Physical: Show Purity, Quantity, Rate */}
          {isPhysical ? (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label>Purity *</label>
                  <select
                    value={formData.purity}
                    onChange={e => setFormData({...formData, purity: e.target.value})}
                  >
                    {currentConfig.purities.map(purity => (
                      <option key={purity} value={purity}>{purity}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Quantity (grams) *</label>
                  <input
                    type="number"
                    step="0.001"
                    value={formData.quantity_grams}
                    onChange={e => setFormData({...formData, quantity_grams: e.target.value})}
                    placeholder="Enter grams"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Rate (₹/10g) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.gold_rate_per_10g}
                  onChange={e => setFormData({...formData, gold_rate_per_10g: e.target.value})}
                  placeholder="Enter purchase rate per 10 grams"
                  required
                />
              </div>
            </>
          ) : (
            /* For ETF/Digital/SGB: Only Quantity and Total Amount */
            <>
              <div className="form-row">
                <div className="form-group">
                  <label>Units/Quantity *</label>
                  <input
                    type="number"
                    step="0.001"
                    value={formData.quantity_grams}
                    onChange={e => setFormData({...formData, quantity_grams: e.target.value})}
                    placeholder="Enter units/quantity"
                    required
                  />
                  <small style={{ color: '#64748b' }}>For ETF/Digital: Units or equivalent grams</small>
                </div>

                <div className="form-group">
                  <label>Total Amount (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.gold_rate_per_10g}
                    onChange={e => setFormData({...formData, gold_rate_per_10g: e.target.value})}
                    placeholder="Enter total investment amount"
                    required
                  />
                </div>
              </div>
            </>
          )}

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PreciousMetalsModule;
