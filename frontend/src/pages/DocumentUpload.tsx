import { useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getUploadCredentials, uploadFileToS3 } from '../api/uploads';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'done' | 'error';
  error?: string;
  documentType: string;
}

const DOCUMENT_TYPES = [
  { type: 'aadhaar', label: 'Aadhaar Card', accept: '.pdf,.jpg,.jpeg,.png' },
  { type: 'marksheet', label: 'Academic Marksheet', accept: '.pdf,.jpg,.jpeg,.png' },
  { type: 'income_certificate', label: 'Income Certificate', accept: '.pdf,.jpg,.jpeg,.png' },
  { type: 'domicile', label: 'Domicile Certificate', accept: '.pdf,.jpg,.jpeg,.png' },
];

export default function DocumentUpload() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const [uploads, setUploads] = useState<Record<string, UploadedFile>>({});
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((documentType: string, file: File) => {
    setUploads((prev) => ({
      ...prev,
      [documentType]: { file, status: 'pending', documentType },
    }));
  }, []);

  const handleDrop = useCallback((documentType: string, e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(documentType, file);
  }, [handleFileSelect]);

  const uploadAll = async () => {
    if (!sessionId) return;
    setUploading(true);
    setError(null);

    const entries = Object.entries(uploads).filter(([, u]) => u.status === 'pending');

    for (const [docType, uploadItem] of entries) {
      // Mark uploading
      setUploads((prev) => ({
        ...prev,
        [docType]: { ...prev[docType], status: 'uploading' },
      }));

      try {
        // 1. Get presigned credentials from backend
        const credentials = await getUploadCredentials(
          sessionId,
          uploadItem.file.name,
          uploadItem.file.type || 'application/pdf',
          docType
        );

        // 2. Upload directly to S3
        await uploadFileToS3(credentials, uploadItem.file);

        setUploads((prev) => ({
          ...prev,
          [docType]: { ...prev[docType], status: 'done' },
        }));
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Upload failed';
        setUploads((prev) => ({
          ...prev,
          [docType]: { ...prev[docType], status: 'error', error: msg },
        }));
        setError(`Failed to upload ${docType}: ${msg}`);
      }
    }

    setUploading(false);
  };

  const allUploaded = DOCUMENT_TYPES.every(
    (dt) => uploads[dt.type]?.status === 'done'
  );
  const anyPending = Object.values(uploads).some((u) => u.status === 'pending');
  const uploadedCount = Object.values(uploads).filter((u) => u.status === 'done').length;

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Upload Documents</h1>
        <p className="page-subtitle">
          Session: <code className="body-sm">{sessionId}</code>
        </p>
      </div>

      {/* Progress */}
      <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
        <div className="flex-between" style={{ marginBottom: '0.5rem' }}>
          <span className="label-md">UPLOAD PROGRESS</span>
          <span className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
            {uploadedCount}/{DOCUMENT_TYPES.length} documents
          </span>
        </div>
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${(uploadedCount / DOCUMENT_TYPES.length) * 100}%` }}
          />
        </div>
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

      {/* Upload Slots */}
      <div className="grid-2 stagger" style={{ marginBottom: 'var(--space-xl)' }}>
        {DOCUMENT_TYPES.map((dt, i) => {
          const upload = uploads[dt.type];
          return (
            <div key={dt.type} className="animate-in" style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="label-md" style={{ marginBottom: '0.5rem' }}>
                {dt.label.toUpperCase()}
              </div>
              {upload?.status === 'done' ? (
                <div
                  className="card"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    background: 'var(--success-surface)',
                    borderColor: 'rgba(46, 125, 99, 0.2)',
                  }}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <div>
                    <div className="body-md" style={{ fontWeight: 600, color: 'var(--success-text)' }}>
                      Uploaded
                    </div>
                    <div className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                      {upload.file.name}
                    </div>
                  </div>
                </div>
              ) : upload?.status === 'uploading' ? (
                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="spinner spinner-sm" />
                  <span className="body-md">Uploading {upload.file.name}…</span>
                </div>
              ) : upload?.status === 'error' ? (
                <div
                  className="card"
                  style={{ borderColor: 'rgba(186, 26, 26, 0.3)' }}
                  onClick={() => fileInputRefs.current[dt.type]?.click()}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--danger)' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" />
                      <line x1="9" y1="9" x2="15" y2="15" />
                    </svg>
                    <div>
                      <div className="body-md" style={{ fontWeight: 600 }}>Failed</div>
                      <div className="body-sm">{upload.error}</div>
                    </div>
                  </div>
                  <input
                    ref={(el) => { fileInputRefs.current[dt.type] = el; }}
                    type="file"
                    accept={dt.accept}
                    hidden
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleFileSelect(dt.type, f);
                    }}
                  />
                </div>
              ) : (
                <div
                  className={`dropzone ${upload ? 'active' : ''}`}
                  onClick={() => fileInputRefs.current[dt.type]?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => handleDrop(dt.type, e)}
                >
                  {upload ? (
                    <div>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2" style={{ margin: '0 auto 0.5rem' }}>
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <div className="body-md" style={{ fontWeight: 600 }}>{upload.file.name}</div>
                      <div className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
                        {(upload.file.size / 1024).toFixed(1)} KB — Ready to upload
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="dropzone-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                          <polyline points="17 8 12 3 7 8" />
                          <line x1="12" y1="3" x2="12" y2="15" />
                        </svg>
                      </div>
                      <div className="dropzone-title">Drop {dt.label} here</div>
                      <div className="dropzone-desc">or click to browse • PDF, JPG, PNG • Max 10 MB</div>
                    </div>
                  )}
                  <input
                    ref={(el) => { fileInputRefs.current[dt.type] = el; }}
                    type="file"
                    accept={dt.accept}
                    hidden
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleFileSelect(dt.type, f);
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex-between">
        <button className="btn btn-ghost" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {anyPending && (
            <button
              className="btn btn-secondary"
              onClick={uploadAll}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <div className="spinner spinner-sm" />
                  Uploading…
                </>
              ) : (
                'Upload All Documents'
              )}
            </button>
          )}
          {allUploaded && (
            <button
              className="btn btn-primary btn-lg"
              onClick={() => navigate(`/progress/${sessionId}`)}
            >
              Start Verification
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
