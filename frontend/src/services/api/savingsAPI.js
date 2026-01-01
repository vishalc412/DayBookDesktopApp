/**
 * Savings API Service
 * All API calls for savings module
 */

import axios from 'axios';

// Use environment variable or fallback to default
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const savingsAPI = {
  // Accounts
  getAccounts: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/savings/accounts`, { params });
    return response.data;
  },

  getAccount: async (id) => {
    const response = await axios.get(`${API_BASE}/savings/accounts/${id}`, {});
    return response.data;
  },

  createAccount: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/accounts`, data, {});
    return response.data;
  },

  updateAccount: async (id, data) => {
    const response = await axios.put(`${API_BASE}/savings/accounts/${id}`, data, {});
    return response.data;
  },

  deleteAccount: async (id) => {
    const response = await axios.delete(`${API_BASE}/savings/accounts/${id}`, {});
    return response.data;
  },

  // Entries
  createEntry: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/entries`, data, {});
    return response.data;
  },

  getEntries: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/savings/entries`, {
      params,
      ...{}
    });
    return response.data;
  },

  // Dashboard & Analytics
  getDashboard: async () => {
    const response = await axios.get(`${API_BASE}/savings/dashboard`, {});
    return response.data;
  },

  getMaturities: async (days = 60) => {
    const response = await axios.get(`${API_BASE}/savings/maturities`, {
      params: { days },
      ...{}
    });
    return response.data;
  },

  // Calculators
  calculateROI: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/roi`, data, {});
    return response.data;
  },

  calculateRD: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/rd`, data, {});
    return response.data;
  },

  calculatePPF: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/ppf`, data, {});
    return response.data;
  }
};
