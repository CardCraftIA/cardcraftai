"""Shared local search primitives; never used to confirm catalog identity or charge credits."""
import unicodedata
from difflib import SequenceMatcher

FUZZY_CUTOFF = 0.78


def normalize_search(value, fold_accents=True):
    text = unicodedata.normalize('NFKC', str(value or '')).casefold()
    if fold_accents:
        parts, latin = [], False
        for char in unicodedata.normalize('NFD', text):
            if not unicodedata.combining(char):
                latin = 'LATIN' in unicodedata.name(char, '')
            if not (latin and unicodedata.combining(char)):
                parts.append(char)
        text = unicodedata.normalize('NFC', ''.join(parts))
    text = ''.join(' ' if unicodedata.category(c).startswith('P') and c != '/' else c for c in text)
    return ' '.join(text.split())


SEARCH_FIELDS = ('card_name', 'set_name', 'card_number', 'condition', 'language', 'variant')


def fuzzy_similarity(needle, candidate):
    """Compare normalized names while preserving gender identity symbols."""
    if {c for c in needle if c in '♀♂'} != {c for c in candidate if c in '♀♂'}:
        return 0.0
    return SequenceMatcher(None, needle, candidate, autojunk=False).ratio()


def rank_entries(query, entries, limit=5):
    needle = normalize_search(query)
    if len(needle) < 3:
        return []
    candidates = []
    for entry in entries:
        name = entry['display_name']
        value = entry['normalized_name']
        if not value:
            continue
        if value == needle:
            priority, score = 0, 1.0
        elif value.startswith(needle):
            priority, score = 1, len(needle) / len(value)
        elif needle in value:
            priority, score = 2, len(needle) / len(value)
        else:
            score = fuzzy_similarity(needle, value)
            if score < FUZZY_CUTOFF:
                continue
            priority = 3
        # Extra edition/owner tokens should not outrank a close base name.
        extra_tokens = max(0, len(value.split()) - len(needle.split()))
        adjusted_score = score - (0.08 * extra_tokens if priority == 3 else 0)
        candidates.append((priority, -adjusted_score, name, entry))
    return [entry for _, _, _, entry in sorted(candidates, key=lambda item: item[:3])[:max(0, min(limit, 5))]]


def rank_names(query, names, limit=5):
    entries = [dict(display_name=name, normalized_name=normalize_search(name)) for name in names]
    return [entry['display_name'] for entry in rank_entries(query, entries, limit)]


def search_collection(items, query):
    """Exact field matches precede partial matches; never return fuzzy results silently."""
    needle = normalize_search(query)
    if not needle:
        return list(items)
    ranked = []
    for item in items:
        fields = [normalize_search(item.get(field, '')) for field in SEARCH_FIELDS]
        if needle in fields:
            ranked.append((0, item))
        elif any(needle in value for value in fields) or needle in ' '.join(fields):
            # A supplied denominator must match the complete number, not its tail.
            if '/' in needle and any(char.isdigit() for char in needle):
                continue
            ranked.append((1, item))
    return [item for _, item in sorted(ranked, key=lambda pair: pair[0])]


def suggest_collection_names(items, query):
    """At most five distinct saved names from the already filtered private records."""
    needle = normalize_search(query)
    if len(needle) < 3 or search_collection(items, query):
        return []
    candidates = {}
    for item in items:
        name = item.get('card_name', '')
        normalized = normalize_search(name)
        if not normalized:
            continue
        score = fuzzy_similarity(needle, normalized)
        if score >= FUZZY_CUTOFF and normalized not in candidates:
            candidates[normalized] = (score, name)
    return [name for _, name in sorted(candidates.values(), key=lambda pair: (-pair[0], pair[1]))[:5]]
