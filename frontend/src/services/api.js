/**
 * API Service for communicating with Python backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const daybookAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get all entries
  getEntries: async () => {
    const response = await api.get('/entries');
    return response.data;
  },

  // Create new entry
  createEntry: async (entry) => {
    const response = await api.post('/entries', entry);
    return response.data;
  },

  // Update entry
  updateEntry: async (entryId, entry) => {
    const response = await api.put(`/entries/${entryId}`, entry);
    return response.data;
  },

  // Delete entry
  deleteEntry: async (entryId) => {
    const response = await api.delete(`/entries/${entryId}`);
    return response.data;
  },

  // Get summary
  getSummary: async () => {
    const response = await api.get('/summary');
    return response.data;
  },

  // Get export file path
  getExportPath: async () => {
    const response = await api.get('/export');
    return response.data;
  },
};

export default api;
