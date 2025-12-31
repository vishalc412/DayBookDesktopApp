/**
 * Precious Metals Portfolio Module - COMPLETE UI
 * Track gold, silver, and precious metals investments
 */

import React, { useState, useEffect } from 'react';
import { metalsAPI } from '../../../services/api/metalsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import '../../../styles/PreciousMetals.css';

const PreciousMetalsModule = () => {
  const [view, setView] = useState('portfolio');
  const [portfolio, setPortfolio] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [showCalculator, setShowCalculator] = useState(false);

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
        <h2>🥇 Precious Metals Portfolio</h2>
        <p>Track your gold, silver, and precious metals investments</p>
      </div>

      {/* Actions */}
      <div className="module-actions">
        <button className="btn-primary" onClick={() => setShowTransactionForm(true)}>
          ➕ Add Transaction
        </button>
        <button className="btn-secondary" onClick={() => setShowCalculator(true)}>
          🧮 Indian Gold Calculator
        </button>
        <button className="btn-secondary" onClick={loadData}>
          🔄 Refresh
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
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-label">Market Value</div>
              <div className="stat-value">₹{portfolio.current_value?.toLocaleString('en-IN')}</div>
              <div className="stat-sub">Based on current market rates</div>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="transactions-section">
        <h3>📋 Transaction History</h3>

        {transactions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🥇</div>
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
                  <th>Quantity</th>
                  <th>Rate</th>
                  <th>Total Cost</th>
                  <th>Market Type</th>
                  <th>Details</th>
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
                    <td>{txn.quantity_grams?.toFixed(3)}g</td>
                    <td>₹{txn.effective_rate_per_gram?.toLocaleString('en-IN')}/g</td>
                    <td>₹{txn.total_cost?.toLocaleString('en-IN')}</td>
                    <td>{txn.market_type}</td>
                    <td>
                      <small>{txn.purchase_form || txn.description}</small>
                    </td>
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

      {/* Calculator Modal */}
      {showCalculator && (
        <GoldCalculatorModal
          onClose={() => setShowCalculator(false)}
        />
      )}
    </div>
  );
};

// Transaction Form Modal
const TransactionFormModal = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    account_id: 1, // Default account
    transaction_type: 'Buy',
    transaction_date: new Date().toISOString().split('T')[0],
    purchase_form: 'Physical Jewelry',
    purity: '22K',
    quantity_grams: '',
    gold_rate_per_10g: '',
    making_charges_type: 'percentage',
    making_charges_value: '12',
    include_gst: true,
    include_hallmark: true,
    item_count: '1',
    vendor_or_buyer: '',
    bill_number: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

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
      <div className="modal-content large" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Gold Transaction (Indian Market)</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="transaction-form">
          <div className="form-row">
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
                <option value="Transfer In">Transfer In</option>
                <option value="Transfer Out">Transfer Out</option>
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

          <div className="form-row">
            <div className="form-group">
              <label>Purchase Form *</label>
              <select
                value={formData.purchase_form}
                onChange={e => setFormData({...formData, purchase_form: e.target.value})}
              >
                <option value="Physical Jewelry">Physical Jewelry</option>
                <option value="Physical Coins">Physical Coins</option>
                <option value="Physical Bars">Physical Bars</option>
                <option value="Sovereign Gold Bonds (SGB)">Sovereign Gold Bonds (SGB)</option>
                <option value="Digital Gold">Digital Gold</option>
                <option value="Gold ETF">Gold ETF</option>
                <option value="Gold Mutual Fund">Gold Mutual Fund</option>
                <option value="Silver ETF">Silver ETF</option>
              </select>
            </div>

            <div className="form-group">
              <label>Purity *</label>
              <select
                value={formData.purity}
                onChange={e => setFormData({...formData, purity: e.target.value})}
              >
                <option value="24K">24K (99.9%)</option>
                <option value="22K">22K (91.67%)</option>
                <option value="18K">18K (75%)</option>
                <option value="14K">14K (58.33%)</option>
                <option value="999">999 (99.9% Silver/Platinum)</option>
                <option value="925">925 (92.5% Sterling Silver)</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Quantity (grams) *</label>
              <input
                type="number"
                step="0.001"
                value={formData.quantity_grams}
                onChange={e => setFormData({...formData, quantity_grams: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Gold Rate (₹/10g) *</label>
              <input
                type="number"
                step="0.01"
                value={formData.gold_rate_per_10g}
                onChange={e => setFormData({...formData, gold_rate_per_10g: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Making Charges Type</label>
              <select
                value={formData.making_charges_type}
                onChange={e => setFormData({...formData, making_charges_type: e.target.value})}
              >
                <option value="percentage">Percentage</option>
                <option value="per_gram">Per Gram</option>
              </select>
            </div>

            <div className="form-group">
              <label>Making Charges Value</label>
              <input
                type="number"
                step="0.01"
                value={formData.making_charges_value}
                onChange={e => setFormData({...formData, making_charges_value: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.include_gst}
                  onChange={e => setFormData({...formData, include_gst: e.target.checked})}
                />
                {' '}Include GST (3%)
              </label>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.include_hallmark}
                  onChange={e => setFormData({...formData, include_hallmark: e.target.checked})}
                />
                {' '}Include Hallmark Charges (₹40/item)
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Number of Items</label>
              <input
                type="number"
                value={formData.item_count}
                onChange={e => setFormData({...formData, item_count: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Vendor/Buyer</label>
              <input
                type="text"
                value={formData.vendor_or_buyer}
                onChange={e => setFormData({...formData, vendor_or_buyer: e.target.value})}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Bill Number</label>
            <input
              type="text"
              value={formData.bill_number}
              onChange={e => setFormData({...formData, bill_number: e.target.value})}
            />
          </div>

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

// Gold Calculator Modal
const GoldCalculatorModal = ({ onClose }) => {
  const [inputs, setInputs] = useState({
    quantity_grams: '10',
    gold_rate_per_10g: '72000',
    purity: 'PURITY_22K',
    making_charges_type: 'percentage',
    making_charges_value: '12',
    include_gst: true,
    include_hallmark: true,
    num_items: '1'
  });
  const [result, setResult] = useState(null);
  const [calculating, setCalculating] = useState(false);

  const handleCalculate = async () => {
    setCalculating(true);
    try {
      const data = await metalsAPI.calculateIndianGold(inputs);
      setResult(data);
    } catch (error) {
      console.error('Calculation error:', error);
      alert('Failed to calculate');
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>🧮 Indian Gold Cost Calculator</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="calculator-content">
          <div className="calculator-inputs">
            <div className="form-group">
              <label>Quantity (grams)</label>
              <input
                type="number"
                step="0.001"
                value={inputs.quantity_grams}
                onChange={e => setInputs({...inputs, quantity_grams: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Gold Rate (₹/10g)</label>
              <input
                type="number"
                value={inputs.gold_rate_per_10g}
                onChange={e => setInputs({...inputs, gold_rate_per_10g: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Purity</label>
              <select
                value={inputs.purity}
                onChange={e => setInputs({...inputs, purity: e.target.value})}
              >
                <option value="PURITY_24K">24K (99.9%)</option>
                <option value="PURITY_22K">22K (91.67%)</option>
                <option value="PURITY_18K">18K (75%)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Making Charges (%)</label>
              <input
                type="number"
                step="0.1"
                value={inputs.making_charges_value}
                onChange={e => setInputs({...inputs, making_charges_value: e.target.value})}
              />
            </div>

            <button className="btn-primary" onClick={handleCalculate} disabled={calculating}>
              {calculating ? 'Calculating...' : '🧮 Calculate'}
            </button>
          </div>

          {result && (
            <div className="calculator-result">
              <h4>💰 Cost Breakdown</h4>
              <div className="result-item">
                <span>Base Gold Cost:</span>
                <strong>₹{result.base_gold_cost?.toLocaleString('en-IN')}</strong>
              </div>
              <div className="result-item">
                <span>Making Charges:</span>
                <strong>₹{result.making_charges?.toLocaleString('en-IN')}</strong>
              </div>
              <div className="result-item">
                <span>GST (3%):</span>
                <strong>₹{result.gst_amount?.toLocaleString('en-IN')}</strong>
              </div>
              <div className="result-item">
                <span>Hallmark Charges:</span>
                <strong>₹{result.hallmark_charges?.toLocaleString('en-IN')}</strong>
              </div>
              <div className="result-total">
                <span>TOTAL COST:</span>
                <strong>₹{result.total_cost?.toLocaleString('en-IN')}</strong>
              </div>
              <div className="result-item">
                <span>Effective Rate:</span>
                <strong>₹{result.effective_rate_per_gram?.toLocaleString('en-IN')}/gram</strong>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default PreciousMetalsModule;
