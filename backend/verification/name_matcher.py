import re
from dataclasses import dataclass
from enum import Enum

class NameMatchResult(str, Enum):
    MATCH = "MATCH"
    MINOR_VARIATION = "MINOR_VARIATION"
    MISMATCH = "MISMATCH"

@dataclass
class NameComparisonResult:
    result: NameMatchResult
    rule_id: str
    normalized_a: str
    normalized_b: str
    details: str

HONORIFICS = {"SHRI", "SMT", "KUM", "MR", "MRS", "MS", "DR", "KUMARI", "LATE", "PROF"}

def jaro_winkler(s1: str, s2: str, p: float = 0.1, max_l: int = 4) -> float:
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    max_dist = (max(len1, len2) // 2) - 1
    
    match_count = 0
    hash_s1 = [0] * len1
    hash_s2 = [0] * len2
    
    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(len2, i + max_dist + 1)
        for j in range(start, end):
            if s1[i] == s2[j] and hash_s2[j] == 0:
                hash_s1[i] = 1
                hash_s2[j] = 1
                match_count += 1
                break
                
    if match_count == 0:
        return 0.0
        
    t = 0
    point = 0
    for i in range(len1):
        if hash_s1[i]:
            while hash_s2[point] == 0:
                point += 1
            if s1[i] != s2[point]:
                t += 1
            point += 1
    t /= 2
    
    match_count = float(match_count)
    jaro = (match_count / len1 + match_count / len2 + (match_count - t) / match_count) / 3.0
    
    l = 0
    weight = 0.1
    for i in range(min(len1, len2, max_l)):
        if s1[i] == s2[i]:
            l += 1
        else:
            break
            
    jw = jaro + (l * weight * (1 - jaro))
    return jw

def normalize(name: str) -> str:
    name = name.upper()
    name = re.sub(r'[^\w\s-]', '', name)
    tokens = name.split()
    tokens = [t for t in tokens if t not in HONORIFICS]
    return ' '.join(tokens)

def fold(token: str) -> str:
    t = token
    t = re.sub(r'A+', 'A', t)
    t = re.sub(r'E+', 'I', t)
    t = re.sub(r'O+', 'U', t)
    t = t.replace('V', 'W')
    t = t.replace('PH', 'F')
    t = re.sub(r'SH(?=[^AEIOU])', 'S', t)
    t = t.replace('KSH', 'X')
    t = t.replace('CHH', 'CH')
    if t.endswith('TH'):
        t = t[:-2] + 'T'
    if t.endswith('GH'):
        t = t[:-2] + 'G'
    t = re.sub(r'([^AEIOU])H(?=[^AEIOU]|$)', r'\1', t)
    if len(t) > 1:
        t = t[0] + t[1:].replace('Y', 'I')
    return t

def match_names(name_a: str, name_b: str, thresholds: dict | None = None) -> NameComparisonResult:
    """Match two names using the three-step Indic name matching algorithm.
    
    Step 1: Normalize (uppercase, strip honorifics, punctuation)
    Step 2: Transliteration fold (AA->A, V<->W, PH->F, etc.)
    Step 3: Token logic (exact, subset, order, Jaro-Winkler)
    """
    from collections import Counter
    
    thresh = thresholds or {'match': 0.94, 'minor': 0.87, 'surname': 0.90}
    norm_a = normalize(name_a)
    norm_b = normalize(name_b)
    
    # Original-order folded tokens (for subset/order checks)
    orig_tokens_a = [fold(t) for t in norm_a.split()]
    orig_tokens_b = [fold(t) for t in norm_b.split()]
    
    # Sorted folded tokens (for exact match and JW alignment)
    sorted_a = sorted(orig_tokens_a)
    sorted_b = sorted(orig_tokens_b)
    
    # NM-03: Same multiset, different order — check BEFORE sorted exact match
    # so we can distinguish "Borse Kunal" vs "Kunal Borse" as an order variation
    if Counter(orig_tokens_a) == Counter(orig_tokens_b) and orig_tokens_a != orig_tokens_b:
        return NameComparisonResult(NameMatchResult.MINOR_VARIATION, "NM-03", norm_a, norm_b,
                                   "Same tokens, different order")
    
    # NM-01: Exact match on folded tokens
    if sorted_a == sorted_b:
        return NameComparisonResult(NameMatchResult.MATCH, "NM-01", norm_a, norm_b,
                                   "Exact match on folded tokens")
    
    # NM-02: Proper subset with first AND last original-order tokens matching
    set_a, set_b = set(orig_tokens_a), set(orig_tokens_b)
    if set_a != set_b and (set_a.issubset(set_b) or set_b.issubset(set_a)):
        shorter = orig_tokens_a if len(orig_tokens_a) <= len(orig_tokens_b) else orig_tokens_b
        longer = orig_tokens_b if len(orig_tokens_a) <= len(orig_tokens_b) else orig_tokens_a
        # First token of shorter matches first token of longer,
        # AND last token of shorter matches last token of longer
        if (shorter and longer and
            shorter[0] == longer[0] and shorter[-1] == longer[-1]):
            return NameComparisonResult(NameMatchResult.MINOR_VARIATION, "NM-02", norm_a, norm_b,
                                       f"Subset match: '{norm_a}' vs '{norm_b}' with matching first/last tokens")
    
    # NM-04/NM-05/NM-06: Jaro-Winkler alignment on sorted tokens
    # Align by best-match scoring to handle different token counts
    longer_tokens = sorted_a if len(sorted_a) >= len(sorted_b) else sorted_b
    shorter_tokens = sorted_b if len(sorted_a) >= len(sorted_b) else sorted_a
    
    aligned_scores = []
    used = set()
    for t_s in shorter_tokens:
        best_score = 0.0
        best_idx = -1
        for idx, t_l in enumerate(longer_tokens):
            if idx in used:
                continue
            score = jaro_winkler(t_s, t_l)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx >= 0:
            used.add(best_idx)
        aligned_scores.append(best_score)
    
    if not aligned_scores:
        return NameComparisonResult(NameMatchResult.MISMATCH, "NM-06", norm_a, norm_b,
                                   "No tokens to compare")
    
    # Check surname (last token) specifically
    surname_score = jaro_winkler(orig_tokens_a[-1], orig_tokens_b[-1]) if orig_tokens_a and orig_tokens_b else 0.0
    
    if all(s >= thresh['match'] for s in aligned_scores):
        return NameComparisonResult(NameMatchResult.MATCH, "NM-04", norm_a, norm_b,
                                   "All tokens Jaro-Winkler >= match threshold")
    
    if (all(s >= thresh['minor'] for s in aligned_scores) and
        surname_score >= thresh['surname']):
        return NameComparisonResult(NameMatchResult.MINOR_VARIATION, "NM-05", norm_a, norm_b,
                                   "Tokens Jaro-Winkler in minor variation range")
    
    return NameComparisonResult(NameMatchResult.MISMATCH, "NM-06", norm_a, norm_b,
                                "Tokens failed Jaro-Winkler thresholds")
