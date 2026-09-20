import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSessionStatus } from '../api/sessions';
import StatusBadge from '../components/StatusBadge';
import type { Session } from '../api/types';

export default function VerificationResult() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    getSessionStatus(sessionId)
      .then((data) => {
        setSession(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [sessionId]);

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        <span className="loading-text">Loading verification results…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="animate-in">
        <div className="error-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <strong>Error loading results:</strong> {error}
            <br />
            <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!session) return null;

  const readiness = session.readinessStatus || session.status || 'UNKNOWN';
  const findings = session.findings || [];
  const blockingFindings = findings.filter((f) => f.severity === 'BLOCKING');
  const warningFindings = findings.filter((f) => f.severity === 'WARNING');
  const reviewFindings = findings.filter((f) => f.severity === 'REVIEW');

  const verdictConfig: Record<string, { color: string; bg: string; icon: React.ReactNode; title: string; desc: string }> = {
    GREEN: {
      color: 'var(--success)',
      bg: 'var(--success-surface)',
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      ),
      title: 'Application Verified',
      desc: 'All documents passed verification checks. Your application is ready.',
    },
    RED: {
      color: 'var(--danger)',
      bg: 'var(--danger-surface)',
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" strokeWidth="2">
          <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      ),
      title: 'Issues Found',
      desc: 'Document verification found blocking issues that must be resolved.',
    },
    AMBER: {
      color: 'var(--warning)',
      bg: 'var(--warning-surface)',
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" strokeWidth="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
      title: 'Under Review',
      desc: 'Some documents require manual review or have warnings.',
    },
  };

  const verdict = verdictConfig[readiness] || verdictConfig.AMBER;

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Verification Result</h1>
            <p className="page-subtitle">
              Session: <code className="body-sm">{sessionId}</code>
            </p>
          </div>
          <StatusBadge status={readiness} />
        </div>
      </div>

      {/* Verdict Banner */}
      <div
        className="card"
        style={{
          background: verdict.bg,
          border: `1px solid ${verdict.color}20`,
          textAlign: 'center',
          marginBottom: 'var(--space-xl)',
          padding: 'var(--space-xl)',
        }}
      >
        <div style={{ margin: '0 auto 1rem' }}>{verdict.icon}</div>
        <h2 className="headline-lg" style={{ color: verdict.color, marginBottom: '0.5rem' }}>
          {verdict.title}
        </h2>
        <p className="body-lg" style={{ color: 'var(--on-surface-variant)', maxWidth: '480px', margin: '0 auto' }}>
          {verdict.desc}
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid-3" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.25rem' }}>
            BLOCKING
          </div>
          <div className="headline-xl" style={{ color: blockingFindings.length > 0 ? 'var(--danger)' : 'var(--success)' }}>
            {blockingFindings.length}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.25rem' }}>
            WARNINGS
          </div>
          <div className="headline-xl" style={{ color: warningFindings.length > 0 ? 'var(--warning)' : 'var(--success)' }}>
            {warningFindings.length}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div className="label-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '0.25rem' }}>
            REVIEW
          </div>
          <div className="headline-xl" style={{ color: reviewFindings.length > 0 ? 'var(--info)' : 'var(--success)' }}>
            {reviewFindings.length}
          </div>
        </div>
      </div>

      {/* Findings List */}
      {findings.length > 0 && (
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <div className="flex-between" style={{ marginBottom: 'var(--space-md)' }}>
            <h2 className="headline-md">Findings</h2>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => navigate(`/findings/${sessionId}`)}
            >
              View Detailed Evidence →
            </button>
          </div>

          <div className="stack gap-sm stagger">
            {findings.map((finding, i) => {
              const severityBadge =
                finding.severity === 'BLOCKING' ? 'badge-red' :
                finding.severity === 'WARNING' ? 'badge-amber' : 'badge-blue';

              return (
                <div
                  className="card animate-in"
                  key={finding.findingId}
                  style={{ animationDelay: `${i * 0.08}s`, cursor: 'pointer' }}
                  onClick={() => navigate(`/findings/${sessionId}`)}
                >
                  <div className="flex-between" style={{ marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <code className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                        {finding.findingId}
                      </code>
                      <span className="body-sm" style={{ color: 'var(--outline)' }}>•</span>
                      <span className="body-sm" style={{ color: 'var(--on-surface-variant)', textTransform: 'capitalize' }}>
                        {finding.category}
                      </span>
                    </div>
                    <span className={`badge ${severityBadge}`}>
                      <span className="badge-dot" />
                      {finding.severity}
                    </span>
                  </div>
                  <p className="body-md" style={{ fontWeight: 500 }}>
                    {finding.deterministicMessage}
                  </p>
                  {finding.explanation && (
                    <p className="body-sm" style={{ color: 'var(--on-surface-variant)', marginTop: '0.375rem' }}>
                      {finding.explanation}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* No findings */}
      {findings.length === 0 && readiness === 'GREEN' && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon" style={{ background: 'var(--success-surface)' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h3 className="empty-state-title">No Issues Found</h3>
            <p className="empty-state-desc">
              All cross-document checks passed. Names, dates, and validity rules are consistent.
            </p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex-between" style={{ marginTop: 'var(--space-xl)' }}>
        <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary"
            onClick={() => navigate(`/progress/${sessionId}`)}
          >
            Re-verify
          </button>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/new')}
          >
            New Application
          </button>
        </div>
      </div>
    </div>
  );
}
