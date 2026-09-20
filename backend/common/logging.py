"""
Structured JSON Logging with PII Redaction.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

# Fields that must NEVER be logged
SENSITIVE_FIELD_PATTERNS = {
    'aadhaar', 'aadhar', 'pan', 'name', 'applicantName', 'guardianName',
    'dob', 'dateOfBirth', 'address', 'phone', 'mobile', 'email',
    'account', 'bank', 'ifsc',
}

def redact(value: Any, field_name: str = '') -> str:
    """Redact sensitive values. This is the ONLY way values get logged."""
    field_lower = field_name.lower()
    
    # Check if field is sensitive
    for pattern in SENSITIVE_FIELD_PATTERNS:
        if pattern in field_lower:
            if isinstance(value, str) and len(value) > 4:
                return f"{value[:2]}***{value[-2:]}"
            return '***REDACTED***'
    
    # Check for long numbers (potential PII)
    str_val = str(value)
    if len(str_val) > 6 and str_val.replace(' ', '').isdigit():
        return f"{str_val[:3]}***{str_val[-2:]}"
    
    return str_val

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }
        # Add structured context if available
        if hasattr(record, 'verification_id'):
            log_entry['verificationId'] = record.verification_id
        if hasattr(record, 'stage'):
            log_entry['stage'] = record.stage
        if hasattr(record, 'document_type'):
            log_entry['documentType'] = record.document_type
        if hasattr(record, 'status'):
            log_entry['status'] = record.status
        if hasattr(record, 'extra_data'):
            log_entry['data'] = record.extra_data
        return json.dumps(log_entry, default=str)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def log_stage(logger: logging.Logger, verification_id: str, stage: str,
              status: str, document_type: str = '', **kwargs):
    extra = {
        'verification_id': verification_id,
        'stage': stage,
        'status': status,
        'document_type': document_type,
    }
    if kwargs:
        extra['extra_data'] = {k: redact(v, k) for k, v in kwargs.items()}
    logger.info(f'{stage}: {status}', extra=extra)
