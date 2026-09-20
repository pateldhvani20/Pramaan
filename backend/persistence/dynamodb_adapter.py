import os
import boto3
from typing import Any

TABLE_NAME = os.environ.get('DOCVERIFY_TABLE', 'docverify-state')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

def save_session(session: Any) -> None:
    """Save verification session. PK=VER#<sessionId>, SK=META"""
    table = dynamodb.Table(TABLE_NAME)
    item = {
        'PK': f"VER#{session.session_id}",
        'SK': 'META',
        **session.__dict__
    }
    table.put_item(Item=item)

def save_document(doc: Any) -> None:
    """Save document record. PK=VER#<sessionId>, SK=DOC#<docId>"""
    table = dynamodb.Table(TABLE_NAME)
    item = {
        'PK': f"VER#{doc.session_id}",
        'SK': f"DOC#{doc.document_id}",
        **doc.__dict__
    }
    table.put_item(Item=item)

def save_findings(session_id: str, findings: list[Any]) -> None:
    """Batch save findings. PK=VER#<sessionId>, SK=FND#<findingId>"""
    table = dynamodb.Table(TABLE_NAME)
    with table.batch_writer() as batch:
        for f in findings:
            item = {
                'PK': f"VER#{session_id}",
                'SK': f"FND#{f.finding_id}",
                **f.__dict__
            }
            batch.put_item(Item=item)

def save_result(result: Any) -> None:
    """Save with conditional write to prevent stale overwrites.
    ConditionExpression: attribute_not_exists(uploadedAt) OR uploadedAt <= :ts"""
    table = dynamodb.Table(TABLE_NAME)
    item = {
        'PK': f"VER#{result.session_id}",
        'SK': 'RESULT',
        **result.__dict__
    }
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(uploadedAt) OR uploadedAt <= :ts",
            ExpressionAttributeValues={":ts": result.uploaded_at}
        )
    except Exception as e:
        print(f"Condition check failed: {e}")

def get_verification(session_id: str) -> dict:
    """Query all items for a session in one call."""
    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": f"VER#{session_id}"}
    )
    return {"items": response.get('Items', [])}
