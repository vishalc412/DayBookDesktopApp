/**
 * Expenses & Budgeting Module - COMPLETE UI
 * Track expenses and manage budgets
 */

import React, { useState, useEffect } from 'react';
import { expensesAPI } from '../../../services/api/expensesAPI';
import '../../../styles/Expenses.css';

const ExpensesModule = () => {
  const [expenses, setExpenses] = useState([]);
  const [budgetStatus, setBudgetStatus] = useState([]);
  const [summary, setSummary] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showBudgetForm, setShowBudgetForm] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [expensesData, budgetsData, summaryData, categoryData] = await Promise.all([
        expensesAPI.getExpenses({ limit: 50 }),
        expensesAPI.getBudgetStatus(),
        expensesAPI.getSummary(),
        expensesAPI.getByCategory()
      ]);
      setExpenses(expensesData);
      setBudgetStatus(budgetsData);
      setSummary(summaryData);
      setCategoryBreakdown(categoryData);
    } catch (error) {
      console.error('Error loading expenses data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddExpense = async (formData) => {
    try {
      await expensesAPI.createExpense(formData);
      setShowExpenseForm(false);
      loadData();
    } catch (error) {
      throw error;
    }
  };

  const handleDeleteExpense = async (id) => {
    if (!window.confirm('Delete this expense?')) return;
    try {
      await expensesAPI.deleteExpense(id);
      loadData();
    } catch (error) {
      alert('Failed to delete expense');
    }
  };

  if (loading && !summary) {
    return <div className="loading">Loading expenses...</div>;
  }

  return (
    <div className="expenses-module">
      {/* Header */}
      <div className="module-header">
        <h2>💳 Expenses & Budgeting</h2>
        <p>Track your expenses and manage monthly budgets</p>
      </div>

      {/* Actions */}
      <div className="module-actions">
        <button className="btn-primary" onClick={() => setShowExpenseForm(true)}>
          ➕ Add Expense
        </button>
        <button className="btn-secondary" onClick={() => setShowBudgetForm(true)}>
          💰 Manage Budgets
        </button>
        <button className="btn-secondary" onClick={loadData}>
          🔄 Refresh
        </button>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="expense-stats">
          <div className="stat-card">
            <div className="stat-icon">💵</div>
            <div className="stat-content">
              <div className="stat-label">Total Expenses</div>
              <div className="stat-value">₹{summary.total_expenses?.toLocaleString('en-IN')}</div>
              <div className="stat-sub">{summary.transaction_count} transactions</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-label">Average Expense</div>
              <div className="stat-value">₹{summary.average_expense?.toLocaleString('en-IN')}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🏷️</div>
            <div className="stat-content">
              <div className="stat-label">Top Category</div>
              <div className="stat-value-text">{summary.top_category || 'N/A'}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <div className="stat-label">Budget Alerts</div>
              <div className="stat-value danger">
                {budgetStatus.filter(b => b.is_exceeded || b.is_alert).length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Budget Status */}
      {budgetStatus.length > 0 && (
        <div className="budgets-section">
          <h3>💰 Budget Status</h3>
          <div className="budget-cards">
            {budgetStatus.map((budget, index) => (
              <div
                key={index}
                className={`budget-card ${budget.is_exceeded ? 'exceeded' : budget.is_alert ? 'alert' : 'ok'}`}
              >
                <div className="budget-category">{budget.category}</div>
                <div className="budget-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
                    />
                  </div>
                  <div className="progress-text">{budget.percentage_used?.toFixed(0)}%</div>
                </div>
                <div className="budget-amounts">
                  <span>₹{budget.spent_amount?.toLocaleString('en-IN')}</span>
                  <span> / ₹{budget.budget_amount?.toLocaleString('en-IN')}</span>
                </div>
                {budget.is_exceeded && <div className="budget-status exceeded">Over Budget!</div>}
                {budget.is_alert && !budget.is_exceeded && <div className="budget-status alert">Near Limit</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expenses Table */}
      <div className="expenses-section">
        <h3>📋 Recent Expenses</h3>

        {expenses.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💳</div>
            <p>No expenses yet</p>
            <button className="btn-primary" onClick={() => setShowExpenseForm(true)}>
              Add Your First Expense
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Amount</th>
                  <th>Payment Method</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map(expense => (
                  <tr key={expense.id}>
                    <td>{new Date(expense.expense_date).toLocaleDateString()}</td>
                    <td><strong>{expense.description}</strong></td>
                    <td>
                      <span className="category-badge">
                        {expense.category}
                      </span>
                    </td>
                    <td>₹{expense.amount?.toLocaleString('en-IN')}</td>
                    <td>{expense.payment_method}</td>
                    <td>
                      <button
                        className="btn-icon-small"
                        onClick={() => handleDeleteExpense(expense.id)}
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

      {/* Category Breakdown */}
      {categoryBreakdown.length > 0 && (
        <div className="category-breakdown">
          <h3>📊 Spending by Category</h3>
          <div className="breakdown-grid">
            {categoryBreakdown.slice(0, 6).map((cat, index) => (
              <div key={index} className="breakdown-card">
                <div className="breakdown-category">{cat.category}</div>
                <div className="breakdown-amount">₹{cat.amount?.toLocaleString('en-IN')}</div>
                <div className="breakdown-count">{cat.count} transactions</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expense Form Modal */}
      {showExpenseForm && (
        <ExpenseFormModal
          onSubmit={handleAddExpense}
          onClose={() => setShowExpenseForm(false)}
        />
      )}

      {/* Budget Form Modal */}
      {showBudgetForm && (
        <BudgetFormModal
          onSubmit={async (data) => {
            await expensesAPI.createBudget(data);
            setShowBudgetForm(false);
            loadData();
          }}
          onClose={() => setShowBudgetForm(false)}
        />
      )}
    </div>
  );
};

// Expense Form Modal
const ExpenseFormModal = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    expense_date: new Date().toISOString().split('T')[0],
    category: 'FOOD_DINING',
    amount: '',
    description: '',
    payment_method: 'UPI',
    merchant: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const categories = [
    'FOOD_DINING', 'TRANSPORTATION', 'HEALTHCARE', 'EDUCATION', 'ENTERTAINMENT',
    'SHOPPING', 'BILLS_UTILITIES', 'EMI_LOANS', 'INSURANCE', 'TRAVEL',
    'GIFTS_DONATIONS', 'PERSONAL_CARE', 'HOME_GARDEN', 'PETS',
    'SUBSCRIPTIONS', 'INVESTMENTS', 'TAXES', 'OTHERS'
  ];

  const paymentMethods = [
    'CASH', 'CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING',
    'WALLET', 'CHEQUE', 'BANK_TRANSFER', 'OTHER'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add expense');
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add New Expense</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="expense-form">
          <div className="form-row">
            <div className="form-group">
              <label>Date *</label>
              <input
                type="date"
                value={formData.expense_date}
                onChange={e => setFormData({...formData, expense_date: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Amount *</label>
              <input
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={e => setFormData({...formData, amount: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Description *</label>
            <input
              type="text"
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="What did you spend on?"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category *</label>
              <select
                value={formData.category}
                onChange={e => setFormData({...formData, category: e.target.value})}
                required
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Payment Method *</label>
              <select
                value={formData.payment_method}
                onChange={e => setFormData({...formData, payment_method: e.target.value})}
                required
              >
                {paymentMethods.map(pm => (
                  <option key={pm} value={pm}>
                    {pm.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Merchant</label>
            <input
              type="text"
              value={formData.merchant}
              onChange={e => setFormData({...formData, merchant: e.target.value})}
              placeholder="Store or service provider"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Budget Form Modal
const BudgetFormModal = ({ onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    category: 'FOOD_DINING',
    budget_amount: '',
    period_type: 'MONTHLY',
    alert_at_percentage: 80
  });
  const [submitting, setSubmitting] = useState(false);

  const categories = [
    'FOOD_DINING', 'TRANSPORTATION', 'HEALTHCARE', 'EDUCATION', 'ENTERTAINMENT',
    'SHOPPING', 'BILLS_UTILITIES', 'EMI_LOANS', 'INSURANCE', 'TRAVEL'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (err) {
      alert('Failed to create budget');
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content small" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Set Budget</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="budget-form">
          <div className="form-group">
            <label>Category *</label>
            <select
              value={formData.category}
              onChange={e => setFormData({...formData, category: e.target.value})}
              required
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Budget Amount *</label>
            <input
              type="number"
              step="0.01"
              value={formData.budget_amount}
              onChange={e => setFormData({...formData, budget_amount: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label>Period *</label>
            <select
              value={formData.period_type}
              onChange={e => setFormData({...formData, period_type: e.target.value})}
              required
            >
              <option value="MONTHLY">Monthly</option>
              <option value="YEARLY">Yearly</option>
            </select>
          </div>

          <div className="form-group">
            <label>Alert at {formData.alert_at_percentage}% usage</label>
            <input
              type="range"
              min="50"
              max="100"
              value={formData.alert_at_percentage}
              onChange={e => setFormData({...formData, alert_at_percentage: Number(e.target.value)})}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Creating...' : 'Create Budget'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExpensesModule;
