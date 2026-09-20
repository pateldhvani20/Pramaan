"""
Pydantic V2 data contracts for DocVerify.
Contains all frozen data models used across the system.
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime

class ReadinessStatus(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    ORANGE = "ORANGE"
    RED = "RED"

class Severity(str, Enum):
    BLOCKING = "BLOCKING"
    WARNING = "WARNING"
    REVIEW = "REVIEW"
    INFO = "INFO"

class FindingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"

class NameMatchResult(str, Enum):
    MATCH = "MATCH"
    MINOR_VARIATION = "MINOR_VARIATION"
    MISMATCH = "MISMATCH"
    UNCERTAIN = "UNCERTAIN"

class DocumentLifecycle(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    EXTRACTED = "EXTRACTED"
    CLASSIFIED = "CLASSIFIED"
    VERIFIED = "VERIFIED"
    PERSISTED = "PERSISTED"
    DELETED = "DELETED"
    REJECTED = "REJECTED"

class IngestResult(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_INVALID = "REJECTED_INVALID"
    REJECTED_TOO_LARGE = "REJECTED_TOO_LARGE"
    REJECTED_LOCKED = "REJECTED_LOCKED"
    REJECTED_UNSUPPORTED = "REJECTED_UNSUPPORTED"

class EvidenceItem(BaseModel):
    documentType: str
    documentId: str
    fieldName: str
    value: str
    confidence: float = 0.0

class Finding(BaseModel):
    findingId: str
    ruleId: str
    category: str  # identity, dob, validity, completeness, classification, integrity
    severity: Severity
    status: FindingStatus = FindingStatus.ACTIVE
    evidence: list[EvidenceItem] = Field(default_factory=list)
    affectedDocuments: list[str] = Field(default_factory=list)
    confidence: float | None = None
    deterministicMessage: str
    deterministicMessageHi: str = ""
    explanation: str | None = None
    actionSteps: list[str] = Field(default_factory=list)
    language: str = "en"

class ExtractedField(BaseModel):
    fieldId: str
    fieldName: str
    rawValue: str = ""
    normalizedValue: str = ""
    confidence: float = 0.0
    sourceDocumentId: str = ""

class DocumentRecord(BaseModel):
    documentId: str
    sessionId: str
    expectedType: str
    detectedType: str | None = None
    sha256: str = ""
    size: int = 0
    pageCount: int = 0
    extractionStatus: str = "PENDING"
    lifecycle: DocumentLifecycle = DocumentLifecycle.UPLOADED
    extractedFields: list[ExtractedField] = Field(default_factory=list)
    uploadedAt: str = ""
    ingestResult: IngestResult | None = None

class VerificationSession(BaseModel):
    sessionId: str
    profileId: str
    verificationVersion: int = 1
    createdAt: str = ""
    status: ReadinessStatus = ReadinessStatus.AMBER
    rulesetVersion: str = "2026.09.1"
    language: str = "en"

class VerificationResult(BaseModel):
    sessionId: str
    verificationVersion: int = 1
    readinessStatus: ReadinessStatus = ReadinessStatus.AMBER
    blockingCount: int = 0
    warningCount: int = 0
    reviewCount: int = 0
    findings: list[Finding] = Field(default_factory=list)
    rulesetVersion: str = "2026.09.1"
    processedAt: str = ""
    documents: list[DocumentRecord] = Field(default_factory=list)
