<div align="center">

# 🏛️ प्रमाण (PRAMAAN)
### Intelligent Deterministic Document Verification & Readiness Platform

[![AWS](https://img.shields.io/badge/AWS-Serverless-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![React 19](https://img.shields.io/badge/React_19-TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Python 3.12](https://img.shields.io/badge/Python_3.12-Pydantic_v2-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Claude_3_Haiku-8C4FFF?style=for-the-badge&logo=anthropic&logoColor=white)](https://aws.amazon.com/bedrock/)
[![AWS CDK](https://img.shields.io/badge/AWS_CDK-v2.270.0-232F3E?style=for-the-badge&logo=awslambda&logoColor=white)](https://aws.amazon.com/cdk/)
[![OWASP Hardened](https://img.shields.io/badge/OWASP-Top_10_Hardened-00599C?style=for-the-badge&logo=owasp&logoColor=white)](https://owasp.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-45%2F45_Passing_(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

**A privacy-first, zero-retention pre-submission readiness gate for Indian student scholarships and public welfare schemes.**

Built for **First Commit — Bharat Builds Tour 2026** *(WeMakeDevs × AWS)*  
Deployed in Region: **`ap-south-1` (Asia Pacific - Mumbai)** 🇮🇳

---

### 🌐 Live Production Deployments

| Resource | Service | Live Endpoint |
|---|---|---|
| **Frontend Web App** | **AWS Amplify Hosting** | [**https://main.d2gfudksirk6lw.amplifyapp.com**](https://main.d2gfudksirk6lw.amplifyapp.com) 🔒 |
| **REST API Gateway** | **Amazon API Gateway** | `https://u99ao00u21.execute-api.ap-south-1.amazonaws.com/prod/` |
| **Full Hackathon Guide** | **Markdown Specification** | [`docs/PRAMAAN_COMPLETE_DOCUMENTATION.md`](docs/PRAMAAN_COMPLETE_DOCUMENTATION.md) |
| **3-Minute Video Script** | **Presentation Storyboard** | [`docs/demo_script.md`](docs/demo_script.md) |

---

</div>

## 📌 Table of Contents
1. [The Crisis: Why Pramaan?](#-the-crisis-why-pramaan)
2. [The Core Architectural Philosophy](#-the-core-architectural-philosophy)
3. [System Architecture & Cloud Topology](#-system-architecture--cloud-topology)
4. [End-to-End Dataflow & Pipeline Execution](#-end-to-end-dataflow--pipeline-execution)
5. [The Verification Engine Deep Dive](#-the-verification-engine-deep-dive)
6. [OWASP Top 10 & DPDP Act 2023 Security Hardening](#-owasp-top-10--dpdp-act-2023-security-hardening)
7. [AWS Cloud Services Utilized](#-aws-cloud-services-utilized)
8. [Tech Stack Matrix](#-tech-stack-matrix)
9. [Repository Directory Structure](#-repository-directory-structure)
10. [Local Development & Testing](#-local-development--testing)
11. [Meet the Team](#-meet-the-team)
12. [License & Acknowledgments](#-license--acknowledgments)

---

## 🚨 The Crisis: Why Pramaan?

In India, over **80 million students** apply annually for state and central government scholarship schemes (such as the National Scholarship Portal - NSP, Post-Matric Scholarships, and State Direct Benefit Transfer / DBT portals). 

Tragically, **18% to 25% of all applications are rejected or indefinitely stalled** due to trivial, avoidable clerical discrepancies:
* **Indic Transliteration Variants**: Differences between English records and regional language phonetic transliterations (e.g., *Laxmi* vs *Lakshmi*, *Ashish* vs *Aashish*, *Diksha* vs *Deeksha*).
* **Token Order Inversion**: Surnames listed first on Class X marksheets but last on Aadhaar cards (e.g., *Patel Saswat* vs *Saswat Patel*).
* **Dropped Initials / Middle Names**: Middle names omitted or abbreviated across records (e.g., *Kunal B. Borse* vs *Kunal Borse*).
* **Date of Birth Formatting Ambiguities**: Conflicting interpretations of ambiguous numeric dates (`05/06/2004`).
* **Lapsing & Expired Documents**: State income and domicile certificates expiring mid-evaluation cycle.
* **The Bureaucratic Black Hole**: Students discover rejections 3 to 6 months after submission—long after academic deadlines have passed, forfeiting crucial financial aid.

### 💡 The Solution
**Pramaan (प्रमाण)** acts as an intelligent, pre-submission readiness checkpoint. Applicants upload their four core documents (Aadhaar, Marksheet, Income Certificate, and Domicile Certificate). Within seconds, Pramaan verifies cross-document consistency, evaluates validity horizons, and produces an unambiguous **Readiness Verdict** (`GREEN`, `AMBER`, `ORANGE`, `RED`). 

Using **Amazon Bedrock (Claude 3 Haiku)**, it translates findings into empathetic, bilingual (Hindi & English) resolution steps, empowering students to fix errors *before* submitting. Under India's **DPDP Act 2023**, all uploaded document files are permanently destroyed post-verification.

---

## ⚖️ The Core Architectural Philosophy

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│   "The Deterministic Verification Engine decides status and severity. │
│    Generative AI only explains structured findings and suggests        │
│    actionable remediation. AI is NEVER permitted to decide whether     │
│    a citizen's legal document passes or fails."                       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

By strictly isolating Generative AI to the explanation layer, Pramaan prevents:
1. **LLM Hallucinations** from falsely validating forged or invalid documents.
2. **Non-deterministic drift** across identical document scans.
3. **Adversarial prompt injection attacks** embedded inside fraudulent document scans.

---

## 🏛️ System Architecture & Cloud Topology

Pramaan is architected as an event-driven, 100% serverless multi-tier infrastructure deployed in **AWS `ap-south-1` (Mumbai)**.

```
+──────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                           PRESENTATION TIER                                          |
|     React 19 + TypeScript + Vite SPA  ──►  Hosted on AWS Amplify Edge CDN (HTTPS / SSL Enforced)     |
|     https://main.d2gfudksirk6lw.amplifyapp.com                                                       |
+───────────────────────────────────────────────────┬──────────────────────────────────────────────────+
                                                    │ TLS 1.3
                                                    ▼
+──────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                            API ROUTING TIER                                          |
|     Amazon API Gateway (REST API, Stage: prod, Throttling: 20 rps / 40 burst, Full CORS)            |
|     ├── GET  /profiles                    ──► Profiles Lambda (Bundled Rule Profiles)                 |
|     ├── POST /verifications               ──► Session Creator Lambda (128-bit Capability Tokens)     |
|     ├── GET  /verifications/{id}          ──► Status & Findings Lambda (DynamoDB Read)               |
|     ├── POST /verifications/{id}/uploads  ──► Presigned POST Controller Lambda (S3 Scoped Policy)    |
|     └── POST /verifications/{id}/run      ──► Workflow Trigger Lambda (Executes Step Functions)      |
+───────────────────────────┬──────────────────────────────────────────────────────────────────────────+
                            │
              ┌─────────────┴────────────────────────────────────────────────────┐
              │ Presigned POST (1B-10MB Cap, 5 min TTL, Key Locked, KMS Encrypted)│
              ▼                                                                  ▼
+─────────────────────────────────────────+          +─────────────────────────────────────────────────+
|         EPHEMERAL RAW STORAGE           |          |            PERSISTENCE & STATE                  |
|   Amazon S3 (Private Raw Bucket)        |          |   Amazon DynamoDB (Single-Table Design)         |
|   - KMS Customer Managed Key (CMK)      |          |   - StateTable (PK: SESSION#{id}, SK: META)     |
|   - Block Public Access (All 4 ON)      |          |   - SSE-KMS Encrypted at Rest                   |
|   - TLS-Only Enforcement Policy         |          |   - Point-in-Time Recovery (PITR) Enabled       |
|   - 1-Day Automated Lifecycle Expiry    |          |   - 90-Day Auto-TTL Expiration                  |
+────────────────────┬────────────────────+          +────────────────────────▲────────────────────────+
                     │ S3 ObjectCreated Notification                          │
                     ▼                                                        │
+─────────────────────────────────────────────────────────────────────────────┴────────────────────────+
|                                         SERVERLESS PIPELINE                                          |
|      AWS Step Functions State Machine: DocVerifyStateMachine (Standard Sequential Workflow)          |
|                                                                                                      |
|   1. IngestGate Lambda       ──► Magic byte verification, MIME validation, SHA-256 digest, page cap  |
|   2. Extraction Lambda       ──► Amazon Textract OCR / Key-Value Pair extraction & confidence scores |
|   3. Classification Lambda   ──► Dynamic weighted keyword & layout signal scoring                    |
|   4. Completeness Lambda     ──► Required field checklist validation & Aadhaar doNotStore masking    |
|   5. Verification Lambda     ──► PURE PYTHON ENGINE (Indic Name Matching, DOB Cross-Check, Horizon)  |
|   6. Explanation Lambda      ──► Amazon Bedrock (Claude 3 Haiku) with Three-Gate Sanitization        |
|   7. Persist Lambda          ──► Conditional atomic update to Amazon DynamoDB                        |
|   8. Cleanup Lambda          ──► S3 DeleteObject raw file destruction & HeadObject 404 verification  |
+──────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 🔄 End-to-End Dataflow & Pipeline Execution

```mermaid
sequenceDiagram
    autonumber
    actor Applicant as Student / Applicant
    participant UI as React 19 Frontend (Amplify)
    participant APIGW as Amazon API Gateway
    participant S3 as Amazon S3 (KMS Encrypted)
    participant SFN as AWS Step Functions
    participant Engine as Deterministic Engine Lambda
    participant Bedrock as Amazon Bedrock (Haiku)
    participant DDB as Amazon DynamoDB

    Applicant->>UI: Selects Profile (Post-Matric Scholarship)
    UI->>APIGW: POST /verifications
    APIGW-->>UI: 201 Created (sessionId: unguessable 128-bit token)
    
    rect rgb(240, 245, 255)
    Note over UI,S3: Direct-to-S3 Presigned Upload (Zero Binary Routing via API)
    UI->>APIGW: POST /verifications/{id}/uploads (filename, type)
    APIGW-->>UI: 200 OK (Presigned POST URL, 5 min TTL, 10MB limit)
    UI->>S3: POST document binary directly to S3
    end

    Applicant->>UI: Clicks "Run Verification"
    UI->>APIGW: POST /verifications/{id}/run
    APIGW->>SFN: start_execution(sessionId)
    
    rect rgb(255, 248, 240)
    Note over SFN,Engine: Serverless Processing & Verification
    SFN->>SFN: 1. IngestGate (Magic bytes, SHA-256, page limit)
    SFN->>SFN: 2. Textract (Key-Value extraction & OCR confidence)
    SFN->>SFN: 3. Classifier (Weighted signal scoring)
    SFN->>SFN: 4. Completeness (Check required fields; mask Aadhaar)
    SFN->>Engine: 5. Execute Pure Python Verification Engine
    Engine-->>SFN: Computed Findings & Final ReadinessStatus (GREEN/AMBER/ORANGE/RED)
    end

    rect rgb(245, 255, 245)
    Note over SFN,Bedrock: Generative AI Explanation (Strict Three-Gate Sandbox)
    SFN->>Bedrock: 6. Pass Sanitized Finding Structs (<<<delimiters>>>)
    Bedrock-->>SFN: Plain-Language Hindi/English Guidance & Action Steps
    end

    rect rgb(255, 240, 240)
    Note over SFN,S3: Atomic State Persistence & Immediate Data Destruction
    SFN->>DDB: 7. Atomic Write: Save metadata, findings & status
    SFN->>S3: 8. DeleteObject (Destroy raw uploads)
    SFN->>S3: 9. HeadObject (Confirm 404 Not Found)
    end

    UI->>APIGW: GET /verifications/{id} (Polling)
    APIGW->>DDB: GetItem(SESSION#{id})
    APIGW-->>UI: 200 OK (Status, Findings, Action Steps, Bilingual Explanations)
    UI-->>Applicant: Renders Color-Coded Findings & Actionable Guidance
```

---

## 🧠 The Verification Engine Deep Dive

Located in `backend/verification/engine.py`, the core engine is **100% pure Python 3.12** using Pydantic V2 models with **zero external cloud or network dependencies**. It runs in milliseconds and is fully testable offline.

### 1. Indic Name Matcher (`NM-01` to `NM-06`)
Indian names present distinct phonological and structural variations that break generic string matching. Our matcher applies a 6-tier hierarchical alignment:

| Rule Code | Match Type | Scenario Example | Confidence | Outcome |
|:---:|---|---|:---:|:---:|
| **`NM-01`** | **EXACT** | Case-folded, whitespace-stripped identical match (`Saswat Kumar` vs `saswat kumar`). | `1.00` | 🟢 Pass |
| **`NM-02`** | **SUBSET_ORDERED** | Dropped middle initials / middle names in exact forward sequence (`Saswat Kumar Patel` vs `Saswat Patel`). | `0.95` | 🟢 Pass |
| **`NM-03`** | **ORDER_SWAP** | Surname inverted to given name position (`Patel Saswat` vs `Saswat Patel`). Common in Western & Southern India. | `0.92` | 🟢 Pass |
| **`NM-04`** | **TRANSLITERATION** | Standard phonetic Indic phoneme substitutions (`Laxmi` vs `Lakshmi`, `Vikas` vs `Bikas`, `Diksha` vs `Deeksha`). | `0.90` | 🟢 Pass |
| **`NM-05`** | **TYPO_TOLERANT** | Clerical typographic slips evaluated via sorted-token Jaro-Winkler distance ($JW \ge 0.88$). | `0.85` | 🟢 Pass |
| **`NM-06`** | **BLOCKING_MISMATCH**| Incompatible tokens exceeding phonetic/edit limits (`Rahul Borse` vs `Kunal Borse`). | `0.00` | 🔴 **BLOCKING** |

### 2. Date of Birth Consistency Checker (`DOB-01` to `DOB-03`)
* **`DOB-01` (MATCH)**: Identical birth dates across Aadhaar, Class X marksheet, and domicile records.
* **`DOB-02` (AMBIGUOUS_FORMAT)**: Catches ambiguous date notation (e.g., `04/05/2004` could be April 5th or May 4th) and alerts the applicant to confirm scan quality.
* **`DOB-03` (MISMATCH)**: Irreconcilable differences in year, month, or day. Rated as `BLOCKING`.

### 3. Validity Horizon Checker (`VAL-01` to `VAL-03`)
* **Permanent Records**: Class X marksheets and Aadhaar cards are recognized as permanently valid.
* **Dynamic Horizon Analysis**: Uses `dateutil.relativedelta` against policy review windows (e.g., 180 days for Post-Matric schemes):
  - **VALID**: Document expiration date safely exceeds the processing window.
  - **LAPSING**: Document expires within **30 days** (triggers an `ORANGE` actionable warning).
  - **EXPIRED**: Expiration date is in the past (triggers a `RED` blocking failure).

### 4. Completeness Checker (`CMP-01`)
* Compares extracted attributes against mandatory schema packs (`rules/documents/*.json`).
* Honors **`doNotStore: true`** directives: raw 12-digit Aadhaar numbers are verified for checksum format in-memory but are stripped from persistence.

### 5. The Readiness Status Matrix
```
   ┌────────────────────────────────────────────────────────────────────────┐
   │                       READINESS STATUS MODEL                           │
   ├──────────────┬──────────────────┬──────────────────────────────────────┤
   │  🟢 GREEN    │ Ready            │ Clean pass; submit immediately.      │
   │  🟡 AMBER    │ Review Required  │ Low OCR confidence / ambiguous date. │
   │  🟠 ORANGE   │ Action Required  │ Fixable non-blocking issue (lapsing).│
   │  🔴 RED      │ Not Ready        │ Hard blocking contradiction.         │
   └──────────────┴──────────────────┴──────────────────────────────────────┘
```

### 6. The Confidence Downgrade Safety Rule
> **Safety Rule**: If Amazon Textract extraction confidence on any critical field falls below **85%**, the engine is architecturally barred from rendering a `GREEN` verdict. It automatically downgrades the status to `AMBER (Review Required)`, ensuring no citizen is misled by a noisy scan.

---

## 🛡️ OWASP Top 10 & DPDP Act 2023 Security Hardening

Pramaan incorporates defense-in-depth measures mapped directly to the **OWASP Top 10 (2021)** and **OWASP Top 10 for Large Language Models**:

```
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| OWASP Vulnerability      | Pramaan Engineering Control                                                        |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A01: Broken Access       | Unguessable 128-bit cryptographic capability tokens (secrets.token_urlsafe(16)).   |
|     Control              | S3 Presigned POST scoped to exact key prefix (uploads/{sessionId}/).               |
|                          | Non-matching session lookups return 404 Not Found to prevent enumeration.          |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A02: Cryptographic       | AWS KMS Customer Managed Key (CMK, alias/docverify) with annual auto-rotation.     |
|     Failures             | Strict S3 bucket policies enforcing TLS 1.2+ (aws:SecureTransport: false denied).  |
|                          | DynamoDB encrypted at rest with CMK; raw PII never stored in plain text.           |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A03: Injection           | THREE-GATE BEDROCK PROMPT INJECTION DEFENSE:                                       |
|     (LLM Defense)        | 1. Raw OCR text NEVER touches Bedrock. Only deterministic findings pass through.  |
|                          | 2. Three-Gate Value Sanitization: Control chars stripped, strict regex allowlist,  |
|                          |    128-character hard cap per field value.                                         |
|                          | 3. System prompt encapsulation with <<<data>>> tags & strict Pydantic JSON schema. |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A04: Insecure Design     | Deterministic Verdict Engine: Bedrock has zero authority over pass/fail or status. |
|                          | Complete failure of Bedrock degrades gracefully to deterministic rule templates.   |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A05: Security            | S3 Block Public Access enabled across all buckets. S3 versioning disabled on raw   |
|     Misconfiguration     | buckets to ensure deletions cannot be recovered via version markers.               |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A07: Identification      | No traditional password/email database stored (minimizing credential leaks).       |
|     Failures             | Ephemeral capability tokens provide zero-friction, secure access without tracking. |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A08: Software & Data     | SHA-256 integrity digest computed at IngestGate prior to processing.               |
|     Integrity Failures   | Rule packs version-stamped (rulesetVersion: 2026.09.1) for forensic auditability.  |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
| A09: Logging &           | Structured JSON logging in CloudWatch with automated PII masking of names,         |
|     Monitoring           | birthdates, and 12-digit numeric sequences. Cleanup failures trigger CW alarms.   |
+──────────────────────────+────────────────────────────────────────────────────────────────────────────────────+
```

### 🇮🇳 India DPDP Act 2023: Zero-Retention Architecture
Under the Digital Personal Data Protection Act, storing citizens' identity records without purpose limitation creates severe compliance and liability exposure. Pramaan enforces **Guaranteed Ephemerality**:
1. Documents uploaded to S3 exist solely for the duration of the Step Functions execution pipeline (< 15 seconds).
2. The **Cleanup Lambda** invokes `s3:DeleteObject` on all raw files.
3. A mandatory `HeadObject` check verifies that S3 returns `404 Not Found`.
4. As an automated secondary fail-safe, an S3 Lifecycle Rule purges any orphan file older than 24 hours.

---

## ☁️ AWS Cloud Services Utilized

| AWS Service | Architecture Role | Production Configuration & Specs |
|---|---|---|
| **AWS Amplify** | Frontend Hosting | Global edge distribution with Amazon SSL/TLS certificate & SPA client-side rewrite rules. |
| **Amazon API Gateway** | API Management | REST API stage `prod`, throttled at 20 rps / 40 burst, CORS enabled for all origins. |
| **AWS Step Functions** | Workflow Orchestrator | Standard State Machine orchestrating 8 sequential microservice steps with native retry logic. |
| **AWS Lambda** | Serverless Compute | 8 microservices running on Python 3.12 with dedicated least-privilege IAM execution roles. |
| **Amazon Bedrock** | Generative AI | Foundation Model API invoking **Anthropic Claude 3 Haiku** for bilingual remediation advice. |
| **Amazon Textract** | Document Intelligence | Machine learning OCR extracting form key-value pairs, tables, and block confidence scores. |
| **Amazon DynamoDB** | State & Findings Store | Single-table `StateTable` with `PAY_PER_REQUEST` billing, KMS CMK encryption & Point-in-Time Recovery. |
| **Amazon S3** | Ephemeral File Vault | KMS-encrypted raw bucket with Block Public Access, TLS-only bucket policy & 1-day lifecycle expiry. |
| **AWS KMS** | Cryptographic Security | Customer Managed Key (`alias/docverify`) with automatic annual key rotation. |
| **Amazon EventBridge** | Event Bus | Asynchronous S3 `ObjectCreated` event filtering and pipeline invocation. |
| **Amazon CloudWatch** | Monitoring & Auditing | PII-redacted structured JSON execution logs, custom metrics, and cleanup failure alerting. |

---

## 💻 Tech Stack Matrix

```
┌─────────────────┬────────────────────────────────────────────────────────┐
│ Layer           │ Technologies & Tools                                   │
├─────────────────┼────────────────────────────────────────────────────────┤
│ Frontend        │ React 19, TypeScript, Vite, React Router v7, Axios     │
│ UI Design       │ Stitch Design System (Glassmorphism, CSS Custom Props) │
│ Backend Core    │ Python 3.12, Pydantic V2, dateutil, ReportLab, pytest  │
│ Cloud & IaC     │ AWS CDK v2 (Python), Boto3, CloudFormation             │
│ AI / ML         │ Amazon Bedrock (Claude 3 Haiku), Amazon Textract       │
│ Database        │ Amazon DynamoDB (Single-Table Design, NoSQL)           │
│ Storage & KMS   │ Amazon S3, AWS Key Management Service (KMS CMK)        │
│ Orchestration   │ AWS Step Functions, Amazon EventBridge                 │
│ Security        │ OWASP Top 10 (2021), OWASP LLM Top 10, DPDP Act 2023   │
└─────────────────┴────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Directory Structure

```text
Pramaan/
├── README.md                            # You are here! Master project documentation
├── backend/                             # Pure Python Serverless Backend
│   ├── common/                          # Shared utilities & data models
│   │   ├── crypto.py                    # SHA-256 hashing & token generators
│   │   ├── logging.py                   # PII-redacted structured JSON logger
│   │   ├── models.py                    # Pydantic V2 data contracts (ReadinessStatus, Findings)
│   │   ├── rule_loader.py               # Dynamic JSON rule pack loader
│   │   └── sanitizer.py                 # Three-Gate OWASP prompt injection sanitizer
│   ├── extraction/                      # OCR & Textract integration adapters
│   │   └── textract_adapter.py          # Amazon Textract client with mock support
│   ├── classification/                  # Document classifier microservice
│   │   └── classifier.py                # Weighted signal & keyword classification
│   ├── verification/                    # Deterministic Verification Engine (Zero AWS deps)
│   │   ├── engine.py                    # Master cross-document orchestrator
│   │   ├── name_matcher.py              # Indic Name Matcher (NM-01 to NM-06)
│   │   ├── dob_checker.py               # Date of Birth Checker (DOB-01 to DOB-03)
│   │   ├── validity_checker.py          # Dynamic Expiry Horizon Checker (VAL-01 to VAL-03)
│   │   └── completeness_checker.py      # Mandatory field audit & doNotStore masking
│   ├── explanation/                     # Generative AI Explanation Layer
│   │   ├── bedrock_adapter.py           # Amazon Bedrock Claude 3 Haiku integration
│   │   └── prompt_builder.py            # Three-Gate delimited prompt constructor
│   ├── ingestion/                       # Ingestion gate & upload controller
│   │   ├── ingest_gate.py               # Magic bytes & MIME validation
│   │   └── upload_controller.py         # S3 Presigned POST generator
│   ├── persistence/                     # DynamoDB persistence adapter
│   │   └── dynamodb_adapter.py          # Single-table KMS-encrypted storage client
│   └── workflow/                        # Lambda microservice handler entrypoints
│       └── handlers.py                  # Handlers for Ingest, Extraction, Engine, API, Cleanup
├── frontend/                            # React 19 + TypeScript + Vite SPA
│   ├── src/
│   │   ├── api/                         # Axios client & typed API SDK
│   │   ├── components/                  # Reusable UI components (Sidebar, Badges)
│   │   ├── context/                     # Global session & profile state context
│   │   ├── pages/                       # LandingPage, Dashboard, Upload, Progress, Results
│   │   └── styles/                      # Stitch design system tokens & glassmorphic CSS
│   ├── package.json                     # Node dependencies (React 19, Vite, Axios)
│   └── vite.config.ts                   # Vite configuration with dev proxy
├── infra/                               # Infrastructure as Code (AWS CDK v2 in Python)
│   ├── app.py                           # CDK application entrypoint
│   ├── cdk.json                         # CDK execution & context configuration
│   ├── deploy_frontend_amplify.py       # Automated AWS Amplify HTTPS deployment script
│   └── stacks/
│       ├── core_stack.py                # S3 raw/results buckets, KMS CMK, DynamoDB table
│       ├── pipeline_stack.py            # 8 Lambdas, Step Functions State Machine, EventBridge
│       └── api_stack.py                 # API Gateway REST API with CORS & throttling
├── rules/                               # Versioned Verification Rule Packs (JSON)
│   ├── profiles/                        # Cross-document profiles (e.g. post-matric-scholarship)
│   └── documents/                       # Per-document definitions (aadhaar, marksheet, income)
├── tests/                               # Comprehensive Automated Test Suite
│   ├── fixtures/                        # ReportLab synthetic PDF generator (f01 to f14)
│   ├── test_name_matching.py            # 10 unit tests for Indic name matching logic
│   ├── test_validity.py                 # 5 tests for validity horizons & expiry dates
│   ├── test_classifier.py               # 6 tests for document classification
│   ├── test_sanitization.py             # 9 tests for Three-Gate prompt injection defense
│   ├── test_ingest_gate.py              # 7 tests for magic bytes and page limits
│   └── test_engine_e2e.py               # 5 end-to-end integration tests (clean pass & rejections)
└── docs/                                # Technical Specifications & Hackathon Documentation
    ├── PRAMAAN_COMPLETE_DOCUMENTATION.md# Master documentation & official form answers
    ├── architecture.md                  # System architecture & trust boundary specification
    ├── api_contract.md                  # REST API schema contract specification
    ├── security.md                      # OWASP Top 10 threat model & mitigations
    └── demo_script.md                   # 3-Minute presentation storyboard & script
```

---

## 🧪 Local Development & Testing

### 1. Run Automated Test Suite
The verification engine is unit-testable locally with zero AWS credentials required:
```powershell
# Navigate to repository root
cd Pramaan

# Install backend dependencies
pip install -r backend/requirements.txt pytest

# Execute all 45 automated tests
pytest -v
```
**Output**:
```text
============================== 45 passed in 0.84s ==============================
```

### 2. Run Frontend Locally
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser. The Vite dev server proxies requests to your production AWS API Gateway!

### 3. Deploy Cloud Infrastructure with AWS CDK
```powershell
cd infra
pip install -r requirements.txt

# Synthesize CloudFormation templates
cdk synth

# Deploy all stacks to AWS ap-south-1
cdk deploy --all --require-approval never
```

### 4. Deploy Frontend to AWS Amplify (1-Click HTTPS)
```powershell
# Build production React bundle
cd frontend
npm run build

# Deploy directly to AWS Amplify Edge CDN
cd ../infra
python deploy_frontend_amplify.py
```

---

## 👥 Meet the Team

| Team Member | Role | Core Deliverables |
|---|---|---|
| **Kunal Borse** | **Team Leader** & Cloud / DevOps Engineer | Multi-stack AWS CDK v2 architecture, IAM zero-trust execution roles, KMS CMK encryption, Step Functions state machine orchestration, S3 lifecycle zero-retention policies. |
| **Saswat Kumar** (`Swaggyop`) | **Backend Architect** & Verification Engine Engineer | Core deterministic verification engine in pure Python, Indic Name Matching algorithm (NM-01 to NM-06), DOB consistency checker, dynamic validity horizon checker, 45 automated pytest cases, API Gateway Lambda handlers. |
| **Dhvani Patel** | **AI/ML & Document Intelligence** Engineer | Amazon Textract integration adapter with confidence mapping, Three-Gate OWASP prompt injection defense, Amazon Bedrock Claude 3 Haiku bilingual explanation integration, ReportLab synthetic PDF generator (f01–f14). |
| **Nitya Gohil** | **Frontend & UI/UX** Engineer | Responsive React 19 SPA with Stitch glassmorphic design token system, presigned direct S3 uploads, real-time Step Functions pipeline visualization, bilingual findings dashboard, AWS Amplify HTTPS deployment. |

---

## 📄 License & Acknowledgments

* **License**: Released under the [MIT License](LICENSE).
* **Organizers**: Built with pride for **First Commit — Bharat Builds Tour 2026**, organized by **WeMakeDevs** in partnership with **Amazon Web Services (AWS)**.
* **National Vision**: Designed to empower India's youth by ensuring that clerical errors never stand between a deserving student and their education.

<div align="center">
<b>🇮🇳 Made with passion for Bharat's Students 🇮🇳</b>
</div>
