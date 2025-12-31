/**
 * Authentication Context
 * Manages master password, session, and auto-lock functionality
 */

import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_BASE = 'http://localhost:8000/api';
const AUTO_LOCK_TIMEOUT = 15 * 60 * 1000; // 15 minutes

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const [isSetup, setIsSetup] = useState(null); // null = checking, true = setup done, false = needs setup
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [lastActivity, setLastActivity] = useState(Date.now());

  // Check if security is set up
  useEffect(() => {
    checkSecurityStatus();
  }, []);

  // Auto-lock functionality
  useEffect(() => {
    if (!isAuthenticated) return;

    const checkAutoLock = setInterval(() => {
      const timeSinceActivity = Date.now() - lastActivity;
      if (timeSinceActivity > AUTO_LOCK_TIMEOUT) {
        lockApp();
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkAutoLock);
  }, [isAuthenticated, lastActivity]);

  // Activity tracking
  useEffect(() => {
    if (!isAuthenticated) return;

    const updateActivity = () => {
      setLastActivity(Date.now());
    };

    // Track user activity
    window.addEventListener('mousemove', updateActivity);
    window.addEventListener('keydown', updateActivity);
    window.addEventListener('click', updateActivity);

    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('click', updateActivity);
    };
  }, [isAuthenticated]);

  const checkSecurityStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/security/status`);
      setIsSetup(response.data.is_setup);

      if (response.data.is_setup && token) {
        // Verify token
        try {
          await axios.post(`${API_BASE}/security/verify-token`, {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setIsAuthenticated(true);
          setIsLocked(false);
        } catch (error) {
          // Token invalid
          localStorage.removeItem('authToken');
          setToken(null);
          setIsAuthenticated(false);
        }
      }
    } catch (error) {
      console.error('Failed to check security status:', error);
      setIsSetup(false);
    }
  };

  const setupMasterPassword = async (password, securityQuestions) => {
    try {
      const response = await axios.post(`${API_BASE}/security/setup`, {
        password,
        security_questions: securityQuestions
      });

      setToken(response.data.token);
      localStorage.setItem('authToken', response.data.token);
      setIsSetup(true);
      setIsAuthenticated(true);
      setIsLocked(false);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Setup failed'
      };
    }
  };

  const login = async (password) => {
    try {
      const response = await axios.post(`${API_BASE}/security/login`, {
        password
      });

      setToken(response.data.token);
      localStorage.setItem('authToken', response.data.token);
      setIsAuthenticated(true);
      setIsLocked(false);
      setLastActivity(Date.now());

      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API_BASE}/security/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setToken(null);
      localStorage.removeItem('authToken');
      setIsAuthenticated(false);
      setIsLocked(false);
    }
  };

  const lockApp = async () => {
    setIsLocked(true);
  };

  const unlockApp = async (password) => {
    try {
      const response = await axios.post(`${API_BASE}/security/unlock`, {
        password
      });

      setToken(response.data.token);
      localStorage.setItem('authToken', response.data.token);
      setIsLocked(false);
      setLastActivity(Date.now());

      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Unlock failed'
      };
    }
  };

  const value = {
    isAuthenticated,
    isLocked,
    isSetup,
    token,
    setupMasterPassword,
    login,
    logout,
    lockApp,
    unlockApp,
    updateActivity: () => setLastActivity(Date.now())
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
