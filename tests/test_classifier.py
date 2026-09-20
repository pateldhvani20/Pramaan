import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.classification.classifier import classify_document


class TestAadhaarClassification:
    def test_aadhaar_text(self):
        text = "Government of India Unique Identification Authority of India AADHAAR 1234 5678 9012 DOB: 15/08/2000"
        r = classify_document(text, expected_type='aadhaar')
        assert r.detected_type == 'aadhaar'
        assert r.is_confident
        assert r.matches_expected


class TestMarksheetClassification:
    def test_marksheet_text(self):
        text = "Central Board of Secondary Education Board Exam Marks Obtained Roll No 12345678 Percentage 85.6%"
        r = classify_document(text, expected_type='marksheet')
        assert r.detected_type == 'marksheet'
        assert r.is_confident


class TestIncomeCertificateClassification:
    def test_income_cert_text(self):
        text = "Income Certificate Annual Income Rs 2,50,000 issued by Tahsildar Revenue Department"
        r = classify_document(text, expected_type='income_certificate')
        assert r.detected_type == 'income_certificate'
        assert r.is_confident


class TestDomicileClassification:
    def test_domicile_text(self):
        text = "Domicile Certificate permanent resident District Collector state of Maharashtra"
        r = classify_document(text, expected_type='domicile')
        assert r.detected_type == 'domicile'
        assert r.is_confident


class TestMisclassification:
    def test_marksheet_as_income_cert(self):
        """E02: Wrong document type detection"""
        text = "Marks Obtained Roll No Board Exam Results Percentage CGPA"
        r = classify_document(text, expected_type='income_certificate')
        assert not r.matches_expected


class TestAmbiguous:
    def test_minimal_text(self):
        """E12: Ambiguous classification"""
        text = "Government document official seal"
        r = classify_document(text)
        assert not r.is_confident
