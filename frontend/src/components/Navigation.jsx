import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Dashboard.css'; // Reusing header styles

const Navigation = ({ username, onLogout }) => {
    const location = useLocation();

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
                        <h1 className="app-title">DayBookKeeper</h1>
                        <p className="app-subtitle">by WarryWorks</p>
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
                        Dashboard
                    </Link>
                    <Link
                        to="/reports"
                        style={{
                            color: location.pathname === '/reports' ? '#2563eb' : '#64748b',
                            fontWeight: location.pathname === '/reports' ? '600' : '500',
                            textDecoration: 'none'
                        }}
                    >
                        Reports
                    </Link>
                </nav>
            </div>

            <div className="header-right">
                <div className="user-info">
                    <svg className="user-icon" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <span>{username}</span>
                </div>
                <button onClick={onLogout} className="logout-button">
                    <svg fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
                    </svg>
                    Logout
                </button>
            </div>
        </header>
    );
};

export default Navigation;
