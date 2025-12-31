/**
 * Reports API Service
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export const reportsAPI = {
  // Report Generation
  getSavingsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/savings/summary`, data, getAuthHeaders());
    return response.data;
  },

  getMetalsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/precious-metals/summary`, data, getAuthHeaders());
    return response.data;
  },

  getExpensesSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/expenses/summary`, data, getAuthHeaders());
    return response.data;
  },

  getBudgetAnalysis: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/budgets/analysis`, data, getAuthHeaders());
    return response.data;
  },

  // Excel Export
  exportSavingsExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/savings/excel`, data, {
      ...getAuthHeaders(),
      responseType: 'blob'
    });
    return response.data;
  },

  exportMetalsExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/precious-metals/excel`, data, {
      ...getAuthHeaders(),
      responseType: 'blob'
    });
    return response.data;
  },

  exportExpensesExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/expenses/excel`, data, {
      ...getAuthHeaders(),
      responseType: 'blob'
    });
    return response.data;
  },

  exportBudgetExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/budgets/excel`, data, {
      ...getAuthHeaders(),
      responseType: 'blob'
    });
    return response.data;
  },

  // Utility
  getAvailablePeriods: async () => {
    const response = await axios.get(`${API_BASE}/reports/available-periods`, getAuthHeaders());
    return response.data;
  }
};
