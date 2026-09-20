import json
import logging

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
