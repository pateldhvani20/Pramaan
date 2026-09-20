import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSessionStatus } from '../api/sessions';
import { useApp } from '../context/AppContext';
import StatusBadge from '../components/StatusBadge';

export default function MyApplications() {
  const navigate = useNavigate();
  const { savedSessions, updateSavedSessionStatus } = useApp();
  const [refreshing, setRefreshing] = useState(false);

  // Refresh all session statuses from backend
  const refreshAll = async () => {
    setRefreshing(true);
    for (const session of savedSessions) {
      try {
        const data = await getSessionStatus(session.sessionId);
        const status = data.readinessStatus || data.status || session.status;
        updateSavedSessionStatus(session.sessionId, status);
      } catch {
        // Keep existing status on error
      }
    }
    setRefreshing(false);
  };

  // Auto-refresh on mount
  useEffect(() => {
    if (savedSessions.length > 0) {
      refreshAll();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">My Applications</h1>
            <p className="page-subtitle">
              {savedSessions.length} application{savedSessions.length !== 1 ? 's' : ''} tracked
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={refreshAll}
              disabled={refreshing}
            >
              {refreshing ? (
                <>
                  <div className="spinner spinner-sm" />
                  Refreshing…
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="23 4 23 10 17 10" />
                    <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
                  </svg>
                  Refresh Status
                </>
              )}
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/new')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              New Application
            </button>
          </div>
        </div>
      </div>

      {savedSessions.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
              </svg>
            </div>
            <h3 className="empty-state-title">No applications yet</h3>
            <p className="empty-state-desc">
              Create your first verification application to get started. All your sessions will appear here.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/new')}>
              Create Application
            </button>
          </div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>Profile</th>
                <th>Created</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {savedSessions.map((session) => (
                <tr key={session.sessionId}>
                  <td>
                    <code className="body-sm" style={{ fontFamily: 'monospace' }}>
                      {session.sessionId.slice(0, 16)}…
                    </code>
                  </td>
                  <td>
                    <span style={{ textTransform: 'capitalize' }}>
                      {session.profileId.replace(/-/g, ' ').replace(/v\d+$/, '')}
                    </span>
                  </td>
                  <td className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                    {new Date(session.createdAt).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td>
                    <StatusBadge status={session.status} />
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => navigate(`/result/${session.sessionId}`)}
                      >
                        View
                      </button>
                      {session.status === 'CREATED' && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => navigate(`/upload/${session.sessionId}`)}
                        >
                          Upload
                        </button>
                      )}
                      {['RED', 'AMBER'].includes(session.status) && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => navigate(`/progress/${session.sessionId}`)}
                        >
                          Re-verify
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
