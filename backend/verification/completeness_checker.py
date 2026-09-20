"""Completeness checker — validates required field presence and OCR confidence.

Pure Python. No AWS dependencies.
"""
from backend.common.models import (
    ExtractedField, Finding, EvidenceItem, Severity, FindingStatus
)
from backend.common.crypto import generate_finding_id


def check_completeness(
    extracted_fields: list[ExtractedField],
    required_fields: list[dict],
    document_type: str,
    document_id: str
) -> list[Finding]:
    """Check all required fields from the document rule pack.

    - Field present with confidence >= 90 -> PASS
    - Field present with confidence 70-90 -> PASS with WARNING (CMP-02)
    - Field present with confidence < 70 -> REVIEW (CMP-03)
    - Field missing -> ORANGE finding (CMP-01)
    """
    findings: list[Finding] = []
    field_map = {f.fieldName: f for f in extracted_fields}

    for req in required_fields:
        field_name = req.get('fieldName', '')
        label = req.get('label', field_name)
        if not field_name:
            continue

        # Skip fields marked as doNotStore — these are deliberately not stored
        # (e.g., aadhaarNumber) per the security/privacy design
        if req.get('doNotStore', False):
            continue

        field = field_map.get(field_name)

        if not field or not field.rawValue.strip():
            # Missing required field
            findings.append(Finding(
                findingId=generate_finding_id('CMP'),
                ruleId='CMP-01',
                category='completeness',
                severity=Severity.WARNING,
                status=FindingStatus.ACTIVE,
                evidence=[EvidenceItem(
                    documentType=document_type,
                    documentId=document_id,
                    fieldName=field_name,
                    value='<missing>',
                    confidence=0.0
                )],
                affectedDocuments=[document_id],
                deterministicMessage=f"Required field '{label}' is missing from {document_type}.",
                deterministicMessageHi=f"आवश्यक फ़ील्ड '{label}' {document_type} में नहीं मिला।",
            ))
        elif field.confidence < 70:
            # Uncertain extraction
            findings.append(Finding(
                findingId=generate_finding_id('CMP'),
                ruleId='CMP-03',
                category='completeness',
                severity=Severity.REVIEW,
                status=FindingStatus.ACTIVE,
                evidence=[EvidenceItem(
                    documentType=document_type,
                    documentId=document_id,
                    fieldName=field_name,
                    value=field.rawValue[:64],
                    confidence=field.confidence
                )],
                affectedDocuments=[document_id],
                confidence=field.confidence,
                deterministicMessage=f"Field '{label}' could not be read clearly (confidence {field.confidence:.0f}%). Manual review needed.",
                deterministicMessageHi=f"फ़ील्ड '{label}' स्पष्ट रूप से नहीं पढ़ा जा सका (विश्वास {field.confidence:.0f}%)। मैनुअल समीक्षा आवश्यक।",
            ))
        elif field.confidence < 90:
            # Low quality warning
            findings.append(Finding(
                findingId=generate_finding_id('CMP'),
                ruleId='CMP-02',
                category='completeness',
                severity=Severity.INFO,
                status=FindingStatus.ACTIVE,
                evidence=[EvidenceItem(
                    documentType=document_type,
                    documentId=document_id,
                    fieldName=field_name,
                    value=field.rawValue[:64],
                    confidence=field.confidence
                )],
                affectedDocuments=[document_id],
                confidence=field.confidence,
                deterministicMessage=f"Field '{label}' quality is below optimal (confidence {field.confidence:.0f}%).",
                deterministicMessageHi=f"फ़ील्ड '{label}' की गुणवत्ता इष्टतम से कम है (विश्वास {field.confidence:.0f}%)।",
            ))

    return findings
