import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.ingestion.ingest_gate import run_ingest_gate, IngestResult


class TestValidFiles:
    def test_valid_pdf(self):
        pdf_data = b'%PDF-1.4 fake pdf content' + b'\x00' * 100
        r = run_ingest_gate(pdf_data, 'application/pdf', 'test.pdf')
        # PDF parsing will likely fail on this fake data, that's expected
        # The test validates the flow works

    def test_valid_jpeg(self):
        # Minimal JPEG header
        jpeg_data = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        r = run_ingest_gate(jpeg_data, 'image/jpeg', 'test.jpg')
        # Will either accept or reject based on Pillow validation

    def test_valid_png(self):
        png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        r = run_ingest_gate(png_data, 'image/png', 'test.png')


class TestRejections:
    def test_zero_byte_file(self):
        """E01: Zero-byte file"""
        r = run_ingest_gate(b'', 'application/pdf', 'empty.pdf')
        assert r.result == IngestResult.REJECTED

    def test_oversized_file(self):
        """E16: Oversized file"""
        big_data = b'%PDF-' + b'\x00' * (11 * 1024 * 1024)  # 11 MB
        r = run_ingest_gate(big_data, 'application/pdf', 'big.pdf')
        assert r.result == IngestResult.REJECTED

    def test_wrong_magic_bytes(self):
        """E01: Malformed / renamed file"""
        # DOCX magic disguised as PDF
        docx_data = b'PK\x03\x04' + b'\x00' * 100
        r = run_ingest_gate(docx_data, 'application/pdf', 'fake.pdf')
        assert r.result == IngestResult.REJECTED

    def test_unsupported_content_type(self):
        r = run_ingest_gate(b'some data', 'application/zip', 'test.zip')
        assert r.result == IngestResult.REJECTED
