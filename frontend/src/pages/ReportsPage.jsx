import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import '../styles/Dashboard.css';

const ReportsPage = ({ onLogout }) => {
    const today = new Date().toISOString().split('T')[0];
    const [startDate, setStartDate] = useState(today);
    const [endDate, setEndDate] = useState(today);
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const username = localStorage.getItem('username') || 'Admin';

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
            } else if (response.status === 401) {
                onLogout();
            } else {
                const err = await response.json();
                setError(err.detail || 'Failed to generate report');
            }
        } catch (err) {
            setError('Connection error. Please try again.');
            console.error('Report error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handlePreset = (type) => {
        const end = new Date();
        let start = new Date();

        if (type === 'week') {
            // Last 7 days
            start.setDate(end.getDate() - 6);
        } else if (type === 'month') {
            // First day of current month
            start.setDate(1);
        }

        setStartDate(start.toISOString().split('T')[0]);
        setEndDate(end.toISOString().split('T')[0]);
        // Optionally trigger generate immediately
    };

    const formatAmount = (amount) => {
        return parseFloat(amount).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div className="dashboard-container">
            <Navigation username={username} onLogout={onLogout} />

            <main className="dashboard-main">
                <div className="date-section" style={{ justifyContent: 'center', gap: '20px', marginBottom: '30px' }}>
                    <div className="date-inputs" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="date-picker"
                        />
                        <span style={{ color: '#64748b' }}>to</span>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="date-picker"
                        />
                    </div>

                    <button onClick={generateReport} className="add-entry-button" disabled={loading}>
                        {loading ? 'Generating...' : 'Generate Report'}
                    </button>

                    <div className="presets" style={{ display: 'flex', gap: '10px' }}>
                        <button
                            onClick={() => handlePreset('week')}
                            className="date-nav-button"
                            style={{ padding: '8px 16px' }}
                        >
                            This Week
                        </button>
                        <button
                            onClick={() => handlePreset('month')}
                            className="date-nav-button"
                            style={{ padding: '8px 16px' }}
                        >
                            This Month
                        </button>
                    </div>
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
                                    <h3>Opening Balance</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.opening_balance)}</p>
                                    <p className="card-subtitle">{formatDate(reportData.period_start)}</p>
                                </div>
                            </div>
                            <div className="balance-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
                                <div className="card-content">
                                    <h3>Total In (Debit)</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.total_debit)}</p>
                                </div>
                            </div>
                            <div className="balance-card" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: 'white' }}>
                                <div className="card-content">
                                    <h3>Total Out (Credit)</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.total_credit)}</p>
                                </div>
                            </div>
                            <div className="balance-card closing">
                                <div className="card-content">
                                    <h3>Closing Balance</h3>
                                    <p className="amount">₹ {formatAmount(reportData.summary.closing_balance)}</p>
                                    <p className="card-subtitle">{formatDate(reportData.period_end)}</p>
                                </div>
                            </div>
                        </div>

                        {/* Entries Table */}
                        <div className="entries-section">
                            <div className="section-header">
                                <h3>Detailed Transactions ({reportData.summary.entry_count})</h3>
                            </div>

                            {reportData.entries.length > 0 ? (
                                <div className="entries-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Entry No.</th>
                                                <th>Description</th>
                                                <th>Reference</th>
                                                <th className="amount-col">Debit</th>
                                                <th className="amount-col">Credit</th>
                                                <th className="amount-col">Run. Bal.</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reportData.entries.map((entry) => (
                                                <tr key={entry.id}>
                                                    <td style={{ fontSize: '0.9em', color: '#64748b' }}>
                                                        {formatDate(entry.created_at)}
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
                                    <h4>No transactions found in this period</h4>
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
