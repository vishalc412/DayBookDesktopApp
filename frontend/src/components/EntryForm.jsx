/**
 * Entry Form Component
 * Form for creating and editing daybook entries
 */

import React, { useState, useEffect } from 'react';

const EntryForm = ({ onSubmit, editingEntry, onCancel }) => {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    debit: '',
    credit: '',
    category: '',
    reference: ''
  });

  useEffect(() => {
    if (editingEntry) {
      setFormData({
        date: editingEntry.date ? editingEntry.date.split('T')[0] : new Date().toISOString().split('T')[0],
        description: editingEntry.description || '',
        debit: editingEntry.debit || '',
        credit: editingEntry.credit || '',
        category: editingEntry.category || '',
        reference: editingEntry.reference || ''
      });
    }
  }, [editingEntry]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate that either debit or credit is provided
    if (!formData.debit && !formData.credit) {
      alert('Please enter either a debit or credit amount');
      return;
    }

    onSubmit({
      ...formData,
      debit: parseFloat(formData.debit) || 0,
      credit: parseFloat(formData.credit) || 0
    });

    // Reset form if not editing
    if (!editingEntry) {
      setFormData({
        date: new Date().toISOString().split('T')[0],
        description: '',
        debit: '',
        credit: '',
        category: '',
        reference: ''
      });
    }
  };

  const handleCancel = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      description: '',
      debit: '',
      credit: '',
      category: '',
      reference: ''
    });
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="entry-form">
      <h2>{editingEntry ? 'Edit Entry' : 'New Entry'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="date">Date</label>
            <input
              type="date"
              id="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
            >
              <option value="">Select Category</option>
              <option value="Sales">Sales</option>
              <option value="Purchase">Purchase</option>
              <option value="Expense">Expense</option>
              <option value="Income">Income</option>
              <option value="Asset">Asset</option>
              <option value="Liability">Liability</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <input
              type="text"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter description"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="reference">Reference</label>
            <input
              type="text"
              id="reference"
              name="reference"
              value={formData.reference}
              onChange={handleChange}
              placeholder="Invoice/Receipt number"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="debit">Debit Amount</label>
            <input
              type="number"
              id="debit"
              name="debit"
              value={formData.debit}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              min="0"
            />
          </div>
          <div className="form-group">
            <label htmlFor="credit">Credit Amount</label>
            <input
              type="number"
              id="credit"
              name="credit"
              value={formData.credit}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              min="0"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary">
            {editingEntry ? 'Update Entry' : 'Add Entry'}
          </button>
          {editingEntry && (
            <button type="button" className="btn btn-secondary" onClick={handleCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default EntryForm;
