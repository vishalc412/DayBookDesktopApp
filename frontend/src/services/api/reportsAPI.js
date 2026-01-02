/**
 * Reports API Service
 */

import axios from 'axios';
import { config } from '../../config';

const API_BASE = config.API_URL;

export const reportsAPI = {
  // Report Generation
  generateSavingsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/savings/summary`, data, {});
    return response.data;
  },

  generateMetalsSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/precious-metals/summary`, data, {});
    return response.data;
  },

  generateExpensesSummary: async (data) => {
    const response = await axios.post(`${API_BASE}/reports/expenses/summary`, data, {});
    return response.data;
  },

  generateBudgetAnalysis: async (data) => {
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

  // Unified Export to Excel
  exportToExcel: async (reportType, data) => {
    let endpoint;
    switch (reportType) {
      case 'savings':
        endpoint = '/reports/export/savings/excel';
        break;
      case 'metals':
        endpoint = '/reports/export/precious-metals/excel';
        break;
      case 'expenses':
        endpoint = '/reports/export/expenses/excel';
        break;
      case 'budgets':
        endpoint = '/reports/export/budgets/excel';
        break;
      default:
        throw new Error('Unknown report type');
    }
    const response = await axios.post(`${API_BASE}${endpoint}`, data, {
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
