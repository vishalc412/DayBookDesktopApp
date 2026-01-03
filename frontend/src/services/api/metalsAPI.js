/**
 * Precious Metals API Service
 */

import axios from 'axios';
import { config } from '../../config';

const API_BASE = config.API_URL;

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
  createTransaction: async (data) => {
    // Simple transaction - just send quantity and total cost
    // Backend will calculate based on these values
    const transaction_type = data.transaction_type;
    const metalType = data.metal_type || 'Gold';

    // For Gold transactions
    if (metalType === 'Gold' || metalType === 'Silver') {
      const payload = {
        account_id: data.account_id,
        transaction_type: transaction_type,
        transaction_date: data.transaction_date,
        purchase_form: data.purchase_form || 'Physical Jewelry',
        purity: data.purity || '22K',
        quantity_grams: data.quantity_grams,
        // Calculate rate from total cost
        gold_rate_per_10g: metalType === 'Gold' ? (data.total_cost / data.quantity_grams) * 10 : undefined,
        silver_rate_per_kg: metalType === 'Silver' ? (data.total_cost / data.quantity_grams) * 1000 : undefined,
        making_charges_type: 'per_gram',
        making_charges_value: 0,
        include_gst: false, // Don't add extra GST
        include_hallmark: false, // Don't add extra hallmark charges
        item_count: 1,
        vendor_or_buyer: data.notes || '',
        bill_number: '',
        item_description: data.notes || '',
        notes: data.notes || ''
      };

      const endpoint = metalType === 'Gold' ? 'indian-gold' : 'indian-silver';
      const response = await axios.post(`${API_BASE}/precious-metals/transactions/${endpoint}`, payload, {});
      return response.data;
    }

    // For other metals, use international endpoint
    const payload = {
      account_id: data.account_id,
      transaction_type: transaction_type,
      transaction_date: data.transaction_date,
      purchase_form: data.purchase_form || 'Physical Bars',
      quantity_troy_oz: data.quantity_grams / 31.1035,
      usd_per_troy_oz: (data.total_cost / data.quantity_grams) * 31.1035 / 83,
      usd_to_inr_rate: 83,
      import_duty_percentage: 0,
      shipping_charges: 0,
      customs_charges: 0,
      vendor_or_buyer: data.notes || '',
      item_description: data.notes || '',
      notes: data.notes || ''
    };

    const response = await axios.post(`${API_BASE}/precious-metals/transactions/international`, payload, {});
    return response.data;
  },

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

  updateCurrentValue: async (accountId, currentPricePerGram) => {
    const response = await axios.post(`${API_BASE}/precious-metals/portfolio/valuate`, {
      account_id: accountId,
      current_market_price_per_gram: currentPricePerGram
    }, {});
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
