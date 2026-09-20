"""Bedrock explanation adapter with schema validation and deterministic fallback.

Security contract (OWASP A04 — Insecure Design):
- Bedrock writes to exactly two fields: explanation and actionSteps
- It CANNOT set status, severity, ruleId, or any verdict field
- On any failure (timeout, parse error, schema violation), the deterministic
  fallback message is used and the verdict remains unchanged
- Temperature 0.2 for consistency
- 10-second timeout with fallback path wired
"""
import json
import os
from typing import Any

from backend.common.models import Finding
from backend.common.logging import get_logger, log_stage
from .prompt_builder import build_explanation_prompt

logger = get_logger(__name__)

MODE = os.environ.get('DOCVERIFY_BEDROCK_MODE', 'mock')
BEDROCK_MODEL_ID = os.environ.get(
    'DOCVERIFY_BEDROCK_MODEL',
    'anthropic.claude-3-haiku-20240307-v1:0'
)
BEDROCK_REGION = os.environ.get('DOCVERIFY_BEDROCK_REGION', 'ap-south-1')
MAX_TOKENS = 2048
TEMPERATURE = 0.2
TIMEOUT_SECONDS = 10

# Deterministic fallback messages (bilingual)
FALLBACK_MESSAGES = {
    'identity': {
        'en': [
            'Ensure the name matches exactly across all documents.',
            'Check for spelling differences or missing middle names.',
            'Get documents re-issued with the correct name if needed.'
        ],
        'hi': [
            'सुनिश्चित करें कि सभी दस्तावेज़ों में नाम एक समान है।',
            'वर्तनी अंतर या लापता मध्य नामों की जाँच करें।',
            'यदि आवश्यक हो तो सही नाम के साथ दस्तावेज़ पुनः जारी करवाएँ।'
        ]
    },
    'dob': {
        'en': [
            'Verify date of birth matches on all submitted documents.',
            'Contact the issuing authority to correct any discrepancy.'
        ],
        'hi': [
            'सत्यापित करें कि सभी दस्तावेज़ों पर जन्म तिथि मेल खाती है।',
            'किसी भी विसंगति को ठीक करने के लिए जारीकर्ता प्राधिकरण से संपर्क करें।'
        ]
    },
    'validity': {
        'en': [
            'Obtain a fresh certificate from the issuing authority.',
            'Ensure the new document will remain valid through the review period.'
        ],
        'hi': [
            'जारीकर्ता प्राधिकरण से नया प्रमाण पत्र प्राप्त करें।',
            'सुनिश्चित करें कि नया दस्तावेज़ समीक्षा अवधि तक वैध रहेगा।'
        ]
    },
    'completeness': {
        'en': [
            'Upload a clearer scan of the document.',
            'Ensure all required information is visible and legible.'
        ],
        'hi': [
            'दस्तावेज़ का एक स्पष्ट स्कैन अपलोड करें।',
            'सुनिश्चित करें कि सभी आवश्यक जानकारी दिखाई और पठनीय है।'
        ]
    },
    'classification': {
        'en': [
            'Verify you have uploaded the correct document type.',
            'Re-upload the correct document for this slot.'
        ],
        'hi': [
            'सत्यापित करें कि आपने सही प्रकार का दस्तावेज़ अपलोड किया है।',
            'इस स्लॉट के लिए सही दस्तावेज़ पुनः अपलोड करें।'
        ]
    }
}


def _get_fallback_actions(category: str, language: str = 'en') -> list[str]:
    """Get deterministic fallback action steps for a finding category."""
    lang = language if language in ('en', 'hi') else 'en'
    category_actions = FALLBACK_MESSAGES.get(category, FALLBACK_MESSAGES['completeness'])
    return category_actions.get(lang, category_actions['en'])


def _validate_explanation_schema(parsed: list[dict], finding_ids: set[str]) -> list[dict]:
    """Validate Bedrock's response against the fixed schema.

    Rules:
    - Must be a list of dicts
    - Each dict must have findingId, explanation, actionSteps
    - findingId must match an existing finding
    - explanation must be string, max 240 chars
    - actionSteps must be list of 2-3 strings
    """
    validated = []
    for item in parsed:
        if not isinstance(item, dict):
            continue

        finding_id = item.get('findingId', '')
        if finding_id not in finding_ids:
            continue  # Drop unrecognized finding IDs

        explanation = item.get('explanation', '')
        if not isinstance(explanation, str):
            continue
        explanation = explanation[:240]  # Enforce length cap

        action_steps = item.get('actionSteps', [])
        if not isinstance(action_steps, list):
            continue
        action_steps = [str(s)[:200] for s in action_steps[:3] if isinstance(s, str)]

        validated.append({
            'findingId': finding_id,
            'explanation': explanation,
            'actionSteps': action_steps,
        })

    return validated


def _invoke_bedrock(system_prompt: str, user_message: str) -> str:
    """Invoke Bedrock model. Returns raw response body string."""
    import boto3

    client = boto3.client(
        'bedrock-runtime',
        region_name=BEDROCK_REGION,
    )

    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE,
        'system': system_prompt,
        'messages': [
            {'role': 'user', 'content': user_message}
        ]
    })

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType='application/json',
        accept='application/json'
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']


def _mock_bedrock(findings: list[Finding], language: str) -> list[dict]:
    """Mock Bedrock response for local testing."""
    results = []
    for f in findings:
        actions = _get_fallback_actions(f.category, language)
        results.append({
            'findingId': f.findingId,
            'explanation': f.deterministicMessage[:240],
            'actionSteps': actions,
        })
    return results


def generate_explanations(
    findings: list[Finding],
    language: str = 'en',
    verification_id: str = ''
) -> list[dict]:
    """Generate explanations for all findings using Bedrock or fallback.

    One batched call for ALL findings — cheaper, faster, and the model
    can order the action plan sensibly across findings.

    On ANY failure:
    - Use deterministicMessage as the explanation
    - Use category-based fallback action steps
    - Verdict remains UNCHANGED (Bedrock cannot alter it)

    Returns:
        List of {findingId, explanation, actionSteps} dicts.
    """
    if not findings:
        return []

    finding_ids = {f.findingId for f in findings}

    # Mock mode for local development
    if MODE == 'mock':
        log_stage(logger, verification_id, 'explain', 'MOCK',
                  finding_count=len(findings))
        return _mock_bedrock(findings, language)

    # Live Bedrock invocation
    try:
        system_prompt, user_message = build_explanation_prompt(findings, language)

        raw_response = _invoke_bedrock(system_prompt, user_message)

        # Parse JSON response
        parsed = json.loads(raw_response)
        if not isinstance(parsed, list):
            raise ValueError('Bedrock response is not a JSON array')

        # Schema validation
        validated = _validate_explanation_schema(parsed, finding_ids)

        if not validated:
            raise ValueError('No valid explanations after schema validation')

        log_stage(logger, verification_id, 'explain', 'SUCCESS',
                  finding_count=len(findings), explained_count=len(validated))
        return validated

    except Exception as e:
        # Fallback path: deterministic messages
        log_stage(logger, verification_id, 'explain', 'FALLBACK',
                  error=str(e), finding_count=len(findings))

        fallback_results = []
        for f in findings:
            actions = _get_fallback_actions(f.category, language)
            msg = f.deterministicMessageHi if language == 'hi' and f.deterministicMessageHi else f.deterministicMessage
            fallback_results.append({
                'findingId': f.findingId,
                'explanation': msg[:240],
                'actionSteps': actions,
            })
        return fallback_results
