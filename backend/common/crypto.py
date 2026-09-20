"""
Crypto and hashing utilities.
Provides secure random generation and SHA-256 operations.
"""
import hashlib
import secrets
from typing import BinaryIO

BUFFER_SIZE = 65536  # 64KB chunks

def compute_sha256(file_obj: BinaryIO) -> str:
    """Compute SHA-256 hash of a file object."""
    sha256 = hashlib.sha256()
    while True:
        data = file_obj.read(BUFFER_SIZE)
        if not data:
            break
        sha256.update(data)
    file_obj.seek(0)  # Reset for subsequent reads
    return sha256.hexdigest()

def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()

def generate_session_id() -> str:
    """Generate a cryptographically secure 128-bit session ID (OWASP A07)."""
    return secrets.token_urlsafe(16)

def generate_document_id() -> str:
    """Generate a cryptographically secure document ID."""
    return secrets.token_urlsafe(12)

def generate_finding_id(prefix: str = 'F') -> str:
    """Generate a finding ID with a prefix."""
    return f"{prefix}-{secrets.token_hex(4).upper()}"

def hash_sensitive_value(value: str, salt: str) -> str:
    """Hash a sensitive value (e.g., Aadhaar number) with a per-session salt.
    Returns first 16 chars of the hash for linkage without storage."""
    combined = f"{value.strip()}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]
