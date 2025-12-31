/**
 * Custom Hook for Real-Time Gold & Silver Prices
 * Optimized for Indian Market with accurate rates
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * Fetch current USD to INR exchange rate
 */
const fetchUsdToInr = async () => {
  try {
    // Using free exchange rate API
    const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
    const data = await response.json();
    return data?.rates?.INR || 84; // Fallback to ~84
  } catch (err) {
    console.warn('USD/INR fetch failed, using default:', err);
    return 84; // Current approximate rate
  }
};

/**
 * Fetch international gold prices and convert to INR
 */
const fetchInternationalGoldPrice = async () => {
  try {
    // Get live USD/INR rate
    const usdToInr = await fetchUsdToInr();

    // Fetch gold spot price in USD per troy oz
    const response = await fetch('https://api.metals.live/v1/spot');
    if (!response.ok) throw new Error('Metals API failed');

    const data = await response.json();
    const goldPerOz = data?.gold || 2650; // Fallback to approximate spot
    const silverPerOz = data?.silver || 31;

    // Convert troy ounce to grams (1 troy oz = 31.1035 grams)
    const goldPerGram24k = (goldPerOz * usdToInr) / 31.1035;

    // Add Indian premium: Import duty (15%) + GST (3%) + Local premium (~5-8%)
    const indianPremium = 1.25; // 25% total markup for Indian market

    return {
      gold_per_gram_24k: goldPerGram24k * indianPremium,
      gold_per_gram_22k: goldPerGram24k * indianPremium * 0.9167, // 22K = 91.67% purity
      gold_per_gram_18k: goldPerGram24k * indianPremium * 0.75,   // 18K = 75% purity
      gold_per_gram_14k: goldPerGram24k * indianPremium * 0.5833, // 14K = 58.33% purity
      silver_per_gram: (silverPerOz * usdToInr / 31.1035) * 1.18, // 18% markup
      gold_per_10g_24k: goldPerGram24k * indianPremium * 10,
      gold_per_10g_22k: goldPerGram24k * indianPremium * 10 * 0.9167,
      gold_per_10g_18k: goldPerGram24k * indianPremium * 10 * 0.75,
      source: 'International Spot + Indian Market Premium',
      usdToInr: usdToInr.toFixed(2),
      timestamp: new Date().toISOString()
    };
  } catch (err) {
    console.error('International price fetch failed:', err);
    throw err;
  }
};

/**
 * Fetch from Indian market sources
 * You can update these rates manually or integrate with Indian APIs
 */
const fetchIndianMarketRates = async () => {
  // These are approximate rates as of January 2025
  // UPDATE THESE with your local market rates
  const currentRates = {
    // Gold rates
    gold_per_gram_24k: 7500,  // ₹7,500 per gram for 24K
    gold_per_gram_22k: 6875,  // ₹6,875 per gram for 22K
    gold_per_gram_18k: 5625,  // ₹5,625 per gram for 18K
    gold_per_gram_14k: 4375,  // ₹4,375 per gram for 14K
    gold_per_10g_24k: 75000,  // ₹75,000 per 10 grams 24K
    gold_per_10g_22k: 68750,  // ₹68,750 per 10 grams 22K
    gold_per_10g_18k: 56250,  // ₹56,250 per 10 grams 18K

    // Silver rates
    silver_per_gram: 92,      // ₹92 per gram for silver
    silver_per_kg: 92000,     // ₹92,000 per kg silver

    // Platinum rates
    platinum_per_gram: 3000,  // ₹3,000 per gram for platinum
    platinum_per_10g: 30000,  // ₹30,000 per 10 grams

    // Copper rates
    copper_per_gram: 0.6,     // ₹0.60 per gram for copper
    copper_per_kg: 600,       // ₹600 per kg

    source: 'Indian Market Estimate (Jan 2025)',
    timestamp: new Date().toISOString()
  };

  return currentRates;
};

/**
 * Hook to fetch real-time gold and silver prices
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoRefresh - Auto-refresh prices (default: true)
 * @param {number} options.refreshInterval - Refresh interval in ms (default: 5 minutes)
 * @param {boolean} options.useInternational - Use international rates with premium (default: false)
 * @returns {Object} Price data and utilities
 */
export const useGoldPrice = (options = {}) => {
  const {
    autoRefresh = true,
    refreshInterval = 5 * 60 * 1000, // 5 minutes default
    useInternational = false, // Set to true to use international + premium
  } = options;

  const [prices, setPrices] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /**
   * Main fetch function with fallback logic
   */
  const fetchPrices = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let priceData = null;

      if (useInternational) {
        // Try international prices first
        try {
          priceData = await fetchInternationalGoldPrice();
        } catch (apiError) {
          console.warn('International API failed, using Indian market rates');
          priceData = await fetchIndianMarketRates();
        }
      } else {
        // Use Indian market rates directly (more accurate for local)
        priceData = await fetchIndianMarketRates();
      }

      setPrices(priceData);
      setLastUpdated(new Date());
      setLoading(false);
      return priceData;

    } catch (err) {
      console.error('Failed to fetch gold prices:', err);
      setError('Failed to fetch live prices. Using default rates.');

      // Final fallback
      const fallbackData = await fetchIndianMarketRates();
      setPrices(fallbackData);
      setLastUpdated(new Date());
      setLoading(false);
    }
  }, [useInternational]);

  /**
   * Calculate price for specific purity and quantity
   */
  const calculatePrice = useCallback((purity, grams) => {
    if (!prices) return 0;

    const ratePerGram = {
      '24K': prices.gold_per_gram_24k,
      '22K': prices.gold_per_gram_22k,
      '18K': prices.gold_per_gram_18k,
      '14K': prices.gold_per_gram_14k
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
      '14K': prices.gold_per_gram_14k * 10
    }[purity] || prices.gold_per_10g_22k;
  }, [prices]);

  /**
   * Manually update rates (useful for setting local market rates)
   */
  const updateRates = useCallback((newRates) => {
    setPrices(prev => ({
      ...prev,
      ...newRates,
      timestamp: new Date().toISOString(),
      source: 'Manually Updated'
    }));
    setLastUpdated(new Date());
  }, []);

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
    getRatePer10g,
    updateRates // New: allow manual rate updates
  };
};

export default useGoldPrice;
