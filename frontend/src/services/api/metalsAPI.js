/**
 * Precious Metals API Service
 */

import axios from 'axios';

// Use environment variable or fallback to default
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const metalsAPI = {
  // Accounts
  getAccounts: async () => {
    const response = await axios.get(`${API_BASE}/precious-metals/accounts`, {});
    return response.data;
  },

  createAccount: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/accounts`, data, {});
    return response.data;
  },

  // Transactions
  createIndianGold: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-gold`, data, {});
    return response.data;
  },

  createIndianSilver: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-silver`, data, {});
    return response.data;
  },

  createInternational: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/international`, data, {});
    return response.data;
  },

  createSGB: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/transactions/sgb`, data, {});
    return response.data;
  },

  getTransactions: async (params = {}) => {
    const response = await axios.get(`${API_BASE}/precious-metals/transactions`, { params, ...{} });
    return response.data;
  },

  // Portfolio
  getPortfolioSummary: async () => {
    const response = await axios.get(`${API_BASE}/precious-metals/portfolio/summary`, {});
    return response.data;
  },

  valuatePortfolio: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/portfolio/valuate`, data, {});
    return response.data;
  },

  // Calculators
  calculateIndianGold: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/calculate/indian-gold`, data, {});
    return response.data;
  },

  calculateSGB: async (data) => {
    const response = await axios.post(`${API_BASE}/precious-metals/calculate/sgb-returns`, data, {});
    return response.data;
  }
};
