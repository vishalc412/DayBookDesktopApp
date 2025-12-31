/**
 * Precious Metals API Service
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export const metalsAPI = {
  // Accounts
  getAccounts: async () => {
    const response = await axios.get(`${API_BASE}/precious-metals/accounts`, getAuthHeaders());
    return response.data;
  },

  createAccount: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/accounts`, data, getAuthHeaders());
    return response.data;
  },

  // Transactions
  createIndianGold: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-gold`, data, getAuthHeaders());
    return response.data;
  },

  createIndianSilver: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-silver`, data, getAuthHeaders());
    return response.data;
  },

  createInternational: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/international`, data, getAuthHeaders());
    return response.data;
  },

  createSGB: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/sgb`, data, getAuthHeaders());
    return response.data;
  },

  getTransactions: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/precious-metals/transactions`, { params, ...getAuthHeaders() });
    return response.data;
  },

  // Portfolio
  getPortfolioSummary: async () => {
    const response = await axios.get(`${API_BASE}/precious-metals/portfolio/summary`, getAuthHeaders());
    return response.data;
  },

  valuatePortfolio: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/portfolio/valuate`, data, getAuthHeaders());
    return response.data;
  },

  // Calculators
  calculateIndianGold: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/calculate/indian-gold`, data, getAuthHeaders());
    return response.data;
  },

  calculateSGB: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/calculate/sgb-returns`, data, getAuthHeaders());
    return response.data;
  }
};
