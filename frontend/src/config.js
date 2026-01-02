/**
 * Application Configuration
 * Centralized configuration for API endpoints
 */

// Get API URL from environment variable or use default
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Log the API URL being used (helps with debugging)
console.log('🔧 API Configuration:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  API_URL: API_URL,
  timestamp: new Date().toISOString()
});

export const config = {
  API_URL,
  API_BASE: API_URL,
  // You can add other configuration here
  APP_NAME: 'DayBook Keeper',
  APP_VERSION: '2.0.0',
};

export default config;
