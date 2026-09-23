"""Private collection search only; no catalog ranking or identification logic."""
import unicodedata
from difflib import SequenceMatcher

SEARCH_FIELDS = ('card_name', 'set_name', 'card_number', 'condition', 'language', 'variant')
FUZZY_CUTOFF = 0.78


def normalize_search(value, fold_accents=True):
    text = unicodedata.normalize('NFKC', str(value or '')).casefold()
    if fold_accents:
        parts = []
        latin = False
        for char in unicodedata.normalize('NFD', text):
            if not unicodedata.combining(char):
                latin = 'LATIN' in unicodedata.name(char, '')
            if not (latin and unicodedata.combining(char)):
                parts.append(char)
        text = unicodedata.normalize('NFC', ''.join(parts))
    text = ''.join(' ' if unicodedata.category(char).startswith('P') and char != '/' else char
                   for char in text)
    return ' '.join(text.split())


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
        if {c for c in needle if c in '♀♂'} != {c for c in normalized if c in '♀♂'}:
            continue
        score = SequenceMatcher(None, needle, normalized, autojunk=False).ratio()
        if score >= FUZZY_CUTOFF and normalized not in candidates:
            candidates[normalized] = (score, name)
    return [name for _, name in sorted(candidates.values(), key=lambda pair: (-pair[0], pair[1]))[:5]]
