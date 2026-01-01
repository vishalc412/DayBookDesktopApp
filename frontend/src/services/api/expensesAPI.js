/**
 * Expenses API Service
 */

import axios from 'axios';

// Use environment variable or fallback to default
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const expensesAPI = {
  // Expenses
  getExpenses: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses`, { params });
    return response.data;
  },

  createExpense: async (data) => {
    const response = await axios.post(`${API_BASE}/expenses`, data);
    return response.data;
  },

  updateExpense: async (id, data) => {
    const response = await axios.put(`${API_BASE}/expenses/${id}`, data);
    return response.data;
  },

  deleteExpense: async (id) => {
    const response = await axios.delete(`${API_BASE}/expenses/${id}`);
    return response.data;
  },

  // Budgets
  getBudgets: async () => {
    const response = await axios.get(`${API_BASE}/expenses/budgets`);
    return response.data;
  },

  createBudget: async (data) => {
    const response = await axios.post(`${API_BASE}/expenses/budgets`, data);
    return response.data;
  },

  updateBudget: async (id, data) => {
    const response = await axios.put(`${API_BASE}/expenses/budgets/${id}`, data);
    return response.data;
  },

  getBudgetStatus: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/budgets/status`, { params });
    return response.data;
  },

  // Analytics
  getSummary: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/summary`, { params });
    return response.data;
  },

  getByCategory: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/by-category`, { params });
    return response.data;
  },

  getByPaymentMethod: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/by-payment-method`, { params });
    return response.data;
  },

  getMonthlyTrend: async (months = 6) => {
    const response = await axios.get(`${API_BASE}/expenses/monthly-trend`, {
      params: { months }
    });
    return response.data;
  },

  getTopExpenses: async (limit = 10) => {
    const response = await axios.get(`${API_BASE}/expenses/top-expenses`, {
      params: { limit }
    });
    return response.data;
  }
};
