/**
 * Precious Metals Portfolio Module - COMPLETE UI
 * Track gold, silver, and precious metals investments
 */

import React, { useState, useEffect } from 'react';
import { metalsAPI } from '../../../services/api/metalsAPI';
import { formatErrorMessage } from '../../../utils/errorHandler';
import { useGoldPrice } from '../../../hooks/useGoldPrice';
import '../../../styles/PreciousMetals.css';

const PreciousMetalsModule = () => {
  const [view, setView] = useState('portfolio');
  const [portfolio, setPortfolio] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [showCalculator, setShowCalculator] = useState(false);

  // Real-time gold prices
  const { prices, loading: pricesLoading, lastUpdated, refresh: refreshPrices } = useGoldPrice({
    autoRefresh: true,
    refreshInterval: 5 * 60 * 1000 // Refresh every 5 minutes
  });

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

      {/* Real-Time Prices */}
      {prices && (
        <div className="live-prices-banner">
          <div className="live-prices-header">
            <h3>📊 Live Market Rates</h3>
            <div className="price-update-info">
              <span className="live-indicator">● LIVE</span>
              {lastUpdated && (
                <span className="last-updated">
                  Updated: {lastUpdated.toLocaleTimeString()}
                </span>
              )}
              <button className="refresh-btn" onClick={refreshPrices} title="Refresh prices">
                🔄
              </button>
            </div>
          </div>
          <div className="live-prices-grid">
            <div className="price-card gold-24k">
              <span className="metal-label">Gold 24K</span>
              <span className="price-value">₹{prices.gold_per_gram_24k?.toFixed(2)}/g</span>
              <span className="price-per-10g">₹{prices.gold_per_10g_24k?.toLocaleString('en-IN')}/10g</span>
            </div>
            <div className="price-card gold-22k">
              <span className="metal-label">Gold 22K</span>
              <span className="price-value">₹{prices.gold_per_gram_22k?.toFixed(2)}/g</span>
              <span className="price-per-10g">₹{prices.gold_per_10g_22k?.toLocaleString('en-IN')}/10g</span>
            </div>
            <div className="price-card gold-18k">
              <span className="metal-label">Gold 18K</span>
              <span className="price-value">₹{prices.gold_per_gram_18k?.toFixed(2)}/g</span>
              <span className="price-per-10g">₹{prices.gold_per_10g_18k?.toLocaleString('en-IN')}/10g</span>
            </div>
            <div className="price-card silver">
              <span className="metal-label">Silver 999</span>
              <span className="price-value">₹{prices.silver_per_gram?.toFixed(2)}/g</span>
              <span className="price-per-10g">₹{(prices.silver_per_gram * 1000)?.toLocaleString('en-IN')}/kg</span>
            </div>
          </div>
          <div className="price-source">
            <small>Source: {prices.source}</small>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="module-actions">
        <button className="btn-primary" onClick={() => setShowTransactionForm(true)}>
          ➕ Add Transaction
        </button>
        <button className="btn-secondary" onClick={() => setShowCalculator(true)}>
          🧮 Indian Gold Calculator
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
          livePrices={prices}
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

// Simplified Transaction Form Modal
const TransactionFormModal = ({ onSubmit, onClose, livePrices }) => {
  const [formData, setFormData] = useState({
    account_id: 1,
    transaction_type: 'Buy',
    transaction_date: new Date().toISOString().split('T')[0],
    purchase_form: 'Physical Jewelry',
    purity: '22K',
    quantity_grams: '',
    gold_rate_per_10g: livePrices?.gold_per_10g_22k || '',
    making_charges_type: 'percentage',
    making_charges_value: '0',
    include_gst: false,
    include_hallmark: false,
    item_count: '1'
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [currentValue, setCurrentValue] = useState(0);

  // Update rate when purity changes
  useEffect(() => {
    if (livePrices) {
      const rate = {
        '24K': livePrices.gold_per_10g_24k,
        '22K': livePrices.gold_per_10g_22k,
        '18K': livePrices.gold_per_10g_18k,
        '14K': livePrices.gold_per_10g_24k * 0.5833
      }[formData.purity] || livePrices.gold_per_10g_22k;

      setFormData(prev => ({ ...prev, gold_rate_per_10g: rate }));
    }
  }, [formData.purity, livePrices]);

  // Calculate current value
  useEffect(() => {
    if (formData.quantity_grams && livePrices) {
      const ratePerGram = {
        '24K': livePrices.gold_per_gram_24k,
        '22K': livePrices.gold_per_gram_22k,
        '18K': livePrices.gold_per_gram_18k,
        '14K': livePrices.gold_per_gram_24k * 0.5833
      }[formData.purity] || livePrices.gold_per_gram_22k;

      setCurrentValue(parseFloat(formData.quantity_grams) * ratePerGram);
    }
  }, [formData.quantity_grams, formData.purity, livePrices]);

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
          <h3>🥇 Add Gold Transaction</h3>
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
              </select>
            </div>

            <div className="form-group">
              <label>Date *</label>
              <input
                type="date"
                value={formData.transaction_date}
                onChange={e => setFormData({...formData, transaction_date: e.target.value})}
                max={new Date().toISOString().split('T')[0]}
                required
              />
            </div>
          </div>

          <div className="form-row">
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
            <label>Current Market Rate (₹/10g)</label>
            <input
              type="text"
              value={`₹${formData.gold_rate_per_10g?.toLocaleString('en-IN') || '0'}`}
              disabled
              style={{ background: '#f0f9ff', fontWeight: '600', color: '#0369a1' }}
            />
            <small style={{ color: '#64748b' }}>Auto-updated from live market</small>
          </div>

          {/* Current Value Display */}
          {currentValue > 0 && (
            <div className="current-value-display" style={{
              background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
              padding: '16px',
              borderRadius: '8px',
              marginTop: '16px',
              border: '2px solid #f59e0b'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#92400e' }}>
                  Current Market Value:
                </span>
                <strong style={{ fontSize: '20px', color: '#92400e' }}>
                  ₹{currentValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </strong>
              </div>
              <small style={{ color: '#92400e', display: 'block', marginTop: '4px' }}>
                Based on live {formData.purity} gold rate
              </small>
            </div>
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

// Gold Calculator Modal
const GoldCalculatorModal = ({ onClose }) => {
  const [inputs, setInputs] = useState({
    quantity_grams: '10',
    gold_rate_per_10g: '72000',
    purity: '22K',
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
                <option value="24K">24K (99.9%)</option>
                <option value="22K">22K (91.67%)</option>
                <option value="18K">18K (75%)</option>
                <option value="14K">14K (58.33%)</option>
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
