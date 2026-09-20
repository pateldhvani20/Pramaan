"""
OWASP Input Sanitization (Prompt Injection Defense).
Critical OWASP A03 defense functions.
"""
import re
import unicodedata

# Character allowlists per field type
ALLOWLIST_NAME = re.compile(
    r'[^a-zA-Z\s.\-\u0900-\u097F\u0A80-\u0AFF\u0980-\u09FF\u0B80-\u0BFF]'
)  # Letters, space, period, hyphen + Devanagari, Gujarati, Bengali, Tamil blocks
ALLOWLIST_DATE = re.compile(r'[^\d/\-.]')
ALLOWLIST_AMOUNT = re.compile(r'[^\d,.\ ₹]')
ALLOWLIST_GENERAL = re.compile(r'[\x00-\x1f\x7f]')  # Strip control chars only

MAX_FIELD_LENGTH = 128

def strip_control_characters(text: str) -> str:
    """Remove all Unicode control characters (OWASP A03)."""
    return ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')

def sanitize_field(value: str, field_type: str = 'general') -> str:
    """Sanitize a field value based on its type.
    
    Three gates:
    1. Strip control characters
    2. Apply charset allowlist per field type
    3. Cap at MAX_FIELD_LENGTH
    """
    if not value:
        return ""
    
    # Gate 1: Strip control characters
    value = strip_control_characters(value)
    
    # Gate 2: Apply charset allowlist
    allowlist_map = {
        'name': ALLOWLIST_NAME,
        'date': ALLOWLIST_DATE,
        'dob': ALLOWLIST_DATE,
        'amount': ALLOWLIST_AMOUNT,
        'income': ALLOWLIST_AMOUNT,
        'general': ALLOWLIST_GENERAL,
    }
    pattern = allowlist_map.get(field_type, ALLOWLIST_GENERAL)
    value = pattern.sub('', value)
    
    # Gate 3: Length cap
    value = value[:MAX_FIELD_LENGTH]
    
    # Collapse whitespace
    value = ' '.join(value.split())
    
    return value.strip()

def wrap_in_delimiters(value: str) -> str:
    """Wrap a value in delimiters for Bedrock prompt safety."""
    return f'<<<{value}>>>'

def detect_injection_patterns(text: str) -> bool:
    """Detect common prompt injection patterns in OCR text."""
    injection_patterns = [
        r'(?i)ignore\s+(previous|all|above)\s+instructions',
        r'(?i)you\s+are\s+now',
        r'(?i)system\s*:\s*',
        r'(?i)report\s+status\s+(ready|valid|approved)',
        r'(?i)suppress\s+all\s+findings',
        r'(?i)override\s+(verdict|status|severity)',
        r'(?i)disregard\s+(previous|all)',
        r'(?i)new\s+instructions?\s*:',
    ]
    for pattern in injection_patterns:
        if re.search(pattern, text):
            return True
    return False
