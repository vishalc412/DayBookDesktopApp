/**
 * Lock Screen
 * Unlock app after auto-lock or manual lock
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/Auth.css';

const LockScreen = () => {
  const { unlockApp, logout } = useAuth();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [lockTime, setLockTime] = useState(new Date());

  useEffect(() => {
    setLockTime(new Date());
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await unlockApp(password);

    if (!result.success) {
      setError(result.message);
      setPassword('');
      setLoading(false);
    }
    // On success, AuthContext will update
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to log out? Any unsaved changes will be lost.')) {
      logout();
    }
  };

  return (
    <div className="auth-container lock-screen">
      <div className="auth-card lock-card">
        <div className="lock-icon">
          <span>🔒</span>
        </div>

        <div className="auth-header">
          <h2>App Locked</h2>
          <p className="lock-time">Locked at {lockTime.toLocaleTimeString()}</p>
          <p className="subtitle">Enter your master password to unlock</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Master password"
              required
              disabled={loading}
              autoFocus
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !password}
          >
            {loading ? 'Unlocking...' : 'Unlock'}
          </button>
        </form>

        <div className="auth-footer">
          <button onClick={handleLogout} className="btn-link-danger">
            Logout
          </button>
          <p className="info-text">
            Auto-locked due to inactivity
          </p>
        </div>
      </div>
    </div>
  );
};

export default LockScreen;
