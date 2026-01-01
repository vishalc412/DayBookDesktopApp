/**
 * Login Screen
 * Master password login for Daybook v2.0
 */

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/Auth.css';

const LoginScreen = () => {
  const { login } = useAuth();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(password);

    if (!result.success) {
      setError(result.message);
      setFailedAttempts(prev => prev + 1);
      setPassword('');
      setLoading(false);

      if (failedAttempts >= 4) {
        setError('Too many failed attempts. Please wait 5 minutes before trying again.');
      }
    }
    // On success, AuthContext will update and redirect automatically
  };

  return (
    <div className="auth-container">
      <div className="auth-card login-card">
        <div className="auth-header">
          <div className="app-logo">
            <span className="logo-icon">📚</span>
            <h1>DayBookKeeper</h1>
          </div>
          <p className="subtitle">by WarryWorks v2.0</p>
          <p className="welcome-text">Enter your master password to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Master Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your master password"
              required
              disabled={loading || failedAttempts >= 5}
              autoFocus
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          {failedAttempts > 0 && failedAttempts < 5 && (
            <div className="warning-message">
              Failed attempts: {failedAttempts}/5
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !password || failedAttempts >= 5}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <button className="btn-link" disabled>
            Forgot Password?
          </button>
          <p className="info-text">
            🔒 Your data is encrypted and secure
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
