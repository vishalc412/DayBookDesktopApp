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
    // Route to appropriate endpoint based on purchase form and metal type
    const purchaseForm = data.purchase_form;
    const metalType = data.metal_type || 'Gold'; // Default to Gold if not specified
    const marketType = data.market_type || 'Indian'; // Default to Indian

    if (purchaseForm === 'Sovereign Gold Bonds (SGB)') {
      // SGB transaction
      const sgbData = {
        account_id: data.account_id,
        transaction_type: data.transaction_type,
        transaction_date: data.transaction_date,
        quantity_grams: data.quantity_grams,
        sgb_issue_price: data.total_cost / data.quantity_grams,
        sgb_issue_date: data.transaction_date,
        vendor_or_buyer: data.vendor_or_buyer,
        notes: data.notes
      };
      const response = await axios.post(`${API_BASE}/precious-metals/transactions/sgb`, sgbData, {});
      return response.data;
    } else if (marketType === 'International') {
      // International bullion transaction
      const internationalData = {
        account_id: data.account_id,
        transaction_type: data.transaction_type,
        transaction_date: data.transaction_date,
        purchase_form: data.purchase_form,
        quantity_troy_oz: data.quantity_grams / 31.1035, // Convert grams to troy oz
        usd_per_troy_oz: (data.total_cost / data.quantity_grams) * 31.1035 / 83, // Rough conversion
        usd_to_inr_rate: 83, // Default exchange rate
        import_duty_percentage: 10.75,
        shipping_charges: 0,
        customs_charges: 0,
        vendor_or_buyer: data.vendor_or_buyer,
        item_description: data.notes,
        notes: data.notes
      };
      const response = await axios.post(`${API_BASE}/precious-metals/transactions/international`, internationalData, {});
      return response.data;
    } else if (metalType === 'Gold') {
      // Indian gold transaction
      const indianData = {
        account_id: data.account_id,
        transaction_type: data.transaction_type,
        transaction_date: data.transaction_date,
        purchase_form: data.purchase_form,
        purity: data.purity || '22K',
        quantity_grams: data.quantity_grams,
        gold_rate_per_10g: (data.total_cost / data.quantity_grams) * 10,
        making_charges_type: 'percentage',
        making_charges_value: 0,
        include_gst: true,
        include_hallmark: true,
        item_count: 1,
        vendor_or_buyer: data.vendor_or_buyer,
        bill_number: data.bill_number,
        item_description: data.notes,
        notes: data.notes
      };
      const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-gold`, indianData, {});
      return response.data;
    } else {
      // Indian silver transaction
      const silverData = {
        account_id: data.account_id,
        transaction_type: data.transaction_type,
        transaction_date: data.transaction_date,
        purchase_form: data.purchase_form,
        quantity_grams: data.quantity_grams,
        silver_rate_per_kg: (data.total_cost / data.quantity_grams) * 1000,
        making_charges_type: 'percentage',
        making_charges_value: 0,
        include_gst: true,
        include_hallmark: false,
        item_count: 1,
        vendor_or_buyer: data.vendor_or_buyer,
        bill_number: data.bill_number,
        item_description: data.notes,
        notes: data.notes
      };
      const response = await axios.post(`${API_BASE}/precious-metals/transactions/indian-silver`, silverData, {});
      return response.data;
    }
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
