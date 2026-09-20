import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      {/* ---- Navbar ---- */}
      <nav className="landing-nav">
        <div className="landing-nav-inner">
          <div className="landing-brand">
            <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="#8a307f" />
              <path d="M14 24l6 6 14-14" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className="landing-brand-text">Pramaan</span>
          </div>
          <div className="landing-nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#security">Security</a>
            <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* ---- Hero ---- */}
      <section className="landing-hero">
        <div className="landing-hero-inner">
          <div className="landing-hero-badge">
            <span className="badge badge-green">
              <span className="badge-dot" />
              Deterministic Verification Engine
            </span>
          </div>
          <h1 className="display-lg landing-hero-title">
            Intelligent Document<br />
            <span className="landing-gradient-text">Verification</span> Platform
          </h1>
          <p className="body-lg landing-hero-desc">
            Pramaan verifies Indian student documents with deterministic rules, 
            AI-powered explanations, and zero-retention security. Upload your Aadhaar, 
            marksheet, income certificate, and domicile — get instant readiness verification.
          </p>
          <div className="landing-hero-actions">
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/new')}>
              Start Verification
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => navigate('/dashboard')}>
              View Dashboard
            </button>
          </div>
        </div>
      </section>

      {/* ---- Features ---- */}
      <section id="features" className="landing-section">
        <div className="landing-section-inner">
          <h2 className="headline-xl landing-section-title">Why Pramaan?</h2>
          <p className="body-lg landing-section-desc">
            Built for the Bharat Builds Tour — a deterministic verification engine that never guesses.
          </p>
          <div className="grid-3 landing-features">
            {[
              {
                icon: '🔒',
                title: 'Zero-Retention Security',
                desc: 'Documents are verified, then destroyed. SHA-256 hashes and metadata only — raw files never persist.',
              },
              {
                icon: '⚡',
                title: 'Deterministic Verification',
                desc: 'Rule-based engine with Indic name matching, DOB cross-checks, validity horizon, and confidence thresholds.',
              },
              {
                icon: '🤖',
                title: 'AI-Powered Explanations',
                desc: 'Amazon Bedrock generates plain-language explanations with three-gate sanitization. AI explains, but never decides.',
              },
              {
                icon: '🇮🇳',
                title: 'Built for India',
                desc: 'Supports Aadhaar, marksheets, income certificates, domicile — with Hindi & English bilingual findings.',
              },
              {
                icon: '📋',
                title: 'Actionable Findings',
                desc: 'Each finding includes structured evidence, resolution steps, and clear severity classification.',
              },
              {
                icon: '☁️',
                title: 'Serverless AWS Architecture',
                desc: 'API Gateway, Lambda, Step Functions, Textract, Bedrock, DynamoDB, S3 with KMS encryption.',
              },
            ].map((f, i) => (
              <div className="card animate-in" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="landing-feature-icon">{f.icon}</div>
                <h3 className="title-lg">{f.title}</h3>
                <p className="body-md" style={{ color: 'var(--on-surface-variant)', marginTop: '0.5rem' }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- How It Works ---- */}
      <section id="how-it-works" className="landing-section landing-section-alt">
        <div className="landing-section-inner">
          <h2 className="headline-xl landing-section-title">How It Works</h2>
          <div className="landing-steps">
            {[
              { step: '1', title: 'Create Application', desc: 'Select a verification profile (e.g., Post-Matric Scholarship).' },
              { step: '2', title: 'Upload Documents', desc: 'Upload Aadhaar, Marksheet, Income Certificate, and Domicile.' },
              { step: '3', title: 'Automatic Verification', desc: 'Step Functions pipeline: ingest → extract → classify → verify → explain.' },
              { step: '4', title: 'View Results', desc: 'Readiness verdict with per-finding evidence, severity, and resolution steps.' },
            ].map((s, i) => (
              <div className="landing-step animate-in" key={i} style={{ animationDelay: `${i * 0.15}s` }}>
                <div className="landing-step-number">{s.step}</div>
                <div>
                  <h3 className="title-lg">{s.title}</h3>
                  <p className="body-md" style={{ color: 'var(--on-surface-variant)', marginTop: '0.25rem' }}>{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---- Security ---- */}
      <section id="security" className="landing-section">
        <div className="landing-section-inner">
          <h2 className="headline-xl landing-section-title">Security First</h2>
          <div className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
            <div className="stack gap-md">
              <div className="flex-between">
                <span className="label-lg">Encryption</span>
                <span className="badge badge-green"><span className="badge-dot" />SSE-KMS</span>
              </div>
              <div className="flex-between">
                <span className="label-lg">Document Retention</span>
                <span className="badge badge-green"><span className="badge-dot" />Zero (Verified Deletion)</span>
              </div>
              <div className="flex-between">
                <span className="label-lg">Transport</span>
                <span className="badge badge-green"><span className="badge-dot" />TLS 1.3</span>
              </div>
              <div className="flex-between">
                <span className="label-lg">Prompt Injection Defense</span>
                <span className="badge badge-green"><span className="badge-dot" />3-Gate Sanitization</span>
              </div>
              <div className="flex-between">
                <span className="label-lg">Data at Rest</span>
                <span className="badge badge-green"><span className="badge-dot" />KMS + Point-in-Time Recovery</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---- Footer ---- */}
      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <p className="body-sm" style={{ color: 'var(--on-surface-variant)' }}>
            Pramaan — First Commit, Bharat Builds Tour (WeMakeDevs × AWS). Ruleset v2026.09.1
          </p>
        </div>
      </footer>
    </div>
  );
}
