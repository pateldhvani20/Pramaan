import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.verification.name_matcher import match_names


class TestExactMatch:
    def test_identical_names(self):
        r = match_names('Kunal Borse', 'Kunal Borse')
        assert r.result.value == 'MATCH'
        assert r.rule_id == 'NM-01'

    def test_case_insensitive(self):
        r = match_names('kunal borse', 'KUNAL BORSE')
        assert r.result.value == 'MATCH'

    def test_honorific_stripped(self):
        r = match_names('Shri Kunal Borse', 'Kunal Borse')
        assert r.result.value == 'MATCH'


class TestTransliterationFolding:
    def test_aashish_ashish(self):
        """AA -> A fold: Aashish == Ashish"""
        r = match_names('Aashish Kumar', 'Ashish Kumar')
        assert r.result.value == 'MATCH'

    def test_v_w_interchange(self):
        """V <-> W: Vikas == Wikas"""
        r = match_names('Vikas Sharma', 'Wikas Sharma')
        assert r.result.value == 'MATCH'

    def test_ph_f_interchange(self):
        """PH -> F: Phalguni == Falguni"""
        r = match_names('Phalguni Patel', 'Falguni Patel')
        assert r.result.value == 'MATCH'


class TestSubsetMatch:
    def test_middle_name_present_vs_absent(self):
        """Kunal Bapurao Borse vs Kunal Borse -> MINOR_VARIATION (NM-02)"""
        r = match_names('Kunal Bapurao Borse', 'Kunal Borse')
        assert r.result.value == 'MINOR_VARIATION'
        assert r.rule_id == 'NM-02'


class TestOrderVariation:
    def test_name_order_swap(self):
        """Borse Kunal vs Kunal Borse -> MINOR_VARIATION (NM-03)"""
        r = match_names('Borse Kunal', 'Kunal Borse')
        assert r.result.value == 'MINOR_VARIATION'
        assert r.rule_id == 'NM-03'


class TestMismatch:
    def test_completely_different_names(self):
        """Rahul Borse vs Kunal Borse -> MISMATCH (NM-06)"""
        r = match_names('Rahul Borse', 'Kunal Borse')
        assert r.result.value == 'MISMATCH'
        assert r.rule_id == 'NM-06'

    def test_completely_different_full_names(self):
        r = match_names('Amit Singh', 'Priya Sharma')
        assert r.result.value == 'MISMATCH'
