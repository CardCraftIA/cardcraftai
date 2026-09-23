"""Search suggestions only. Does not participate in catalog confirmation."""
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
            if {c for c in needle if c in '♀♂'} != {c for c in value if c in '♀♂'}:
                continue
            score = SequenceMatcher(None, needle, value, autojunk=False).ratio()
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
