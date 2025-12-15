import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import '../styles/Dashboard.css'; // Reusing header styles

const Navigation = () => {
    const location = useLocation();
    const { language, toggleLanguage, t } = useLanguage();

    return (
        <header className="dashboard-header">
            <div className="header-left">
                <Link to="/" className="logo-section" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <svg className="header-logo" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                        />
                    </svg>
                    <div>
                        <h1 className="app-title">{t('appTitle')}</h1>
                        <p className="app-subtitle">{t('subtitle')}</p>
                    </div>
                </Link>
                <nav className="nav-links" style={{ marginLeft: '40px', display: 'flex', gap: '20px' }}>
                    <Link
                        to="/"
                        style={{
                            color: location.pathname === '/' ? '#2563eb' : '#64748b',
                            fontWeight: location.pathname === '/' ? '600' : '500',
                            textDecoration: 'none'
                        }}
                    >
                        {t('dashboard')}
                    </Link>
                    <Link
                        to="/reports"
                        style={{
                            color: location.pathname === '/reports' ? '#2563eb' : '#64748b',
                            fontWeight: location.pathname === '/reports' ? '600' : '500',
                            textDecoration: 'none'
                        }}
                    >
                        {t('reports')}
                    </Link>
                </nav>
            </div>

            <div className="header-right">
                <button
                    onClick={toggleLanguage}
                    className="logout-button"
                    style={{
                        background: '#f1f5f9',
                        color: '#475569',
                        border: '1px solid #e2e8f0',
                        fontSize: '0.9rem',
                        padding: '6px 12px'
                    }}
                >
                    <span style={{ marginRight: '6px' }}>🌐</span>
                    {language === 'en' ? 'हिन्दी' : 'English'}
                </button>
            </div>
        </header>
    );
};

export default Navigation;
