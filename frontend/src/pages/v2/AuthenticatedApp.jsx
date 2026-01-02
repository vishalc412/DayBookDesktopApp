/**
 * Authenticated App Wrapper
 * Handles authentication flow and displays appropriate screen
 */

import React from 'react';
import { useAuth } from '../../context/AuthContext';
import LoginScreen from './LoginScreen';
import MasterPasswordSetup from './MasterPasswordSetup';
import LockScreen from './LockScreen';
import MainApp from './MainApp';
import '../../styles/Auth.css';

const AuthenticatedApp = () => {
  const { isAuthenticated, isLocked, isSetup } = useAuth();

  // Show loading while checking security status
  if (isSetup === null) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show setup screen if security not configured
  if (!isSetup) {
    return <MasterPasswordSetup />;
  }

  // Show lock screen if app is locked
  if (isLocked) {
    return <LockScreen />;
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  // Show main app if authenticated and unlocked
  return <MainApp />;
};

export default AuthenticatedApp;
