/**
 * Master Password Setup Screen
 * First-time setup for Daybook v2.0 security
 */

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/Auth.css';

const MasterPasswordSetup = () => {
  const { setupMasterPassword } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    question1: '',
    answer1: '',
    question2: '',
    answer2: '',
    question3: '',
    answer3: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);

  const commonQuestions = [
    "What is your mother's maiden name?",
    "What city were you born in?",
    "What is your favorite teacher's name?",
    "What is your pet's name?",
    "What is your favorite book?",
    "What is your first school's name?",
    "What is your favorite food?",
    "What is your childhood nickname?"
  ];

  const checkPasswordStrength = (password) => {
    const requirements = {
      length: password.length >= 12,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    const score = Object.values(requirements).filter(Boolean).length;
    const allMet = Object.values(requirements).every(Boolean);

    return {
      score,
      allMet,
      requirements,
      strength: score <= 2 ? 'weak' : score <= 4 ? 'medium' : 'strong'
    };
  };

  const handlePasswordChange = (e) => {
    const password = e.target.value;
    setFormData(prev => ({ ...prev, password }));
    setPasswordStrength(checkPasswordStrength(password));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate username
    if (!formData.username || formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    // Validate password
    const strength = checkPasswordStrength(formData.password);
    if (!strength.allMet) {
      setError('Password does not meet all requirements');
      return;
    }

    // Validate password confirmation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate security questions
    if (!formData.question1 || !formData.answer1 ||
        !formData.question2 || !formData.answer2 ||
        !formData.question3 || !formData.answer3) {
      setError('Please answer all 3 security questions');
      return;
    }

    if (formData.answer1.length < 3 || formData.answer2.length < 3 || formData.answer3.length < 3) {
      setError('Security answers must be at least 3 characters');
      return;
    }

    setLoading(true);

    const securityQuestions = [
      { question: formData.question1, answer: formData.answer1 },
      { question: formData.question2, answer: formData.answer2 },
      { question: formData.question3, answer: formData.answer3 }
    ];

    const result = await setupMasterPassword(formData.password, securityQuestions, formData.username);

    if (!result.success) {
      setError(result.message);
      setLoading(false);
    }
    // On success, AuthContext will update and redirect automatically
  };

  return (
    <div className="auth-container">
      <div className="auth-card setup-card">
        <div className="auth-header">
          <h1>🔒 Daybook v2.0 Setup</h1>
          <p>Create your master password to secure your financial data</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* User Information */}
          <div className="form-section">
            <h3>User Information</h3>
            <div className="form-group">
              <label>Username *</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                placeholder="Enter your username"
                required
                disabled={loading}
                minLength={3}
              />
              <small>This will be displayed throughout the application</small>
            </div>
          </div>

          {/* Master Password */}
          <div className="form-section">
            <h3>Master Password</h3>
            <div className="form-group">
              <label>Master Password *</label>
              <input
                type="password"
                value={formData.password}
                onChange={handlePasswordChange}
                placeholder="Enter master password"
                required
                disabled={loading}
              />
              {passwordStrength && (
                <div className={`password-strength ${passwordStrength.strength}`}>
                  <div className="strength-bar">
                    <div
                      className="strength-fill"
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    />
                  </div>
                  <div className="requirements">
                    <div className={passwordStrength.requirements.length ? 'met' : 'unmet'}>
                      {passwordStrength.requirements.length ? '✓' : '○'} 12+ characters
                    </div>
                    <div className={passwordStrength.requirements.uppercase ? 'met' : 'unmet'}>
                      {passwordStrength.requirements.uppercase ? '✓' : '○'} Uppercase letter
                    </div>
                    <div className={passwordStrength.requirements.lowercase ? 'met' : 'unmet'}>
                      {passwordStrength.requirements.lowercase ? '✓' : '○'} Lowercase letter
                    </div>
                    <div className={passwordStrength.requirements.number ? 'met' : 'unmet'}>
                      {passwordStrength.requirements.number ? '✓' : '○'} Number
                    </div>
                    <div className={passwordStrength.requirements.special ? 'met' : 'unmet'}>
                      {passwordStrength.requirements.special ? '✓' : '○'} Special character
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Confirm Password *</label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                placeholder="Confirm master password"
                required
                disabled={loading}
              />
            </div>
          </div>

          {/* Security Questions */}
          <div className="form-section">
            <h3>Security Questions</h3>
            <p className="section-desc">Answer 3 security questions for password recovery</p>

            {[1, 2, 3].map(num => (
              <div key={num} className="security-question">
                <div className="form-group">
                  <label>Question {num} *</label>
                  <select
                    value={formData[`question${num}`]}
                    onChange={(e) => setFormData(prev => ({ ...prev, [`question${num}`]: e.target.value }))}
                    required
                    disabled={loading}
                  >
                    <option value="">Select a question...</option>
                    {commonQuestions.map(q => (
                      <option key={q} value={q}>{q}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Answer {num} *</label>
                  <input
                    type="text"
                    value={formData[`answer${num}`]}
                    onChange={(e) => setFormData(prev => ({ ...prev, [`answer${num}`]: e.target.value }))}
                    placeholder="Your answer"
                    required
                    disabled={loading}
                  />
                </div>
              </div>
            ))}
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || (passwordStrength && !passwordStrength.allMet)}
          >
            {loading ? 'Setting up...' : 'Complete Setup'}
          </button>
        </form>

        <div className="auth-footer">
          <p className="info-text">
            ⚠️ <strong>Important:</strong> Remember your master password. It cannot be recovered without security questions.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MasterPasswordSetup;
