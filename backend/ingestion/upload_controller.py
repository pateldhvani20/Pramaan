import boto3
import uuid

def generate_session_id() -> str:
    return str(uuid.uuid4())

def generate_document_id() -> str:
    return str(uuid.uuid4())

def create_verification_session(profile_id: str, language: str = 'en') -> dict:
    """Create a new verification session and return session metadata."""
    session_id = generate_session_id()
    return {
        "sessionId": session_id,
        "profileId": profile_id,
        "rulesetVersion": "2026.09.1",
        "language": language
    }

def generate_presigned_upload(session_id: str, document_id: str, content_type: str, kms_key_arn: str, bucket: str) -> dict:
    """Generate a presigned POST URL for direct S3 upload.
    Scoped by key prefix, content-type, size, and KMS encryption."""
    s3_client = boto3.client('s3', region_name='ap-south-1')
    object_name = f"raw/{session_id}/{document_id}"
    
    conditions = [
        {"bucket": bucket},
        ["starts-with", "$key", f"raw/{session_id}/"],
        {"content-type": content_type},
        ["content-length-range", 1, 10 * 1024 * 1024],
        {"x-amz-server-side-encryption": "aws:kms"},
        {"x-amz-server-side-encryption-aws-kms-key-id": kms_key_arn}
    ]
    
    fields = {
        "content-type": content_type,
        "x-amz-server-side-encryption": "aws:kms",
        "x-amz-server-side-encryption-aws-kms-key-id": kms_key_arn
    }
    
    response = s3_client.generate_presigned_post(
        Bucket=bucket,
        Key=object_name,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600
    )
    
    return response
