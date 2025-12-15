/**
 * Main Application Component
 * Daybook Desktop Application v1.1
 */

import React, { useState, useEffect } from 'react';
import './styles/App.css';
import { daybookAPI } from './services/api';
import EntryForm from './components/EntryForm';
import EntriesTable from './components/EntriesTable';
import Summary from './components/Summary';

function App() {
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);

  // Load entries on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load entries and summary
      const [entriesResponse, summaryResponse] = await Promise.all([
        daybookAPI.getEntries(),
        daybookAPI.getSummary()
      ]);

      if (entriesResponse.success) {
        setEntries(entriesResponse.entries);
      }

      if (summaryResponse.success) {
        setSummary(summaryResponse.summary);
      }

      setLoading(false);
    } catch (err) {
      setError('Failed to load data. Make sure the backend server is running.');
      setLoading(false);
      console.error('Error loading data:', err);
    }
  };

  const handleCreateEntry = async (entryData) => {
    try {
      setError(null);
      const response = await daybookAPI.createEntry(entryData);

      if (response.success) {
        setSuccess('Entry created successfully!');
        setTimeout(() => setSuccess(null), 3000);
        await loadData();
      } else {
        setError(response.error || 'Failed to create entry');
      }
    } catch (err) {
      setError('Failed to create entry. Please try again.');
      console.error('Error creating entry:', err);
    }
  };

  const handleUpdateEntry = async (entryData) => {
    try {
      setError(null);
      const response = await daybookAPI.updateEntry(editingEntry.entry_id, entryData);

      if (response.success) {
        setSuccess('Entry updated successfully!');
        setTimeout(() => setSuccess(null), 3000);
        setEditingEntry(null);
        await loadData();
      } else {
        setError(response.error || 'Failed to update entry');
      }
    } catch (err) {
      setError('Failed to update entry. Please try again.');
      console.error('Error updating entry:', err);
    }
  };

  const handleDeleteEntry = async (entryId) => {
    try {
      setError(null);
      const response = await daybookAPI.deleteEntry(entryId);

      if (response.success) {
        setSuccess('Entry deleted successfully!');
        setTimeout(() => setSuccess(null), 3000);
        await loadData();
      } else {
        setError(response.error || 'Failed to delete entry');
      }
    } catch (err) {
      setError('Failed to delete entry. Please try again.');
      console.error('Error deleting entry:', err);
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCancelEdit = () => {
    setEditingEntry(null);
  };

  if (loading) {
    return (
      <div className="App">
        <header className="app-header">
          <h1>Daybook Desktop Application</h1>
          <p>Version 1.1 - Real-Time Excel Synchronization</p>
        </header>
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Daybook Desktop Application</h1>
        <p>Version 1.1 - Real-Time Excel Synchronization</p>
      </header>

      <main className="main-container">
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <Summary summary={summary} />

        <EntryForm
          onSubmit={editingEntry ? handleUpdateEntry : handleCreateEntry}
          editingEntry={editingEntry}
          onCancel={handleCancelEdit}
        />

        <EntriesTable
          entries={entries}
          onEdit={handleEdit}
          onDelete={handleDeleteEntry}
        />
      </main>
    </div>
  );
}

export default App;
