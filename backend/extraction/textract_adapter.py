import os
from dataclasses import dataclass
from typing import Any

MODE = os.environ.get('DOCVERIFY_EXTRACTION_MODE', 'mock')

@dataclass
class ExtractedField:
    key: str
    value: str
    confidence: float

@dataclass
class ExtractionResult:
    fields: list[ExtractedField]
    raw_text: str
    confidence_scores: dict
    page_count: int

def _mock_extract(document_type: str) -> ExtractionResult:
    return ExtractionResult(
        fields=[
            ExtractedField("name", "MOCK NAME", 99.0),
            ExtractedField("dob", "01/01/1990", 99.0)
        ],
        raw_text="MOCK RAW TEXT OF DOCUMENT",
        confidence_scores={"name": 99.0, "dob": 99.0},
        page_count=1
    )

def _textract_extract(document_bytes: bytes, queries: list[dict]) -> ExtractionResult:
    # Boto3 would be used here in actual LIVE mode
    return ExtractionResult(
        fields=[],
        raw_text="LIVE TEXTRACT TEXT",
        confidence_scores={},
        page_count=1
    )

def extract_document(document_bytes: bytes, document_type: str, queries: list[dict]) -> ExtractionResult:
    """Extract fields from document using Textract or mock."""
    if MODE == 'mock':
        return _mock_extract(document_type)
    return _textract_extract(document_bytes, queries)
