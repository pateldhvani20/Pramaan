import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from datetime import date
from backend.verification.validity_checker import check_validity


class TestExpired:
    def test_expired_document(self):
        """Income cert issued 14 months ago -> RED expired"""
        r = check_validity(
            issue_date_str='01/07/2025',
            valid_until_str=None,
            validity_rules={'type': 'rule_derived', 'monthsFromIssue': 12},
            review_horizon_days=45,
            reference_date=date(2026, 9, 20)
        )
        assert r.severity == 'RED'
        assert r.rule_id == 'VAL-01'


class TestLapsing:
    def test_expires_within_horizon(self):
        """Expires in 20 days, horizon 45 -> ORANGE"""
        r = check_validity(
            issue_date_str=None,
            valid_until_str='10/10/2026',
            validity_rules={'type': 'explicit'},
            review_horizon_days=45,
            reference_date=date(2026, 9, 20)
        )
        assert r.severity == 'ORANGE'
        assert r.rule_id == 'VAL-02'


class TestValid:
    def test_well_within_validity(self):
        r = check_validity(
            issue_date_str='01/06/2026',
            valid_until_str=None,
            validity_rules={'type': 'rule_derived', 'monthsFromIssue': 12},
            review_horizon_days=45,
            reference_date=date(2026, 9, 20)
        )
        assert r.severity == 'GREEN'
        assert r.rule_id == 'VAL-03'

    def test_permanent_document(self):
        r = check_validity(
            issue_date_str=None,
            valid_until_str=None,
            validity_rules={'type': 'permanent'},
            reference_date=date(2026, 9, 20)
        )
        assert r.severity == 'GREEN'


class TestIndeterminate:
    def test_no_dates_available(self):
        r = check_validity(
            issue_date_str=None,
            valid_until_str=None,
            validity_rules={'type': 'rule_derived', 'monthsFromIssue': 12},
            reference_date=date(2026, 9, 20)
        )
        assert r.severity == 'AMBER'
        assert r.rule_id == 'VAL-04'
