import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listProfiles } from '../api/profiles';
import { useApp } from '../context/AppContext';
import StatusBadge from '../components/StatusBadge';
import type { Profile } from '../api/types';

export default function Dashboard() {
  const navigate = useNavigate();
  const { profiles, setProfiles, savedSessions } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listProfiles()
      .then((data) => {
        setProfiles(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [setProfiles]);

  const recentSessions = savedSessions.slice(0, 5);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome to Pramaan — Intelligent Document Verification</p>
      </div>

      {/* ---- Stats ---- */}
      <div className="grid-4 stagger" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="card animate-in">
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.5rem' }}>
            TOTAL APPLICATIONS
          </div>
          <div className="headline-xl">{savedSessions.length}</div>
        </div>
        <div className="card animate-in">
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.5rem' }}>
            VERIFIED
          </div>
          <div className="headline-xl" style={{ color: 'var(--success)' }}>
            {savedSessions.filter((s) => s.status === 'GREEN').length}
          </div>
        </div>
        <div className="card animate-in">
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.5rem' }}>
            ISSUES FOUND
          </div>
          <div className="headline-xl" style={{ color: 'var(--danger)' }}>
            {savedSessions.filter((s) => s.status === 'RED').length}
          </div>
        </div>
        <div className="card animate-in">
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.5rem' }}>
            IN PROGRESS
          </div>
          <div className="headline-xl" style={{ color: 'var(--info)' }}>
            {savedSessions.filter((s) => ['RUNNING', 'CREATED', 'AMBER'].includes(s.status)).length}
          </div>
        </div>
      </div>

      {/* ---- Profiles ---- */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="flex-between" style={{ marginBottom: 'var(--space-md)' }}>
          <h2 className="headline-md">Verification Profiles</h2>
          <button className="btn btn-primary" onClick={() => navigate('/new')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Application
          </button>
        </div>

        {loading && (
          <div className="loading-overlay">
            <div className="spinner" />
            <span className="loading-text">Loading profiles from API…</span>
          </div>
        )}

        {error && (
          <div className="error-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div>
              <strong>Error loading profiles:</strong> {error}
              <br />
              <span className="body-sm">Check that VITE_API_BASE_URL is set correctly in your .env file.</span>
            </div>
          </div>
        )}

        {!loading && !error && (
          <div className="grid-2 stagger">
            {profiles.map((profile: Profile, i: number) => (
              <div
                className="card animate-in"
                key={profile.profileId}
                style={{ cursor: 'pointer', animationDelay: `${i * 0.1}s` }}
                onClick={() => navigate('/new', { state: { profileId: profile.profileId } })}
              >
                <div className="flex-between" style={{ marginBottom: '0.75rem' }}>
                  <h3 className="title-lg">{profile.name}</h3>
                  <span className="badge badge-green">
                    <span className="badge-dot" />
                    v{profile.version}
                  </span>
                </div>
                <p className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                  Required documents: {profile.requiredDocuments.join(', ')}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ---- Recent Applications ---- */}
      <div>
        <div className="flex-between" style={{ marginBottom: 'var(--space-md)' }}>
          <h2 className="headline-md">Recent Applications</h2>
          {savedSessions.length > 0 && (
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/applications')}>
              View All →
            </button>
          )}
        </div>

        {recentSessions.length === 0 ? (
          <div className="card">
            <div className="empty-state">
              <div className="empty-state-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                </svg>
              </div>
              <h3 className="empty-state-title">No applications yet</h3>
              <p className="empty-state-desc">
                Create your first verification application to get started.
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
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map((s) => (
                  <tr key={s.sessionId}>
                    <td>
                      <code className="body-sm">{s.sessionId.slice(0, 12)}…</code>
                    </td>
                    <td>{s.profileId}</td>
                    <td className="body-sm">{new Date(s.createdAt).toLocaleDateString()}</td>
                    <td><StatusBadge status={s.status} /></td>
                    <td>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => navigate(`/result/${s.sessionId}`)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
