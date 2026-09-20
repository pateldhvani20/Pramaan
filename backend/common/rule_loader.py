"""
Rule pack loading and caching utilities.
Loads JSON rules definitions from the filesystem.
"""
import json
import os
from pathlib import Path
from functools import lru_cache
from typing import Any

def _get_rules_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / 'rules',
        Path('/var/task/rules'),
        Path(__file__).resolve().parent.parent.parent / 'rules',
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]

RULES_DIR = _get_rules_dir()

@lru_cache(maxsize=16)
def load_profile(profile_id: str) -> dict[str, Any]:
    """Load an application profile rule pack."""
    profiles_dir = RULES_DIR / 'profiles'
    for f in profiles_dir.glob('*.json'):
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            if data.get('profileId') == profile_id:
                return data
    raise ValueError(f"Profile not found: {profile_id}")

@lru_cache(maxsize=32)
def load_document_rules(document_type: str) -> dict[str, Any]:
    """Load document-type specific rules."""
    doc_file = RULES_DIR / 'documents' / f'{document_type}.json'
    if not doc_file.exists():
        raise ValueError(f"Document rules not found: {document_type}")
    with open(doc_file, 'r', encoding='utf-8') as fh:
        return json.load(fh)

def get_ruleset_version(profile_id: str) -> str:
    """Get the rulesetVersion for a profile."""
    profile = load_profile(profile_id)
    return profile.get('rulesetVersion', '2026.09.1')

def list_available_profiles() -> list[dict[str, str]]:
    """List all available application profiles."""
    profiles = []
    profiles_dir = RULES_DIR / 'profiles'
    if not profiles_dir.exists():
        return profiles
    for f in profiles_dir.glob('*.json'):
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            profiles.append({
                'profileId': data['profileId'],
                'displayName': data['displayName'],
                'rulesetVersion': data.get('rulesetVersion', ''),
                'requiredDocCount': len([d for d in data.get('requiredDocuments', []) if d.get('required', False)]),
            })
    return profiles
