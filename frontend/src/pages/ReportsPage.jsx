import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import { useLanguage } from '../context/LanguageContext';
import '../styles/Dashboard.css';

const ReportsPage = () => {
    const today = new Date().toISOString().split('T')[0];
    const [startDate, setStartDate] = useState(today);
    const [endDate, setEndDate] = useState(today);
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { t, language } = useLanguage();

    const generateReport = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        setError('');
        setReportData(null);

        try {
            const token = localStorage.getItem('access_token');
            const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

            const response = await fetch(`${API_URL}/daybook/reports`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate
                })
            });

            if (response.ok) {
                const data = await response.json();
                setReportData(data);
            } else {
                const err = await response.json();
                setError(err.detail || 'Failed to generate report');
            }
        } catch (err) {
            setError(t('connectionError'));
            console.error('Report error:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatAmount = (amount) => {
        return parseFloat(amount).toLocaleString(language === 'hi' ? 'hi-IN' : 'en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        // Debug log
        // console.log('Formatting date:', dateStr);

        // Manual parsing to avoid timezone issues completely
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            const year = parseInt(parts[0]);
            const month = parseInt(parts[1]) - 1;
            const day = parseInt(parts[2]);
            const date = new Date(year, month, day);

            return date.toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en-IN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }

        // Fallback
        const date = new Date(dateStr);
        return date.toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div className="dashboard-container">
            <Navigation />

            <main className="dashboard-main">
                <div className="date-section" style={{ justifyContent: 'center', gap: '20px', marginBottom: '30px' }}>
                    <div className="date-inputs" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="date-picker"
                        />
                        <span style={{ color: '#64748b' }}>{t('to')}</span>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="date-picker"
                        />
                    </div>

                    <button onClick={generateReport} className="add-entry-button" disabled={loading}>
                        {loading ? t('generating') : t('generateReport')}
                    </button>
                </div>

                {error && (
                    <div className="error-banner">
                        {error}
                    </div>
                )}

                {reportData && (
                    <>
                        {/* Summary Cards */}
                        <div className="balance-cards">
                            <div className="balance-card opening">
                                <div className="card-content">
                                    <h3>{t('openingBalance')}</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.opening_balance)}</p>
                                    <p className="card-subtitle">{formatDate(reportData.period_start)}</p>
                                </div>
                            </div>
                            <div className="balance-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
                                <div className="card-content">
                                    <h3>{t('totalIn')}</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.total_debit)}</p>
                                </div>
                            </div>
                            <div className="balance-card" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: 'white' }}>
                                <div className="card-content">
                                    <h3>{t('totalOut')}</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.total_credit)}</p>
                                </div>
                            </div>
                            <div className="balance-card closing">
                                <div className="card-content">
                                    <h3>{t('closingBalance')}</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.closing_balance)}</p>
                                    <p className="card-subtitle">{formatDate(reportData.period_end)}</p>
                                </div>
                            </div>
                        </div>

                        {/* Entries Table */}
                        <div className="entries-section">
                            <div className="section-header" style={{ justifyContent: 'space-between', width: '100%' }}>
                                <h3>{t('detailedTransactions')} ({reportData.summary.entry_count})</h3>
                                <button
                                    onClick={() => window.print()}
                                    className="add-entry-button print-hide"
                                    style={{ background: '#475569' }}
                                >
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                                    </svg>
                                    {t('printReport')}
                                </button>
                            </div>

                            {reportData.entries.length > 0 ? (
                                <div className="entries-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>{t('date')}</th>
                                                <th>{t('entryNo')}</th>
                                                <th>{t('description')}</th>
                                                <th>{t('reference')}</th>
                                                <th className="amount-col">{t('debit')}</th>
                                                <th className="amount-col">{t('credit')}</th>
                                                <th className="amount-col">{t('runBal')}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reportData.entries.map((entry) => (
                                                <tr key={entry.id}>
                                                    <td style={{ fontSize: '0.9em', color: '#64748b' }}>
                                                        {formatDate(entry.date)}
                                                    </td>
                                                    <td className="entry-number">{entry.entry_number}</td>
                                                    <td>{entry.description}</td>
                                                    <td className="reference">{entry.reference || '-'}</td>
                                                    <td className="amount-col debit">
                                                        {parseFloat(entry.debit_amount) > 0 ? `₹ ${formatAmount(entry.debit_amount)}` : '-'}
                                                    </td>
                                                    <td className="amount-col credit">
                                                        {parseFloat(entry.credit_amount) > 0 ? `₹ ${formatAmount(entry.credit_amount)}` : '-'}
                                                    </td>
                                                    <td className="amount-col balance">₹ {formatAmount(entry.balance)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <h4>{t('noTransactions')}</h4>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </main>
        </div>
    );
};

export default ReportsPage;
