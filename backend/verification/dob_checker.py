"""Date of Birth comparison engine.

Pure Python. No AWS dependencies.
Handles Indian document date formats (DD/MM/YYYY default)
and DD/MM vs MM/DD ambiguity.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
import re


@dataclass
class DobComparisonResult:
    """Result of a DOB cross-document comparison."""
    result: str  # MATCH, MISMATCH, AMBIGUOUS
    rule_id: str  # DOB-01, DOB-02, DOB-03
    parsed_a: Optional[str]
    parsed_b: Optional[str]
    assumed_format_a: Optional[str]
    assumed_format_b: Optional[str]
    details: str


def _parse_dob(dob_str: str) -> tuple[Optional[date], str, bool]:
    """Parse a DOB string. Returns (parsed_date, assumed_format, is_ambiguous).

    Indian documents default to DD/MM/YYYY.
    Ambiguity: if day <= 12, both DD/MM and MM/DD are valid.
    """
    if not dob_str or not dob_str.strip():
        return None, '', False

    dob_str = dob_str.strip()

    # Try YYYY-MM-DD / YYYY/MM/DD
    m = re.match(r'^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$', dob_str)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d), 'YYYY-MM-DD', False
        except ValueError:
            return None, '', False

    # Try DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    m = re.match(r'^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$', dob_str)
    if m:
        p1, p2, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        is_ambiguous = (p1 <= 12 and p2 <= 12)

        # Default: DD/MM/YYYY for Indian documents
        try:
            parsed = date(y, p2, p1)  # DD/MM/YYYY -> date(y, month=p2, day=p1)
            return parsed, 'DD/MM/YYYY', is_ambiguous
        except ValueError:
            # Try MM/DD/YYYY as fallback
            try:
                parsed = date(y, p1, p2)
                return parsed, 'MM/DD/YYYY', is_ambiguous
            except ValueError:
                return None, '', False

    return None, '', False


def compare_dob(
    dob_a: str,
    dob_b: str,
    doc_type_a: str = '',
    doc_type_b: str = ''
) -> DobComparisonResult:
    """Compare dates of birth from two documents.

    Rules:
    - If both parse and match -> DOB-01 MATCH
    - If both parse but differ, AND one is ambiguous, try alternate format ->
      if reconcilable under different formats -> DOB-02 AMBIGUOUS (REVIEW)
    - If genuinely different -> DOB-03 MISMATCH (BLOCKING)
    """
    date_a, fmt_a, ambig_a = _parse_dob(dob_a)
    date_b, fmt_b, ambig_b = _parse_dob(dob_b)

    str_a = date_a.isoformat() if date_a else None
    str_b = date_b.isoformat() if date_b else None

    if date_a is None or date_b is None:
        return DobComparisonResult(
            result='MISMATCH',
            rule_id='DOB-03',
            parsed_a=str_a,
            parsed_b=str_b,
            assumed_format_a=fmt_a or None,
            assumed_format_b=fmt_b or None,
            details=f'Could not parse one or both dates. A="{dob_a}" B="{dob_b}".'
        )

    if date_a == date_b:
        return DobComparisonResult(
            result='MATCH',
            rule_id='DOB-01',
            parsed_a=str_a,
            parsed_b=str_b,
            assumed_format_a=fmt_a,
            assumed_format_b=fmt_b,
            details='Dates of birth match.'
        )

    # Check if ambiguity could reconcile the dates
    if ambig_a or ambig_b:
        # Try swapping day/month on the ambiguous one
        if ambig_a:
            swapped_a = date(date_a.year, date_a.day, date_a.month)
            if swapped_a == date_b:
                return DobComparisonResult(
                    result='AMBIGUOUS',
                    rule_id='DOB-02',
                    parsed_a=str_a,
                    parsed_b=str_b,
                    assumed_format_a=fmt_a,
                    assumed_format_b=fmt_b,
                    details=(
                        f'Dates can be reconciled under different format assumptions. '
                        f'{doc_type_a}: {dob_a} ({fmt_a}), {doc_type_b}: {dob_b} ({fmt_b}). '
                        f'Manual verification recommended.'
                    )
                )
        if ambig_b:
            try:
                swapped_b = date(date_b.year, date_b.day, date_b.month)
                if date_a == swapped_b:
                    return DobComparisonResult(
                        result='AMBIGUOUS',
                        rule_id='DOB-02',
                        parsed_a=str_a,
                        parsed_b=str_b,
                        assumed_format_a=fmt_a,
                        assumed_format_b=fmt_b,
                        details=(
                            f'Dates can be reconciled under different format assumptions. '
                            f'Manual verification recommended.'
                        )
                    )
            except ValueError:
                pass

    return DobComparisonResult(
        result='MISMATCH',
        rule_id='DOB-03',
        parsed_a=str_a,
        parsed_b=str_b,
        assumed_format_a=fmt_a,
        assumed_format_b=fmt_b,
        details=f'Dates of birth differ. {doc_type_a}: {date_a.isoformat()}, {doc_type_b}: {date_b.isoformat()}.'
    )
