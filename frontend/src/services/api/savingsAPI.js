/**
 * Savings API Service
 * All API calls for savings module
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// Get auth token from localStorage
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

export const savingsAPI = {
  // Accounts
  getAccounts: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/savings/accounts`, {
      params,
      ...getAuthHeaders()
    });
    return response.data;
  },

  getAccount: async (id) => {
    const response = await axios.get(`${API_BASE}/savings/accounts/${id}`, getAuthHeaders());
    return response.data;
  },

  createAccount: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/accounts`, data, getAuthHeaders());
    return response.data;
  },

  updateAccount: async (id, data) => {
    const response = await axios.put(`${API_BASE}/savings/accounts/${id}`, data, getAuthHeaders());
    return response.data;
  },

  deleteAccount: async (id) => {
    const response = await axios.delete(`${API_BASE}/savings/accounts/${id}`, getAuthHeaders());
    return response.data;
  },

  // Entries
  createEntry: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/entries`, data, getAuthHeaders());
    return response.data;
  },

  getEntries: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/savings/entries`, {
      params,
      ...getAuthHeaders()
    });
    return response.data;
  },

  // Dashboard & Analytics
  getDashboard: async () => {
    const response = await axios.get(`${API_BASE}/savings/dashboard`, getAuthHeaders());
    return response.data;
  },

  getMaturities: async (days = 60) => {
    const response = await axios.get(`${API_BASE}/savings/maturities`, {
      params: { days },
      ...getAuthHeaders()
    });
    return response.data;
  },

  // Calculators
  calculateROI: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/roi`, data, getAuthHeaders());
    return response.data;
  },

  calculateRD: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/rd`, data, getAuthHeaders());
    return response.data;
  },

  calculatePPF: async (data) => {
    const response = await axios.post(`${API_BASE}/savings/calculate/ppf`, data, getAuthHeaders());
    return response.data;
  }
};
