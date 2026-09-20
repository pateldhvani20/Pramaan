# DocVerify — System Architecture & Design Specification

> **Version**: 1.0.0 (Ruleset: `2026.09.1`)  
> **Target Region**: AWS `ap-south-1` (Mumbai)  
> **Event**: First Commit — Bharat Builds Tour (WeMakeDevs × AWS)

---

## 1. Product Summary

**DocVerify** is a deterministic document consistency and expiry verification pipeline designed for Indian student applications (scholarships, admissions, public schemes). DocVerify checks uploaded documents against one another and against policy-driven validity rules. It returns a deterministic readiness verdict with structured per-finding evidence, actionable resolution guidance (in English and Hindi), and immediately destroys raw document objects upon verification.

> *"DocVerify does not guess. A deterministic engine decides; the model only explains. And the document is gone before you finish reading the result."*

---

## 2. Architectural Diagram

```
                             [Client Application]
                                      │ TLS 1.3
                                      ▼
                        Amazon API Gateway (REST API)
                        - Throttling (20 rps / 40 burst)
                        - Request Validation & Body Caps
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
              Upload Controller λ            Verification API λ
                       │                             │
             Presigned POST (5 min,                  │
             ≤10 MB, Key-Prefix Locked,              │
             Type-Locked, SSE-KMS)                   │
                       ▼                             │
        ┌─────────────────────────────┐              │
        │   Amazon S3 (Private Raw)   │              │
        │   - Block Public Access     │              │
        │   - SSE-KMS (Customer Key)  │              │
        │   - TLS-Only Bucket Policy  │              │
        │   - Lifecycle: Expire 1 Day │              │
        │   - No Versioning           │              │
        └──────────────┬──────────────┘              │
                       │ S3 EventBridge Trigger      │
                       ▼                             │
        ┌──────────────────────────────────────┐     │
        │  AWS Step Functions (State Machine)  │     │
        │  ─────────────────────────────────── │     │
        │  1. IngestGate λ                     │     │
        │     - Magic bytes & MIME check       │     │
        │     - PDF unlock & page cap (≤50)    │     │
        │     - SHA-256 computation            │     │
        │  2. Extraction λ (Amazon Textract)   │     │
        │     - DetectDocumentText / Queries   │     │
        │     - Confidence mapping             │     │
        │  3. Classification λ                 │     │
        │     - Deterministic weighted signals │     │
        │  4. Completeness λ                   │     │
        │     - Mandatory fields & confidence  │     │
        │  5. VerificationEngine λ             │     │
        │     - Indic name matching (NM-01..06)│     │
        │     - DOB comparison (DOB-01..03)    │     │
        │     - Validity & Horizon (VAL-01..04)│     │
        │     - Confidence downgrade rule      │     │
        │     - Deterministic verdict stamping │     │
        │  6. Explanation λ (Amazon Bedrock)   │     │
        │     - Three-gate sanitization        │     │
        │     - Delimited prompt isolation     │     │
        │     - Strict schema validation       │     │
        │     - Deterministic fallback path    │     │
        │  7. Persist λ                        │────►│
        │     - Conditional write on timestamp │  Amazon DynamoDB
        │  8. Cleanup λ                        │  - Single Table: docverify-state
        │     - S3 DeleteObjects raw files     │  - SSE-KMS
        │  9. VerifyDeletion λ                 │  - Point-in-Time Recovery
        │     - HeadObject 404 verification    │  - TTL: 90 days
        └──────────────────────────────────────┘
```

---

## 3. Trust Boundaries & Security Controls

| # | Boundary | What Crosses It | Security Control |
|---|----------|-----------------|------------------|
| **1** | Client → AWS S3 | Raw user files | Presigned POST with content-length-range (1B to 10MB), content-type allowlist, key prefix constraint (`uploads/{sessionId}/`). No AWS credentials on client. |
| **2** | Storage → Ingestion Gate | Untrusted bytes | Magic bytes verification (`%PDF-`, `FF D8 FF`, `89 50 4E`), encryption check, parser verification, page limit cap ($\le 50$), SHA-256 hashing. |
| **3** | Extraction → AI Layer | Extracted text | **OWASP A03 / Prompt Injection Defense**: Raw OCR text is NEVER passed to Bedrock. Only structured findings with sanitized fields (control char stripping, allowlist regex, length cap at 128 chars) wrapped in `<finding>` delimiters. |
| **4** | Model → Verdict | AI output | **Strict architectural separation**: Bedrock output is schema-validated and populates `explanation` and `actionSteps` strings ONLY. Bedrock cannot alter `severity`, `ruleId`, or `readinessStatus`. On failure, falls back to deterministic text. |
| **5** | Processing → Persistence | State metadata | No raw document content, no unmasked Aadhaar numbers. Only hashes, structured findings, and metadata stored in DynamoDB under SSE-KMS. |
| **6** | Verification → Destruction | Raw S3 objects | Dual-layer deletion: Lambda issues S3 `DeleteObjects` followed by `HeadObject` 404 verification, backed by independent S3 1-day lifecycle expiration policy. |

---

## 4. Rule Pack Architecture

Rules are completely data-driven and versioned (`rulesetVersion: 2026.09.1`).

- **Profiles** (`rules/profiles/post-matric-scholarship.json`): Define required documents, review horizon days, and cross-document validation rules.
- **Documents** (`rules/documents/{aadhaar, marksheet, income_certificate, domicile}.json`): Define document signals, required fields, and validity rules.

Any change to a rule pack produces a new version, guaranteeing full auditability and reproducibility.
