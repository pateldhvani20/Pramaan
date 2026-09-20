import pytest
import sys, os
import json
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.common.models import DocumentRecord, ExtractedField, ReadinessStatus
from backend.verification.engine import run_verification

# Load rule packs
RULES_DIR = os.path.join(os.path.dirname(__file__), '..', 'rules')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

PROFILE = load_json(os.path.join(RULES_DIR, 'profiles', 'post-matric-scholarship.json'))
DOC_RULES = {
    'aadhaar': load_json(os.path.join(RULES_DIR, 'documents', 'aadhaar.json')),
    'marksheet': load_json(os.path.join(RULES_DIR, 'documents', 'marksheet.json')),
    'income_certificate': load_json(os.path.join(RULES_DIR, 'documents', 'income_certificate.json')),
    'domicile': load_json(os.path.join(RULES_DIR, 'documents', 'domicile.json')),
}

def make_doc(doc_id, session_id, doc_type, fields):
    return DocumentRecord(
        documentId=doc_id,
        sessionId=session_id,
        expectedType=doc_type,
        detectedType=doc_type,
        extractedFields=[
            ExtractedField(
                fieldId=f'{doc_id}-{k}',
                fieldName=k,
                rawValue=v,
                normalizedValue=v,
                confidence=95.0,
                sourceDocumentId=doc_id
            ) for k, v in fields.items()
        ]
    )


class TestCleanSet:
    def test_all_matching_documents_ready(self):
        """f01: Clean set -> GREEN/READY"""
        docs = [
            make_doc('d1', 's1', 'aadhaar', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000'}),
            make_doc('d2', 's1', 'marksheet', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000', 'passingYear': '2018'}),
            make_doc('d3', 's1', 'income_certificate', {'applicantName': 'Kunal Borse', 'issueDate': '01/06/2026', 'incomeAmount': '250000'}),
            make_doc('d4', 's1', 'domicile', {'applicantName': 'Kunal Borse', 'issueDate': '01/01/2025'}),
        ]
        result = run_verification(docs, PROFILE, DOC_RULES, reference_date=date(2026, 9, 20))
        assert result.readinessStatus == ReadinessStatus.GREEN
        assert result.blockingCount == 0


class TestNameMismatch:
    def test_different_first_name_blocks(self):
        """f03: Kunal vs Rahul -> RED/NOT_READY"""
        docs = [
            make_doc('d1', 's1', 'aadhaar', {'applicantName': 'Rahul Borse', 'dob': '15/08/2000'}),
            make_doc('d2', 's1', 'marksheet', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000', 'passingYear': '2018'}),
            make_doc('d3', 's1', 'income_certificate', {'applicantName': 'Kunal Borse', 'issueDate': '01/06/2026', 'incomeAmount': '250000'}),
            make_doc('d4', 's1', 'domicile', {'applicantName': 'Kunal Borse', 'issueDate': '01/01/2025'}),
        ]
        result = run_verification(docs, PROFILE, DOC_RULES, reference_date=date(2026, 9, 20))
        assert result.readinessStatus == ReadinessStatus.RED
        assert result.blockingCount > 0


class TestNameVariation:
    def test_transliteration_fold_passes(self):
        """f02: Aashish vs Ashish -> should not produce blocking finding"""
        docs = [
            make_doc('d1', 's1', 'aadhaar', {'applicantName': 'Aashish Kumar', 'dob': '15/08/2000'}),
            make_doc('d2', 's1', 'marksheet', {'applicantName': 'Ashish Kumar', 'dob': '15/08/2000', 'passingYear': '2018'}),
            make_doc('d3', 's1', 'income_certificate', {'applicantName': 'Ashish Kumar', 'issueDate': '01/06/2026', 'incomeAmount': '250000'}),
            make_doc('d4', 's1', 'domicile', {'applicantName': 'Ashish Kumar', 'issueDate': '01/01/2025'}),
        ]
        result = run_verification(docs, PROFILE, DOC_RULES, reference_date=date(2026, 9, 20))
        assert result.blockingCount == 0


class TestExpiredDocument:
    def test_income_cert_expired(self):
        """f07: Income cert issued 14 months ago -> RED"""
        docs = [
            make_doc('d1', 's1', 'aadhaar', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000'}),
            make_doc('d2', 's1', 'marksheet', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000', 'passingYear': '2018'}),
            make_doc('d3', 's1', 'income_certificate', {'applicantName': 'Kunal Borse', 'issueDate': '01/07/2025', 'incomeAmount': '250000'}),
            make_doc('d4', 's1', 'domicile', {'applicantName': 'Kunal Borse', 'issueDate': '01/01/2025'}),
        ]
        result = run_verification(docs, PROFILE, DOC_RULES, reference_date=date(2026, 9, 20))
        assert result.readinessStatus == ReadinessStatus.RED
        # Should have a VAL-01 finding
        val_findings = [f for f in result.findings if f.ruleId == 'VAL-01']
        assert len(val_findings) > 0


class TestLowConfidence:
    def test_low_confidence_downgrades_blocking(self):
        """f09: Low confidence -> REVIEW not BLOCKING"""
        docs = [
            make_doc('d1', 's1', 'aadhaar', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000'}),
            make_doc('d2', 's1', 'marksheet', {'applicantName': 'Kunal Borse', 'dob': '15/08/2000', 'passingYear': '2018'}),
        ]
        # Manually set low confidence on one field
        docs[0].extractedFields[0].confidence = 65.0  # name with low confidence
        docs[1].extractedFields[0].confidence = 65.0

        result = run_verification(docs, PROFILE, DOC_RULES, reference_date=date(2026, 9, 20))
        # Any name-related blocking findings should be downgraded
        blocking_name = [f for f in result.findings if f.category == 'identity' and f.severity.value == 'BLOCKING']
        assert len(blocking_name) == 0
