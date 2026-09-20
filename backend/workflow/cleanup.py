import boto3
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CleanupResult:
    success: bool
    failed_keys: list[str]

def cleanup_raw_documents(session_id: str, document_keys: list[str], bucket: str) -> CleanupResult:
    """Delete raw documents and VERIFY deletion.
    1. DeleteObjects on all raw keys
    2. HeadObject each one, expecting 404
    3. Emit CleanupFailures metric if any survive
    """
    s3_client = boto3.client('s3', region_name='ap-south-1')
    cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
    
    objects = [{'Key': key} for key in document_keys]
    
    if not objects:
        return CleanupResult(True, [])
        
    s3_client.delete_objects(
        Bucket=bucket,
        Delete={'Objects': objects, 'Quiet': True}
    )
    
    failed_keys = []
    for key in document_keys:
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
            # If we succeed, it means the object STILL exists
            failed_keys.append(key)
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                pass # expected
            else:
                failed_keys.append(key)
                
    if failed_keys:
        cloudwatch.put_metric_data(
            Namespace='DocVerify',
            MetricData=[
                {
                    'MetricName': 'CleanupFailures',
                    'Value': len(failed_keys),
                    'Unit': 'Count'
                }
            ]
        )
        logger.error(f"Failed to cleanup keys: {failed_keys}")
        return CleanupResult(False, failed_keys)
        
    return CleanupResult(True, [])
