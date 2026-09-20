import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { runVerification } from '../api/verification';
import { getSessionStatus } from '../api/sessions';
import { useApp } from '../context/AppContext';

const PIPELINE_STEPS = [
  { key: 'ingest', label: 'Ingestion Gate', desc: 'Validating file integrity, MIME type, and PDF structure' },
  { key: 'extract', label: 'Text Extraction', desc: 'Running Amazon Textract for OCR and field extraction' },
  { key: 'classify', label: 'Classification', desc: 'Identifying document type from extracted signals' },
  { key: 'complete', label: 'Completeness Check', desc: 'Verifying all required fields are present' },
  { key: 'verify', label: 'Verification Engine', desc: 'Cross-document name, DOB, and validity checks' },
  { key: 'explain', label: 'Explanation', desc: 'Generating human-readable explanations via Bedrock' },
  { key: 'persist', label: 'Persist Results', desc: 'Saving findings to DynamoDB' },
  { key: 'cleanup', label: 'Secure Cleanup', desc: 'Deleting raw documents from S3' },
];

export default function VerificationProgress() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { updateSavedSessionStatus } = useApp();

  const [status, setStatus] = useState<'idle' | 'starting' | 'running' | 'done' | 'error'>('idle');
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [resultStatus, setResultStatus] = useState<string>('');
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Start verification and begin polling
  const startVerification = async () => {
    if (!sessionId) return;
    setStatus('starting');
    setError(null);

    try {
      await runVerification(sessionId);
      setStatus('running');
      setCurrentStep(0);

      // Simulate step progression while polling for real results
      const stepInterval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < PIPELINE_STEPS.length - 1) return prev + 1;
          return prev;
        });
      }, 2000);

      // Poll for real status
      pollRef.current = setInterval(async () => {
        try {
          const session = await getSessionStatus(sessionId);
          const readiness = session.readinessStatus || session.status;

          if (readiness && readiness !== 'CREATED' && readiness !== 'RUNNING') {
            // Verification complete
            clearInterval(stepInterval);
            if (pollRef.current) clearInterval(pollRef.current);

            setCurrentStep(PIPELINE_STEPS.length);
            setResultStatus(readiness);
            setStatus('done');
            updateSavedSessionStatus(sessionId, readiness);
          }
        } catch {
          // Keep polling on transient errors
        }
      }, 3000);

      // Safety timeout — stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(stepInterval);
        if (pollRef.current) clearInterval(pollRef.current);
        setCurrentStep(PIPELINE_STEPS.length);
        setStatus('done');
      }, 120000);

    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start verification');
      setStatus('error');
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // Auto-start
  useEffect(() => {
    if (status === 'idle') {
      startVerification();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Verification in Progress</h1>
        <p className="page-subtitle">
          Session: <code className="body-sm">{sessionId}</code>
        </p>
      </div>

      {error && (
        <div className="error-box" style={{ marginBottom: 'var(--space-lg)' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <strong>Error:</strong> {error}
            <br />
            <button className="btn btn-ghost btn-sm" style={{ marginTop: '0.5rem' }} onClick={startVerification}>
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="card" style={{ maxWidth: '640px' }}>
        <div className="stack gap-xs">
          {PIPELINE_STEPS.map((step, i) => {
            const isActive = i === currentStep && status === 'running';
            const isDone = i < currentStep || status === 'done';
            const isPending = i > currentStep;

            return (
              <div
                key={step.key}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius)',
                  background: isActive ? 'rgba(138, 48, 127, 0.04)' : 'transparent',
                  transition: 'all 0.3s ease',
                }}
              >
                {/* Step Icon */}
                <div style={{ flexShrink: 0, marginTop: '2px' }}>
                  {isDone ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5">
                      <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                  ) : isActive ? (
                    <div className="spinner spinner-sm" />
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--outline)" strokeWidth="1.5">
                      <circle cx="12" cy="12" r="10" />
                    </svg>
                  )}
                </div>

                {/* Step Text */}
                <div>
                  <div
                    className="body-md"
                    style={{
                      fontWeight: isActive || isDone ? 600 : 400,
                      color: isPending ? 'var(--outline)' : 'var(--on-surface)',
                    }}
                  >
                    {step.label}
                  </div>
                  <div className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                    {step.desc}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Overall Progress */}
        <div style={{ marginTop: 'var(--space-lg)' }}>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{
                width: `${status === 'done' ? 100 : (currentStep / PIPELINE_STEPS.length) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Done state */}
        {status === 'done' && (
          <div style={{ marginTop: 'var(--space-lg)', textAlign: 'center' }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" style={{ margin: '0 auto 1rem' }}>
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <h3 className="headline-md" style={{ marginBottom: '0.5rem' }}>
              Verification Complete
            </h3>
            <p className="body-md" style={{ color: 'var(--on-surface-variant)', marginBottom: '1rem' }}>
              {resultStatus === 'GREEN'
                ? 'All checks passed. Your documents are verified.'
                : resultStatus === 'RED'
                  ? 'Issues were found. Review the findings.'
                  : 'Verification completed. Review your results.'}
            </p>
            <button
              className="btn btn-primary btn-lg"
              onClick={() => navigate(`/result/${sessionId}`)}
            >
              View Results
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
