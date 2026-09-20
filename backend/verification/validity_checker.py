"""Document validity and expiry checker.

Pure Python. No AWS dependencies.
Three paths:
1. Printed validUntil -> use it
2. No printed expiry -> rule-derived: issueDate + validity.monthsFromIssue
3. Neither date extractable -> INDETERMINATE -> review
"""
from dataclasses import dataclass
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import re
from typing import Optional


@dataclass
class ValidityResult:
    """Result of a document validity check."""
    severity: str  # RED, ORANGE, GREEN, AMBER
    rule_id: str   # VAL-01..VAL-04
    valid_until: Optional[date]
    is_rule_derived: bool
    details: str


DATE_FORMATS = [
    (r'^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$', 'DMY'),
    (r'^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$', 'YMD'),
]


def parse_date_flexible(date_str: str) -> Optional[date]:
    """Parse a date string in common Indian document formats.
    Default assumption: DD/MM/YYYY for Indian documents.
    """
    if not date_str or not date_str.strip():
        return None
    date_str = date_str.strip()

    for pattern, fmt in DATE_FORMATS:
        m = re.match(pattern, date_str)
        if m:
            groups = [int(g) for g in m.groups()]
            try:
                if fmt == 'DMY':
                    return date(groups[2], groups[1], groups[0])
                elif fmt == 'YMD':
                    return date(groups[0], groups[1], groups[2])
            except ValueError:
                continue
    return None


def check_validity(
    issue_date_str: Optional[str],
    valid_until_str: Optional[str],
    validity_rules: dict,
    review_horizon_days: int = 45,
    reference_date: Optional[date] = None
) -> ValidityResult:
    """Check document validity against rules and review horizon.

    Args:
        issue_date_str: Extracted issue date string.
        valid_until_str: Extracted validity/expiry date string.
        validity_rules: From document rule pack, e.g. {"type": "rule_derived", "monthsFromIssue": 12}
        review_horizon_days: From profile, e.g. 45.
        reference_date: Override for testing. Defaults to today.

    Returns:
        ValidityResult with severity, rule_id, and details.
    """
    today = reference_date or date.today()
    is_rule_derived = False

    # Path 1: Printed validUntil
    expiry = parse_date_flexible(valid_until_str or '')

    # Path 2: Rule-derived from issueDate
    if expiry is None and issue_date_str:
        issue_date = parse_date_flexible(issue_date_str)
        validity_type = validity_rules.get('type', '')

        if issue_date and validity_type == 'rule_derived':
            months = validity_rules.get('monthsFromIssue', 0)
            if months > 0:
                try:
                    expiry = issue_date + relativedelta(months=months)
                    is_rule_derived = True
                except Exception:
                    expiry = issue_date + timedelta(days=months * 30)
                    is_rule_derived = True
        elif issue_date is None and validity_type != 'permanent':
            pass  # Fall through to path 3

    # Permanent documents (Aadhaar, Marksheet) — always valid
    if validity_rules.get('type') == 'permanent':
        return ValidityResult(
            severity='GREEN',
            rule_id='VAL-03',
            valid_until=None,
            is_rule_derived=False,
            details='Document type has permanent validity.'
        )

    # Path 3: Neither date extractable
    if expiry is None:
        return ValidityResult(
            severity='AMBER',
            rule_id='VAL-04',
            valid_until=None,
            is_rule_derived=False,
            details='Could not determine document validity. Neither expiry date nor issue date could be extracted.'
        )

    # Forward-looking checks
    derived_note = ' (rule-derived)' if is_rule_derived else ''

    if expiry < today:
        days_expired = (today - expiry).days
        return ValidityResult(
            severity='RED',
            rule_id='VAL-01',
            valid_until=expiry,
            is_rule_derived=is_rule_derived,
            details=f'Document expired {days_expired} days ago on {expiry.isoformat()}{derived_note}.'
        )

    horizon_end = today + timedelta(days=review_horizon_days)
    if expiry < horizon_end:
        days_left = (expiry - today).days
        return ValidityResult(
            severity='ORANGE',
            rule_id='VAL-02',
            valid_until=expiry,
            is_rule_derived=is_rule_derived,
            details=f'Document expires in {days_left} days on {expiry.isoformat()}{derived_note}. May lapse before review completes.'
        )

    return ValidityResult(
        severity='GREEN',
        rule_id='VAL-03',
        valid_until=expiry,
        is_rule_derived=is_rule_derived,
        details=f'Document valid until {expiry.isoformat()}{derived_note}.'
    )
