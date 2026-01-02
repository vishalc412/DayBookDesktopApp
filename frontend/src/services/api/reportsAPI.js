/**
 * Reports API Service
 */

import axios from 'axios';
import { config } from '../../config';

const API_BASE = config.API_URL;

export const reportsAPI = {
  // Report Generation
  getSavingsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/savings/summary`, data, {});
    return response.data;
  },

  getMetalsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/precious-metals/summary`, data, {});
    return response.data;
  },

  getExpensesSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/expenses/summary`, data, {});
    return response.data;
  },

  getBudgetAnalysis: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/budgets/analysis`, data, {});
    return response.data;
  },

  // Excel Export
  exportSavingsExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/savings/excel`, data, {
responseType: 'blob'
    });
    return response.data;
  },

  exportMetalsExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/precious-metals/excel`, data, {
      responseType: 'blob'
    });
    return response.data;
  },

  exportExpensesExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/expenses/excel`, data, {
responseType: 'blob'
    });
    return response.data;
  },

  exportBudgetExcel: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/export/budgets/excel`, data, {
responseType: 'blob'
    });
    return response.data;
  },

  // Utility
  getAvailablePeriods: async () => {
    const response = await axios.get(`${API_BASE}/reports/available-periods`, {});
    return response.data;
  }
};
