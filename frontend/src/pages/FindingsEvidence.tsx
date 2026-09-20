import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSessionStatus } from '../api/sessions';
import type { Session, Finding } from '../api/types';

export default function FindingsEvidence() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFinding, setExpandedFinding] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getSessionStatus(sessionId)
      .then((data) => {
        setSession(data);
        setLoading(false);
        // Auto-expand first finding
        if (data.findings && data.findings.length > 0) {
          setExpandedFinding(data.findings[0].findingId);
        }
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
        <span className="loading-text">Loading findings…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>{error}</span>
      </div>
    );
  }

  const findings = session?.findings || [];

  const severityOrder: Record<string, number> = { BLOCKING: 0, WARNING: 1, REVIEW: 2 };
  const sorted = [...findings].sort(
    (a, b) => (severityOrder[a.severity] ?? 3) - (severityOrder[b.severity] ?? 3)
  );

  const severityColor = (s: string) =>
    s === 'BLOCKING' ? 'var(--danger)' : s === 'WARNING' ? 'var(--warning)' : 'var(--info)';

  const severityBg = (s: string) =>
    s === 'BLOCKING' ? 'var(--danger-surface)' : s === 'WARNING' ? 'var(--warning-surface)' : 'var(--info-surface)';

  return (
    <div className="animate-in">
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Findings & Evidence</h1>
            <p className="page-subtitle">
              Session: <code className="body-sm">{sessionId}</code> •{' '}
              {findings.length} finding{findings.length !== 1 ? 's' : ''}
            </p>
          </div>
          <button className="btn btn-ghost" onClick={() => navigate(`/result/${sessionId}`)}>
            ← Back to Result
          </button>
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon" style={{ background: 'var(--success-surface)' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h3 className="empty-state-title">No findings</h3>
            <p className="empty-state-desc">All verification checks passed without issues.</p>
          </div>
        </div>
      ) : (
        <div className="stack gap-md stagger">
          {sorted.map((finding: Finding, i: number) => {
            const isExpanded = expandedFinding === finding.findingId;

            return (
              <div
                className="card animate-in"
                key={finding.findingId}
                style={{
                  animationDelay: `${i * 0.08}s`,
                  borderLeft: `4px solid ${severityColor(finding.severity)}`,
                }}
              >
                {/* Header */}
                <div
                  className="flex-between"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setExpandedFinding(isExpanded ? null : finding.findingId)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span
                      className="badge"
                      style={{
                        background: severityBg(finding.severity),
                        color: severityColor(finding.severity),
                      }}
                    >
                      <span className="badge-dot" style={{ background: severityColor(finding.severity) }} />
                      {finding.severity}
                    </span>
                    <code className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                      {finding.findingId}
                    </code>
                    <span className="body-sm" style={{ color: 'var(--outline)' }}>•</span>
                    <span className="body-sm" style={{ color: 'var(--on-surface-variant)', textTransform: 'capitalize' }}>
                      Rule: {finding.ruleId}
                    </span>
                  </div>
                  <svg
                    width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--outline)" strokeWidth="2"
                    style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>

                {/* Message */}
                <p className="body-md" style={{ fontWeight: 500, marginTop: '0.75rem' }}>
                  {finding.deterministicMessage}
                </p>

                {finding.deterministicMessageHi && (
                  <p className="body-sm" style={{ color: 'var(--on-surface-variant)', marginTop: '0.25rem', fontStyle: 'italic' }}>
                    {finding.deterministicMessageHi}
                  </p>
                )}

                {/* Expanded Details */}
                {isExpanded && (
                  <div style={{ marginTop: 'var(--space-md)' }}>
                    {/* Explanation */}
                    {finding.explanation && (
                      <div style={{
                        padding: 'var(--space-md)',
                        background: 'var(--surface-container)',
                        borderRadius: 'var(--radius)',
                        marginBottom: 'var(--space-md)',
                      }}>
                        <div className="label-md" style={{ marginBottom: '0.375rem' }}>EXPLANATION</div>
                        <p className="body-md">{finding.explanation}</p>
                      </div>
                    )}

                    {/* Action Steps */}
                    {finding.actionSteps && finding.actionSteps.length > 0 && (
                      <div style={{ marginBottom: 'var(--space-md)' }}>
                        <div className="label-md" style={{ marginBottom: '0.5rem' }}>RESOLUTION STEPS</div>
                        <ol style={{ paddingLeft: '1.25rem' }} className="stack gap-xs">
                          {finding.actionSteps.map((step, j) => (
                            <li key={j} className="body-md" style={{ color: 'var(--on-surface)' }}>
                              {step}
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {/* Evidence */}
                    {finding.evidence && finding.evidence.length > 0 && (
                      <div>
                        <div className="label-md" style={{ marginBottom: '0.5rem' }}>EVIDENCE</div>
                        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Document</th>
                                <th>Field</th>
                                <th>Value</th>
                                <th>Confidence</th>
                              </tr>
                            </thead>
                            <tbody>
                              {finding.evidence.map((ev, k) => (
                                <tr key={k}>
                                  <td>
                                    <span className="badge badge-neutral" style={{ textTransform: 'capitalize' }}>
                                      {ev.documentType.replace(/_/g, ' ')}
                                    </span>
                                  </td>
                                  <td className="body-sm">{ev.fieldName}</td>
                                  <td>
                                    <strong>{ev.value}</strong>
                                  </td>
                                  <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      <div className="progress-track" style={{ width: '60px' }}>
                                        <div
                                          className="progress-fill"
                                          style={{ width: `${ev.confidence}%` }}
                                        />
                                      </div>
                                      <span className="body-sm">{ev.confidence}%</span>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Footer Actions */}
      <div className="flex-between" style={{ marginTop: 'var(--space-xl)' }}>
        <button className="btn btn-ghost" onClick={() => navigate(`/result/${sessionId}`)}>
          ← Back to Result
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => navigate(`/progress/${sessionId}`)}
        >
          Re-verify Documents
        </button>
      </div>
    </div>
  );
}
