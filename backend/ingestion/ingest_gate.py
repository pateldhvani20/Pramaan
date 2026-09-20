import struct
import hashlib
from io import BytesIO
from dataclasses import dataclass
from typing import Optional
from enum import Enum

try:
    from pypdf import PdfReader
    from pypdf.errors import PdfError
except ImportError:
    pass

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    pass

MAGIC_BYTES = {
    'application/pdf': b'%PDF-',
    'image/jpeg': b'\xff\xd8\xff',
    'image/png': b'\x89PNG\r\n\x1a\n',
}

ALLOWED_CONTENT_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PAGE_COUNT = 50

class IngestResult(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

@dataclass
class IngestGateResult:
    result: IngestResult
    sha256: str
    page_count: int
    size: int
    detected_content_type: str
    reason: Optional[str] = None
    reason_internal: Optional[str] = None

def validate_magic_bytes(data: bytes, declared_type: str) -> bool:
    if declared_type not in MAGIC_BYTES:
        return False
    magic = MAGIC_BYTES[declared_type]
    return data.startswith(magic)

def validate_file_size(size: int) -> Optional[IngestResult]:
    if size > MAX_FILE_SIZE:
        return IngestResult.REJECTED
    return None

def check_pdf_encrypted(data: bytes) -> bool:
    try:
        reader = PdfReader(BytesIO(data))
        return reader.is_encrypted
    except Exception:
        return True

def count_pdf_pages(data: bytes) -> int:
    try:
        reader = PdfReader(BytesIO(data))
        return len(reader.pages)
    except Exception:
        return -1

def validate_image(data: bytes) -> bool:
    try:
        img = Image.open(BytesIO(data))
        img.verify()
        return True
    except Exception:
        return False

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run_ingest_gate(file_data: bytes, declared_content_type: str, declared_filename: str) -> IngestGateResult:
    size = len(file_data)
    sha256_hash = compute_sha256(file_data)
    
    if validate_file_size(size) == IngestResult.REJECTED:
        return IngestGateResult(IngestResult.REJECTED, sha256_hash, 0, size, declared_content_type, "File is too large.", "Exceeded MAX_FILE_SIZE")
    
    if declared_content_type not in ALLOWED_CONTENT_TYPES:
        return IngestGateResult(IngestResult.REJECTED, sha256_hash, 0, size, declared_content_type, "Unsupported file type.", "Content type not in ALLOWED_CONTENT_TYPES")
        
    if not validate_magic_bytes(file_data, declared_content_type):
        return IngestGateResult(IngestResult.REJECTED, sha256_hash, 0, size, declared_content_type, "Invalid file format.", "Magic bytes mismatch")

    page_count = 1
    if declared_content_type == 'application/pdf':
        if check_pdf_encrypted(file_data):
            return IngestGateResult(IngestResult.REJECTED, sha256_hash, 0, size, declared_content_type, "PDF is encrypted.", "PDF is encrypted")
        page_count = count_pdf_pages(file_data)
        if page_count < 1 or page_count > MAX_PAGE_COUNT:
            return IngestGateResult(IngestResult.REJECTED, sha256_hash, page_count, size, declared_content_type, "Invalid page count.", "Exceeded MAX_PAGE_COUNT or unreadable")
    else:
        if not validate_image(file_data):
            return IngestGateResult(IngestResult.REJECTED, sha256_hash, 0, size, declared_content_type, "Invalid image format.", "Image validation failed")
            
    return IngestGateResult(IngestResult.ACCEPTED, sha256_hash, page_count, size, declared_content_type)
