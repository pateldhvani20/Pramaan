"""DocVerify Verification Engine — pure Python, zero AWS dependencies."""
from .name_matcher import match_names, NameComparisonResult, jaro_winkler
from .dob_checker import compare_dob, DobComparisonResult
from .validity_checker import check_validity, ValidityResult
from .completeness_checker import check_completeness
from .engine import run_verification

__all__ = [
    'match_names', 'NameComparisonResult', 'jaro_winkler',
    'compare_dob', 'DobComparisonResult',
    'check_validity', 'ValidityResult',
    'check_completeness',
    'run_verification',
]
