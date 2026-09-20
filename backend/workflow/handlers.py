import json
import logging
import os
import secrets
import glob
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _log_event(handler_name: str, status: str, event: dict):
    logger.info(json.dumps({
        "handler": handler_name,
        "status": status,
        "session_id": event.get("sessionId", "unknown")
    }))

def ingest_gate_handler(event, context):
    _log_event("ingest_gate", "start", event)
    try:
        # Ingestion logic
        result = {"status": "SUCCESS", "step": "ingest_gate"}
        _log_event("ingest_gate", "success", event)
        return result
    except Exception as e:
        _log_event("ingest_gate", f"error: {str(e)}", event)
        raise

def extraction_handler(event, context):
    _log_event("extraction", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "extraction"}
        _log_event("extraction", "success", event)
        return result
    except Exception as e:
        _log_event("extraction", f"error: {str(e)}", event)
        raise

def classification_handler(event, context):
    _log_event("classification", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "classification"}
        _log_event("classification", "success", event)
        return result
    except Exception as e:
        _log_event("classification", f"error: {str(e)}", event)
        raise

def completeness_handler(event, context):
    _log_event("completeness", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "completeness"}
        _log_event("completeness", "success", event)
        return result
    except Exception as e:
        _log_event("completeness", f"error: {str(e)}", event)
        raise

def verification_handler(event, context):
    _log_event("verification", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "verification"}
        _log_event("verification", "success", event)
        return result
    except Exception as e:
        _log_event("verification", f"error: {str(e)}", event)
        raise

def explanation_handler(event, context):
    _log_event("explanation", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "explanation"}
        _log_event("explanation", "success", event)
        return result
    except Exception as e:
        _log_event("explanation", f"error: {str(e)}", event)
        raise

def persist_handler(event, context):
    _log_event("persist", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "persist"}
        _log_event("persist", "success", event)
        return result
    except Exception as e:
        _log_event("persist", f"error: {str(e)}", event)
        raise

def cleanup_handler(event, context):
    _log_event("cleanup", "start", event)
    try:
        result = {"status": "SUCCESS", "step": "cleanup"}
        _log_event("cleanup", "success", event)
        return result
    except Exception as e:
        _log_event("cleanup", f"error: {str(e)}", event)
        raise


# ============================================================
# API Gateway Handlers (called by API stack Lambdas)
# ============================================================

def _api_response(status_code: int, body: dict) -> dict:
    """Build API Gateway proxy response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(body)
    }


def list_profiles_handler(event, context):
    """GET /profiles — return available verification profiles."""
    try:
        # Look for profile JSON files bundled with the Lambda code
        profiles_dir = os.path.join(os.path.dirname(__file__), "..", "rules", "profiles")
        if not os.path.isdir(profiles_dir):
            profiles_dir = os.path.join(os.path.dirname(__file__), "..", "..", "rules", "profiles")
        if not os.path.isdir(profiles_dir):
            profiles_dir = "/var/task/rules/profiles"

        profiles = []
        if os.path.isdir(profiles_dir):
            for fp in sorted(glob.glob(os.path.join(profiles_dir, "*.json"))):
                with open(fp, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    profiles.append({
                        "profileId": profile.get("profileId", Path(fp).stem),
                        "name": profile.get("name", Path(fp).stem),
                        "version": profile.get("rulesetVersion", "unknown"),
                        "requiredDocuments": [d.get("type", d.get("expectedType", ""))
                                              for d in profile.get("requiredDocuments", [])]
                    })

        # Hardcoded fallback if no rule files found on disk
        if not profiles:
            profiles = [{
                "profileId": "post-matric-scholarship-v1",
                "name": "Post-Matric Scholarship",
                "version": "2026.09.1",
                "requiredDocuments": ["aadhaar", "marksheet", "income_certificate", "domicile"]
            }]

        return _api_response(200, {"profiles": profiles})
    except Exception as e:
        logger.error(f"list_profiles error: {e}")
        return _api_response(500, {"error": str(e)})


def create_session_handler(event, context):
    """POST /verifications — create a new verification session."""
    try:
        import boto3
        body = json.loads(event.get("body", "{}"))
        profile_id = body.get("profileId", "post-matric-scholarship-v1")

        session_id = secrets.token_urlsafe(16)
        now = datetime.now(timezone.utc).isoformat()

        table_name = os.environ.get("DOCVERIFY_TABLE", "")
        if table_name:
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(table_name)
            table.put_item(Item={
                "PK": f"SESSION#{session_id}",
                "SK": "META",
                "sessionId": session_id,
                "profileId": profile_id,
                "status": "CREATED",
                "createdAt": now,
                "verificationVersion": 1,
            })

        return _api_response(201, {
            "sessionId": session_id,
            "profileId": profile_id,
            "status": "CREATED",
            "createdAt": now,
        })
    except Exception as e:
        logger.error(f"create_session error: {e}")
        return _api_response(500, {"error": str(e)})


def get_status_handler(event, context):
    """GET /verifications/{id} — return session status and results."""
    try:
        import boto3
        session_id = event.get("pathParameters", {}).get("id", "")
        if not session_id:
            return _api_response(400, {"error": "Missing session ID"})

        table_name = os.environ.get("DOCVERIFY_TABLE", "")
        if not table_name:
            return _api_response(500, {"error": "Table not configured"})

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        resp = table.get_item(Key={"PK": f"SESSION#{session_id}", "SK": "META"})
        item = resp.get("Item")

        if not item:
            return _api_response(404, {"error": "Session not found"})

        return _api_response(200, {
            "sessionId": item.get("sessionId"),
            "profileId": item.get("profileId"),
            "status": item.get("status", "UNKNOWN"),
            "createdAt": item.get("createdAt"),
            "readinessStatus": item.get("readinessStatus"),
            "findings": json.loads(item["findings"]) if "findings" in item else [],
        })
    except Exception as e:
        logger.error(f"get_status error: {e}")
        return _api_response(500, {"error": str(e)})


def upload_handler(event, context):
    """POST /verifications/{id}/uploads — generate presigned S3 POST URL."""
    try:
        import boto3
        session_id = event.get("pathParameters", {}).get("id", "")
        body = json.loads(event.get("body", "{}"))
        filename = body.get("filename", "document.pdf")
        content_type = body.get("contentType", "application/pdf")

        if not session_id:
            return _api_response(400, {"error": "Missing session ID"})

        bucket = os.environ.get("RAW_BUCKET", "")
        if not bucket:
            return _api_response(500, {"error": "Bucket not configured"})

        s3_client = boto3.client("s3")
        key = f"{session_id}/{filename}"

        presigned = s3_client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, 10 * 1024 * 1024],  # 1B - 10MB
            ],
            ExpiresIn=300  # 5 minutes
        )

        return _api_response(200, {
            "uploadUrl": presigned["url"],
            "fields": presigned["fields"],
            "key": key,
        })
    except Exception as e:
        logger.error(f"upload error: {e}")
        return _api_response(500, {"error": str(e)})


def run_verification_handler(event, context):
    """POST /verifications/{id}/run — trigger the Step Functions pipeline."""
    try:
        import boto3
        session_id = event.get("pathParameters", {}).get("id", "")
        if not session_id:
            return _api_response(400, {"error": "Missing session ID"})

        state_machine_arn = os.environ.get("STATE_MACHINE_ARN", "")
        if not state_machine_arn:
            return _api_response(500, {"error": "State machine not configured"})

        sfn_client = boto3.client("stepfunctions")
        execution = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"verify-{session_id}-{int(datetime.now(timezone.utc).timestamp())}",
            input=json.dumps({"sessionId": session_id})
        )

        return _api_response(202, {
            "sessionId": session_id,
            "executionArn": execution["executionArn"],
            "status": "RUNNING",
        })
    except Exception as e:
        logger.error(f"run_verification error: {e}")
        return _api_response(500, {"error": str(e)})
