/**
 * Expenses API Service
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export const expensesAPI = {
  // Expenses
  getExpenses: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses`, { params, ...getAuthHeaders() });
    return response.data;
  },

  createExpense: async (data) => {
    const response = await axios.post(`${API_BASE}/expenses`, data, getAuthHeaders());
    return response.data;
  },

  updateExpense: async (id, data) => {
    const response = await axios.put(`${API_BASE}/expenses/${id}`, data, getAuthHeaders());
    return response.data;
  },

  deleteExpense: async (id) => {
    const response = await axios.delete(`${API_BASE}/expenses/${id}`, getAuthHeaders());
    return response.data;
  },

  // Budgets
  getBudgets: async () => {
    const response = await axios.get(`${API_BASE}/expenses/budgets`, getAuthHeaders());
    return response.data;
  },

  createBudget: async (data) => {
    const response = await axios.post(`${API_BASE}/expenses/budgets`, data, getAuthHeaders());
    return response.data;
  },

  updateBudget: async (id, data) => {
    const response = await axios.put(`${API_BASE}/expenses/budgets/${id}`, data, getAuthHeaders());
    return response.data;
  },

  getBudgetStatus: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/budgets/status`, { params, ...getAuthHeaders() });
    return response.data;
  },

  // Analytics
  getSummary: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/summary`, { params, ...getAuthHeaders() });
    return response.data;
  },

  getByCategory: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/by-category`, { params, ...getAuthHeaders() });
    return response.data;
  },

  getByPaymentMethod: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/expenses/by-payment-method`, { params, ...getAuthHeaders() });
    return response.data;
  },

  getMonthlyTrend: async (months = 6) => {
    const response = await axios.get(`${API_BASE}/expenses/monthly-trend`, {
      params: { months },
      ...getAuthHeaders()
    });
    return response.data;
  },

  getTopExpenses: async (limit = 10) => {
    const response = await axios.get(`${API_BASE}/expenses/top-expenses`, {
      params: { limit },
      ...getAuthHeaders()
    });
    return response.data;
  }
};
