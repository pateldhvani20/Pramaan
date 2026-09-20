import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { listProfiles } from '../api/profiles';
import { createSession } from '../api/sessions';
import { useApp } from '../context/AppContext';
import type { Profile } from '../api/types';

export default function NewApplication() {
  const navigate = useNavigate();
  const location = useLocation();
  const { saveSession } = useApp();

  const preselectedProfile = (location.state as { profileId?: string })?.profileId || '';

  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState(preselectedProfile);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listProfiles()
      .then((data) => {
        setProfiles(data);
        if (!selectedProfile && data.length > 0) {
          setSelectedProfile(data[0].profileId);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [selectedProfile]);

  const handleCreate = async () => {
    if (!selectedProfile) return;
    setCreating(true);
    setError(null);

    try {
      const session = await createSession(selectedProfile);
      saveSession({
        sessionId: session.sessionId,
        profileId: session.profileId,
        createdAt: session.createdAt,
        status: session.status,
      });
      navigate(`/upload/${session.sessionId}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
      setCreating(false);
    }
  };

  const selected = profiles.find((p) => p.profileId === selectedProfile);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">New Application</h1>
        <p className="page-subtitle">Create a new document verification application</p>
      </div>

      {error && (
        <div className="error-box" style={{ marginBottom: 'var(--space-lg)' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      <div className="grid-2">
        {/* Left: Profile Selection */}
        <div className="card">
          <h2 className="headline-md" style={{ marginBottom: 'var(--space-lg)' }}>
            Select Verification Profile
          </h2>

          {loading ? (
            <div className="loading-overlay">
              <div className="spinner" />
              <span className="loading-text">Loading profiles…</span>
            </div>
          ) : (
            <div className="stack gap-sm">
              {profiles.map((profile) => (
                <label
                  key={profile.profileId}
                  className="card"
                  style={{
                    cursor: 'pointer',
                    border: selectedProfile === profile.profileId
                      ? '2px solid var(--primary)'
                      : '1px solid var(--neutral-border)',
                    padding: '1rem',
                    background: selectedProfile === profile.profileId
                      ? 'rgba(138, 48, 127, 0.04)'
                      : 'white',
                  }}
                  onClick={() => setSelectedProfile(profile.profileId)}
                >
                  <div className="flex-between">
                    <div>
                      <div className="title-lg">{profile.name}</div>
                      <div className="body-sm" style={{ color: 'var(--on-surface-variant)', marginTop: '0.25rem' }}>
                        {profile.requiredDocuments.length} documents required
                      </div>
                    </div>
                    <input
                      type="radio"
                      name="profile"
                      checked={selectedProfile === profile.profileId}
                      onChange={() => setSelectedProfile(profile.profileId)}
                      style={{ accentColor: 'var(--primary)', width: 18, height: 18 }}
                    />
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Right: Summary & Create */}
        <div className="card">
          <h2 className="headline-md" style={{ marginBottom: 'var(--space-lg)' }}>
            Application Summary
          </h2>

          {selected ? (
            <div className="stack gap-lg">
              <div>
                <div className="label-md" style={{ marginBottom: '0.25rem' }}>PROFILE</div>
                <div className="title-lg">{selected.name}</div>
                <div className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                  Ruleset Version: {selected.version}
                </div>
              </div>

              <div>
                <div className="label-md" style={{ marginBottom: '0.5rem' }}>REQUIRED DOCUMENTS</div>
                <div className="stack gap-xs">
                  {selected.requiredDocuments.map((doc) => (
                    <div
                      key={doc}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 0.75rem',
                        background: 'var(--surface-container)',
                        borderRadius: 'var(--radius)',
                      }}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <span className="body-md" style={{ textTransform: 'capitalize' }}>
                        {doc.replace(/_/g, ' ')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                className="btn btn-primary btn-lg"
                onClick={handleCreate}
                disabled={creating}
                style={{ width: '100%' }}
              >
                {creating ? (
                  <>
                    <div className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />
                    Creating Session…
                  </>
                ) : (
                  <>
                    Create Application
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="empty-state">
              <p className="body-md" style={{ color: 'var(--on-surface-variant)' }}>
                Select a verification profile to continue.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
