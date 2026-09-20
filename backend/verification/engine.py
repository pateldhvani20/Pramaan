"""DocVerify Verification Engine — the core IP.

Pure Python. ZERO boto3 imports. ZERO AWS dependencies.
Takes structured documents + profile + rules in, returns deterministic verdict out.
Every finding carries the ruleId that produced it.
"""
from datetime import date
from typing import Optional

from backend.common.models import (
    DocumentRecord, ExtractedField, Finding, EvidenceItem,
    VerificationResult, ReadinessStatus, Severity, FindingStatus
)
from backend.common.crypto import generate_finding_id
from .name_matcher import match_names, NameMatchResult as NMResult
from .dob_checker import compare_dob
from .validity_checker import check_validity
from .completeness_checker import check_completeness


def _get_field_value(doc: DocumentRecord, field_name: str) -> tuple[Optional[str], float]:
    """Get extracted field value and confidence from a document."""
    for f in doc.extractedFields:
        if f.fieldName == field_name:
            return f.normalizedValue or f.rawValue, f.confidence
    return None, 0.0


def _run_cross_document_name_checks(
    documents: list[DocumentRecord],
    check: dict
) -> list[Finding]:
    """Run cross-document name matching for a specific check definition."""
    findings: list[Finding] = []
    field_name = check.get('field', 'applicantName')
    check_docs = check.get('documents', [])
    on_mismatch = check.get('onMismatch', 'BLOCKING')

    # Gather all documents that match the check's document types
    relevant_docs = [d for d in documents if d.expectedType in check_docs or d.detectedType in check_docs]

    # Compare all pairs
    compared = set()
    for i, doc_a in enumerate(relevant_docs):
        for j, doc_b in enumerate(relevant_docs):
            if i >= j:
                continue
            pair_key = tuple(sorted([doc_a.documentId, doc_b.documentId]))
            if pair_key in compared:
                continue
            compared.add(pair_key)

            val_a, conf_a = _get_field_value(doc_a, field_name)
            val_b, conf_b = _get_field_value(doc_b, field_name)

            if not val_a or not val_b:
                continue

            result = match_names(val_a, val_b)
            type_a = doc_a.detectedType or doc_a.expectedType
            type_b = doc_b.detectedType or doc_b.expectedType

            if result.result == NMResult.MISMATCH:
                severity = Severity.BLOCKING if on_mismatch == 'BLOCKING' else Severity.WARNING
                findings.append(Finding(
                    findingId=generate_finding_id('NM'),
                    ruleId=result.rule_id,
                    category='identity',
                    severity=severity,
                    evidence=[
                        EvidenceItem(documentType=type_a, documentId=doc_a.documentId,
                                     fieldName=field_name, value=val_a, confidence=conf_a),
                        EvidenceItem(documentType=type_b, documentId=doc_b.documentId,
                                     fieldName=field_name, value=val_b, confidence=conf_b),
                    ],
                    affectedDocuments=[doc_a.documentId, doc_b.documentId],
                    confidence=min(conf_a, conf_b),
                    deterministicMessage=f"Name mismatch between {type_a} and {type_b}: '{val_a}' vs '{val_b}'. {result.details}",
                    deterministicMessageHi=f"{type_a} और {type_b} में नाम मेल नहीं खाता: '{val_a}' बनाम '{val_b}'।",
                ))
            elif result.result == NMResult.MINOR_VARIATION:
                findings.append(Finding(
                    findingId=generate_finding_id('NM'),
                    ruleId=result.rule_id,
                    category='identity',
                    severity=Severity.INFO,
                    evidence=[
                        EvidenceItem(documentType=type_a, documentId=doc_a.documentId,
                                     fieldName=field_name, value=val_a, confidence=conf_a),
                        EvidenceItem(documentType=type_b, documentId=doc_b.documentId,
                                     fieldName=field_name, value=val_b, confidence=conf_b),
                    ],
                    affectedDocuments=[doc_a.documentId, doc_b.documentId],
                    confidence=min(conf_a, conf_b),
                    deterministicMessage=f"Minor name variation between {type_a} and {type_b}: '{val_a}' vs '{val_b}'. {result.details}",
                    deterministicMessageHi=f"{type_a} और {type_b} में नाम में मामूली अंतर: '{val_a}' बनाम '{val_b}'।",
                ))

    return findings


def _run_cross_document_dob_checks(
    documents: list[DocumentRecord],
    check: dict
) -> list[Finding]:
    """Run cross-document DOB matching."""
    findings: list[Finding] = []
    field_name = check.get('field', 'dob')
    check_docs = check.get('documents', [])
    on_mismatch = check.get('onMismatch', 'BLOCKING')

    relevant_docs = [d for d in documents if d.expectedType in check_docs or d.detectedType in check_docs]

    compared = set()
    for i, doc_a in enumerate(relevant_docs):
        for j, doc_b in enumerate(relevant_docs):
            if i >= j:
                continue
            pair_key = tuple(sorted([doc_a.documentId, doc_b.documentId]))
            if pair_key in compared:
                continue
            compared.add(pair_key)

            val_a, conf_a = _get_field_value(doc_a, field_name)
            val_b, conf_b = _get_field_value(doc_b, field_name)

            if not val_a or not val_b:
                continue

            type_a = doc_a.detectedType or doc_a.expectedType
            type_b = doc_b.detectedType or doc_b.expectedType
            result = compare_dob(val_a, val_b, type_a, type_b)

            if result.result == 'MISMATCH':
                severity = Severity.BLOCKING if on_mismatch == 'BLOCKING' else Severity.WARNING
                findings.append(Finding(
                    findingId=generate_finding_id('DOB'),
                    ruleId=result.rule_id,
                    category='dob',
                    severity=severity,
                    evidence=[
                        EvidenceItem(documentType=type_a, documentId=doc_a.documentId,
                                     fieldName=field_name, value=val_a, confidence=conf_a),
                        EvidenceItem(documentType=type_b, documentId=doc_b.documentId,
                                     fieldName=field_name, value=val_b, confidence=conf_b),
                    ],
                    affectedDocuments=[doc_a.documentId, doc_b.documentId],
                    deterministicMessage=f"Date of birth mismatch: {result.details}",
                    deterministicMessageHi=f"जन्म तिथि मेल नहीं खाती: {type_a} बनाम {type_b}।",
                ))
            elif result.result == 'AMBIGUOUS':
                findings.append(Finding(
                    findingId=generate_finding_id('DOB'),
                    ruleId=result.rule_id,
                    category='dob',
                    severity=Severity.REVIEW,
                    evidence=[
                        EvidenceItem(documentType=type_a, documentId=doc_a.documentId,
                                     fieldName=field_name, value=val_a, confidence=conf_a),
                        EvidenceItem(documentType=type_b, documentId=doc_b.documentId,
                                     fieldName=field_name, value=val_b, confidence=conf_b),
                    ],
                    affectedDocuments=[doc_a.documentId, doc_b.documentId],
                    deterministicMessage=f"Date of birth is ambiguous across documents. {result.details}",
                    deterministicMessageHi=f"जन्म तिथि दस्तावेज़ों में अस्पष्ट है। मैनुअल सत्यापन आवश्यक।",
                ))

    return findings


def _run_validity_checks(
    documents: list[DocumentRecord],
    document_rules: dict[str, dict],
    review_horizon_days: int,
    reference_date: Optional[date]
) -> list[Finding]:
    """Run validity/expiry checks on all documents."""
    findings: list[Finding] = []

    for doc in documents:
        doc_type = doc.detectedType or doc.expectedType
        rules = document_rules.get(doc_type, {})
        validity_rules = rules.get('validity', {})

        # Skip permanent documents (no expiry check needed)
        if validity_rules.get('type') == 'permanent':
            continue

        issue_val, _ = _get_field_value(doc, 'issueDate')
        expiry_val, _ = _get_field_value(doc, 'validUntil')

        result = check_validity(
            issue_date_str=issue_val,
            valid_until_str=expiry_val,
            validity_rules=validity_rules,
            review_horizon_days=review_horizon_days,
            reference_date=reference_date
        )

        if result.severity == 'RED':
            findings.append(Finding(
                findingId=generate_finding_id('VAL'),
                ruleId=result.rule_id,
                category='validity',
                severity=Severity.BLOCKING,
                evidence=[EvidenceItem(
                    documentType=doc_type, documentId=doc.documentId,
                    fieldName='validUntil',
                    value=result.valid_until.isoformat() if result.valid_until else 'unknown',
                    confidence=0.0
                )],
                affectedDocuments=[doc.documentId],
                deterministicMessage=result.details,
                deterministicMessageHi=f"{doc_type} की वैधता समाप्त हो गई है।",
            ))
        elif result.severity == 'ORANGE':
            findings.append(Finding(
                findingId=generate_finding_id('VAL'),
                ruleId=result.rule_id,
                category='validity',
                severity=Severity.WARNING,
                evidence=[EvidenceItem(
                    documentType=doc_type, documentId=doc.documentId,
                    fieldName='validUntil',
                    value=result.valid_until.isoformat() if result.valid_until else 'unknown',
                    confidence=0.0
                )],
                affectedDocuments=[doc.documentId],
                deterministicMessage=result.details,
                deterministicMessageHi=f"{doc_type} की वैधता जल्द समाप्त हो रही है।",
            ))
        elif result.severity == 'AMBER':
            findings.append(Finding(
                findingId=generate_finding_id('VAL'),
                ruleId=result.rule_id,
                category='validity',
                severity=Severity.REVIEW,
                evidence=[EvidenceItem(
                    documentType=doc_type, documentId=doc.documentId,
                    fieldName='validUntil', value='indeterminate', confidence=0.0
                )],
                affectedDocuments=[doc.documentId],
                deterministicMessage=result.details,
                deterministicMessageHi=f"{doc_type} की वैधता निर्धारित नहीं की जा सकी।",
            ))

    return findings


def _apply_confidence_downgrade(findings: list[Finding], documents: list[DocumentRecord]) -> None:
    """If a field with confidence < 90 is the SOLE basis of a BLOCKING finding,
    downgrade it to REVIEW. We must not tell a student their application will be
    rejected because our OCR was unsure."""
    for finding in findings:
        if finding.severity != Severity.BLOCKING:
            continue
        if not finding.evidence:
            continue

        # Check if ALL evidence items have low confidence
        low_confidence_items = [
            e for e in finding.evidence if 0 < e.confidence < 90
        ]
        if low_confidence_items and len(low_confidence_items) == len(finding.evidence):
            finding.severity = Severity.REVIEW
            finding.deterministicMessage += ' [Downgraded: OCR confidence below threshold.]'


def run_verification(
    documents: list[DocumentRecord],
    profile: dict,
    document_rules: dict[str, dict],
    reference_date: Optional[date] = None
) -> VerificationResult:
    """Run the full deterministic verification pipeline.

    Pure function. No AWS calls. Input: documents + profile + rules.
    Output: VerificationResult with all findings and deterministic readiness.

    Steps:
    1. Completeness checks on each document
    2. Cross-document name matching (profile-defined checks)
    3. Cross-document DOB matching
    4. Validity/expiry checks
    5. Confidence downgrade rule
    6. Aggregate -> deterministic readiness
    7. Stamp rulesetVersion
    """
    all_findings: list[Finding] = []
    ruleset_version = profile.get('rulesetVersion', '2026.09.1')
    review_horizon = profile.get('reviewHorizonDays', 45)

    # 1. Completeness checks
    for doc in documents:
        doc_type = doc.detectedType or doc.expectedType
        rules = document_rules.get(doc_type, {})
        required_fields = rules.get('requiredFields', [])
        completeness_findings = check_completeness(
            extracted_fields=doc.extractedFields,
            required_fields=required_fields,
            document_type=doc_type,
            document_id=doc.documentId
        )
        all_findings.extend(completeness_findings)

    # 2 & 3. Cross-document checks (profile-defined)
    cross_checks = profile.get('crossDocumentChecks', [])
    for check in cross_checks:
        matcher = check.get('matcher', '')
        if matcher == 'indic_name':
            all_findings.extend(_run_cross_document_name_checks(documents, check))
        elif matcher == 'exact_date':
            all_findings.extend(_run_cross_document_dob_checks(documents, check))

    # 4. Validity checks
    all_findings.extend(_run_validity_checks(
        documents, document_rules, review_horizon, reference_date
    ))

    # 5. Confidence downgrade
    _apply_confidence_downgrade(all_findings, documents)

    # 6. Aggregate deterministic readiness
    blocking = sum(1 for f in all_findings if f.severity == Severity.BLOCKING)
    review = sum(1 for f in all_findings if f.severity == Severity.REVIEW)
    warnings = sum(1 for f in all_findings if f.severity == Severity.WARNING)

    if blocking > 0:
        status = ReadinessStatus.RED
    elif review > 0:
        status = ReadinessStatus.AMBER
    elif warnings > 0:
        status = ReadinessStatus.ORANGE
    else:
        status = ReadinessStatus.GREEN

    return VerificationResult(
        sessionId=documents[0].sessionId if documents else '',
        readinessStatus=status,
        blockingCount=blocking,
        warningCount=warnings,
        reviewCount=review,
        findings=all_findings,
        rulesetVersion=ruleset_version,
        documents=documents
    )
