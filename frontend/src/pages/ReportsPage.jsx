import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import { useLanguage } from '../context/LanguageContext';
import '../styles/Dashboard.css';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

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
            const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

            const response = await fetch(`${API_URL}/daybook/reports`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
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

                        {/* Credit vs Debit Comparison Charts */}
                        <div className="charts-section" style={{ marginBottom: '40px' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
                                {/* Bar Chart */}
                                <div className="entries-section" style={{ marginBottom: 0 }}>
                                    <h3 style={{ marginBottom: '20px', fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>
                                        {t('creditVsDebit') || 'Credit vs Debit Comparison'}
                                    </h3>
                                    <Bar
                                        data={{
                                            labels: [t('totalIn') || 'Total In (Debit)', t('totalOut') || 'Total Out (Credit)'],
                                            datasets: [{
                                                label: language === 'hi' ? 'राशि (₹)' : 'Amount (₹)',
                                                data: [
                                                    parseFloat(reportData.summary.total_debit),
                                                    parseFloat(reportData.summary.total_credit)
                                                ],
                                                backgroundColor: [
                                                    'rgba(16, 185, 129, 0.8)',
                                                    'rgba(239, 68, 68, 0.8)'
                                                ],
                                                borderColor: [
                                                    'rgb(16, 185, 129)',
                                                    'rgb(239, 68, 68)'
                                                ],
                                                borderWidth: 2,
                                                borderRadius: 8,
                                            }]
                                        }}
                                        options={{
                                            responsive: true,
                                            maintainAspectRatio: true,
                                            plugins: {
                                                legend: {
                                                    display: false
                                                },
                                                tooltip: {
                                                    callbacks: {
                                                        label: function(context) {
                                                            return `${context.dataset.label}: ₹ ${formatAmount(context.parsed.y)}`;
                                                        }
                                                    }
                                                }
                                            },
                                            scales: {
                                                y: {
                                                    beginAtZero: true,
                                                    ticks: {
                                                        callback: function(value) {
                                                            return '₹ ' + formatAmount(value);
                                                        }
                                                    }
                                                }
                                            }
                                        }}
                                    />
                                </div>

                                {/* Doughnut Chart */}
                                <div className="entries-section" style={{ marginBottom: 0 }}>
                                    <h3 style={{ marginBottom: '20px', fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>
                                        {t('transactionDistribution') || 'Transaction Distribution'}
                                    </h3>
                                    <div style={{ maxWidth: '350px', margin: '0 auto' }}>
                                        <Doughnut
                                            data={{
                                                labels: [t('totalIn') || 'Total In', t('totalOut') || 'Total Out'],
                                                datasets: [{
                                                    data: [
                                                        parseFloat(reportData.summary.total_debit),
                                                        parseFloat(reportData.summary.total_credit)
                                                    ],
                                                    backgroundColor: [
                                                        'rgba(16, 185, 129, 0.8)',
                                                        'rgba(239, 68, 68, 0.8)'
                                                    ],
                                                    borderColor: [
                                                        'rgb(16, 185, 129)',
                                                        'rgb(239, 68, 68)'
                                                    ],
                                                    borderWidth: 2,
                                                }]
                                            }}
                                            options={{
                                                responsive: true,
                                                maintainAspectRatio: true,
                                                plugins: {
                                                    legend: {
                                                        position: 'bottom',
                                                        labels: {
                                                            padding: 20,
                                                            font: {
                                                                size: 14,
                                                                weight: '600'
                                                            }
                                                        }
                                                    },
                                                    tooltip: {
                                                        callbacks: {
                                                            label: function(context) {
                                                                const total = parseFloat(reportData.summary.total_debit) + parseFloat(reportData.summary.total_credit);
                                                                const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                                                return `${context.label}: ₹ ${formatAmount(context.parsed)} (${percentage}%)`;
                                                            }
                                                        }
                                                    }
                                                }
                                            }}
                                        />
                                    </div>
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
