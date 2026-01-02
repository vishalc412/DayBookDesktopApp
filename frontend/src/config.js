/**
 * Application Configuration
 * Centralized configuration for API endpoints
 */

// Get API URL from environment variable or use default
// Using port 8765 (uncommon port to avoid conflicts with other services)
// IMPORTANT: Using 127.0.0.1 instead of localhost for consistency
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8765/api';

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
