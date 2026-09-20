"""Deterministic weighted-signal document classifier.

No ML. No training. Fully explainable.
Each document type carries weighted regex signals in its rule pack.
Score every type; the winner must clear minScore and beat the runner-up by minMargin.
"""
import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

def _get_rules_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / 'rules' / 'documents',
        Path('/var/task/rules/documents'),
        Path(__file__).resolve().parent.parent.parent / 'rules' / 'documents',
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]

RULES_DIR = _get_rules_dir()


@dataclass
class ClassificationResult:
    """Result of document classification."""
    detected_type: str
    confidence_score: float
    runner_up_type: str
    runner_up_score: float
    margin: float
    is_confident: bool
    matches_expected: bool
    details: str
    all_scores: dict = field(default_factory=dict)


def _load_all_document_rules() -> list[dict]:
    """Load all document rule packs from the rules directory."""
    rules = []
    if not RULES_DIR.exists():
        return rules
    for f in sorted(RULES_DIR.glob('*.json')):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if 'documentType' in data and 'signals' in data:
                    rules.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return rules


def _score_document(raw_text: str, signals: list[dict]) -> float:
    """Score text against a list of weighted regex signals."""
    total = 0.0
    for signal in signals:
        pattern = signal.get('pattern', '')
        weight = signal.get('weight', 0)
        try:
            if re.search(pattern, raw_text):
                total += weight
        except re.error:
            continue
    return total


def classify_document(
    raw_text: str,
    expected_type: Optional[str] = None,
    document_rules: Optional[list[dict]] = None
) -> ClassificationResult:
    """Classify a document using deterministic weighted signal scoring.

    Scores every known document type against the extracted text.
    The winner must clear minScore AND beat the runner-up by minMargin,
    otherwise classification is marked as not confident (ambiguous).

    Args:
        raw_text: Raw OCR text from the document.
        expected_type: The document type the user declared (optional).
        document_rules: Pre-loaded rule packs. If None, loads from disk.

    Returns:
        ClassificationResult with detected type, scores, and confidence.
    """
    if document_rules is None:
        document_rules = _load_all_document_rules()

    if not document_rules:
        return ClassificationResult(
            detected_type='unknown',
            confidence_score=0.0,
            runner_up_type='',
            runner_up_score=0.0,
            margin=0.0,
            is_confident=False,
            matches_expected=False,
            details='No document rule packs available.',
            all_scores={}
        )

    # Score every document type
    scores: dict[str, float] = {}
    min_scores: dict[str, float] = {}
    min_margins: dict[str, float] = {}

    for rule in document_rules:
        doc_type = rule['documentType']
        signals = rule.get('signals', [])
        scores[doc_type] = _score_document(raw_text, signals)
        min_scores[doc_type] = rule.get('minScore', 50)
        min_margins[doc_type] = rule.get('minMargin', 20)

    # Sort by score descending
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    winner_type, winner_score = sorted_types[0]
    runner_up_type = sorted_types[1][0] if len(sorted_types) > 1 else ''
    runner_up_score = sorted_types[1][1] if len(sorted_types) > 1 else 0.0
    margin = winner_score - runner_up_score

    # Confidence: winner must clear its own minScore AND beat runner-up by minMargin
    required_min_score = min_scores.get(winner_type, 50)
    required_min_margin = min_margins.get(winner_type, 20)
    is_confident = (winner_score >= required_min_score) and (margin >= required_min_margin)

    matches_expected = (expected_type == winner_type) if expected_type else True

    # Build human-readable details
    if is_confident:
        details = (
            f"Detected {winner_type} (score {winner_score:.0f}) "
            f"vs {runner_up_type} (score {runner_up_score:.0f}), "
            f"margin {margin:.0f}."
        )
    else:
        details = (
            f"Ambiguous: {winner_type} (score {winner_score:.0f}) "
            f"vs {runner_up_type} (score {runner_up_score:.0f}), "
            f"margin {margin:.0f}. "
            f"Required minScore={required_min_score}, minMargin={required_min_margin}."
        )

    return ClassificationResult(
        detected_type=winner_type,
        confidence_score=winner_score,
        runner_up_type=runner_up_type,
        runner_up_score=runner_up_score,
        margin=margin,
        is_confident=is_confident,
        matches_expected=matches_expected,
        details=details,
        all_scores=dict(scores)
    )
