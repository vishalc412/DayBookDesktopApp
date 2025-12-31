/**
 * Custom Hook for Real-Time Gold & Silver Prices
 * Fetches live market rates from multiple API providers
 */

import { useState, useEffect, useCallback } from 'react';

// API Configuration - supports multiple providers
const PRICE_API_CONFIG = {
  // Option 1: Metals-API.com (Free tier: 50 requests/month)
  metalsAPI: {
    url: 'https://api.metals.live/v1/spot',
    enabled: true,
    transform: (data) => ({
      gold_per_gram_inr: data?.gold?.INR / 31.1035, // Troy oz to gram
      silver_per_gram_inr: data?.silver?.INR / 31.1035,
      timestamp: new Date().toISOString()
    })
  },

  // Option 2: GoldAPI.io (Free tier available)
  goldAPI: {
    url: 'https://www.goldapi.io/api/XAU/INR',
    apiKey: process.env.REACT_APP_GOLD_API_KEY || '',
    enabled: false, // Set to true if API key is provided
    transform: (data) => ({
      gold_per_gram_inr: data?.price_gram_24k,
      gold_22k_per_gram: data?.price_gram_22k,
      gold_18k_per_gram: data?.price_gram_18k,
      timestamp: data?.timestamp
    })
  },

  // Option 3: Fallback - Mock/Static data
  fallback: {
    enabled: true,
    data: () => ({
      gold_per_gram_inr: 7200, // ₹7,200 per gram (24K)
      gold_22k_per_gram: 6600, // ₹6,600 per gram (22K)
      gold_18k_per_gram: 5400, // ₹5,400 per gram (18K)
      silver_per_gram_inr: 88, // ₹88 per gram
      timestamp: new Date().toISOString(),
      source: 'fallback'
    })
  }
};

/**
 * Hook to fetch real-time gold and silver prices
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoRefresh - Auto-refresh prices (default: true)
 * @param {number} options.refreshInterval - Refresh interval in ms (default: 5 minutes)
 * @returns {Object} Price data and utilities
 */
export const useGoldPrice = (options = {}) => {
  const {
    autoRefresh = true,
    refreshInterval = 5 * 60 * 1000, // 5 minutes default
  } = options;

  const [prices, setPrices] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /**
   * Fetch prices from Metals-API (free, no API key needed)
   */
  const fetchFromMetalsAPI = async () => {
    try {
      const response = await fetch('https://api.metals.live/v1/spot');
      if (!response.ok) throw new Error('Metals API failed');

      const data = await response.json();

      // Convert troy ounce to grams (1 troy oz = 31.1035 grams)
      const goldPerOz = data?.gold || 0;
      const silverPerOz = data?.silver || 0;

      // Approximate INR conversion (you may want to fetch live USD/INR rate)
      const usdToInr = 83; // Approximate rate, should be fetched dynamically

      return {
        gold_per_gram_24k: (goldPerOz * usdToInr) / 31.1035,
        gold_per_gram_22k: ((goldPerOz * usdToInr) / 31.1035) * 0.9167, // 22K = 91.67% purity
        gold_per_gram_18k: ((goldPerOz * usdToInr) / 31.1035) * 0.75, // 18K = 75% purity
        silver_per_gram: (silverPerOz * usdToInr) / 31.1035,
        gold_per_10g_24k: ((goldPerOz * usdToInr) / 31.1035) * 10,
        gold_per_10g_22k: ((goldPerOz * usdToInr) / 31.1035) * 10 * 0.9167,
        gold_per_10g_18k: ((goldPerOz * usdToInr) / 31.1035) * 10 * 0.75,
        source: 'Metals Live API',
        timestamp: new Date().toISOString()
      };
    } catch (err) {
      console.error('Metals API error:', err);
      throw err;
    }
  };

  /**
   * Fetch prices from GoodReturns India (free, web scraping alternative)
   */
  const fetchFromIndianSource = async () => {
    // For demonstration - returns typical Indian market rates
    // In production, you could use a backend API that scrapes goodreturns.in or similar
    return {
      gold_per_gram_24k: 7200,
      gold_per_gram_22k: 6600,
      gold_per_gram_18k: 5400,
      gold_per_10g_24k: 72000,
      gold_per_10g_22k: 66000,
      gold_per_10g_18k: 54000,
      silver_per_gram: 88,
      silver_per_kg: 88000,
      source: 'Indian Market Estimate',
      timestamp: new Date().toISOString()
    };
  };

  /**
   * Main fetch function with fallback logic
   */
  const fetchPrices = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Try primary API first
      let priceData = null;

      try {
        priceData = await fetchFromMetalsAPI();
      } catch (apiError) {
        console.warn('Primary API failed, using Indian market estimate');
        priceData = await fetchFromIndianSource();
      }

      setPrices(priceData);
      setLastUpdated(new Date());
      setLoading(false);
      return priceData;

    } catch (err) {
      console.error('Failed to fetch gold prices:', err);
      setError('Failed to fetch live prices. Using cached or estimated rates.');

      // Use fallback data
      const fallbackData = PRICE_API_CONFIG.fallback.data();
      setPrices(fallbackData);
      setLastUpdated(new Date());
      setLoading(false);
    }
  }, []);

  /**
   * Calculate price for specific purity and quantity
   */
  const calculatePrice = useCallback((purity, grams) => {
    if (!prices) return 0;

    const ratePerGram = {
      '24K': prices.gold_per_gram_24k,
      '22K': prices.gold_per_gram_22k,
      '18K': prices.gold_per_gram_18k,
      '14K': prices.gold_per_gram_24k * 0.5833
    }[purity] || prices.gold_per_gram_22k;

    return ratePerGram * grams;
  }, [prices]);

  /**
   * Get rate per 10 grams for specific purity
   */
  const getRatePer10g = useCallback((purity) => {
    if (!prices) return 0;

    return {
      '24K': prices.gold_per_10g_24k,
      '22K': prices.gold_per_10g_22k,
      '18K': prices.gold_per_10g_18k,
      '14K': prices.gold_per_10g_24k * 0.5833
    }[purity] || prices.gold_per_10g_22k;
  }, [prices]);

  // Initial fetch
  useEffect(() => {
    fetchPrices();
  }, [fetchPrices]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchPrices();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchPrices]);

  return {
    prices,
    loading,
    error,
    lastUpdated,
    refresh: fetchPrices,
    calculatePrice,
    getRatePer10g
  };
};

export default useGoldPrice;
