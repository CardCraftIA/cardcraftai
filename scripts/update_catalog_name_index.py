"""Explicit maintenance command: python scripts/update_catalog_name_index.py --language en.
Never imported or invoked by the app. Fetches brief cards only, with pagination.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import requests
from catalog_search import IndexUnavailable, representative_image
from search_utils import normalize_search

PAGE_SIZE = 1000
MAX_PAGES = 200


def fetch_index(provider='tcgdex', language='en', get=None):
    if provider != 'tcgdex' or not re.fullmatch(r'[a-z]{2}(?:-[a-z]{2})?', language):
        raise IndexUnavailable('Unsupported index source')
    get = get or requests.get
    records = {}
    try:
        for page in range(1, MAX_PAGES + 1):
            response = get(f'https://api.tcgdex.net/v2/{language}/cards', params={
                'pagination:page': page, 'pagination:itemsPerPage': PAGE_SIZE,
                'sort:field': 'id', 'sort:order': 'ASC',
            }, timeout=15)
            response.raise_for_status()
            batch = response.json()
            if not isinstance(batch, list):
                raise IndexUnavailable('Invalid index response')
            if not batch:
                if not records:
                    raise IndexUnavailable('Empty index')
                return list(records.values())
            before = len(records)
            for card in batch:
                if not isinstance(card, dict) or not isinstance(card.get('id'), str) or not card['id'] or not isinstance(card.get('name'), str) or not card['name'].strip():
                    raise IndexUnavailable('Invalid index entry')
                records[card['id']] = {key: str(card.get(key) or '') for key in ('id', 'localId', 'name', 'image')}
            if len(records) == before:
                raise IndexUnavailable('Pagination did not advance')
            # Continue until an empty page, even if the server caps page size.
        raise IndexUnavailable('Index page limit reached')
    except (requests.RequestException, ValueError) as error:
        raise IndexUnavailable('Index temporarily unavailable') from error



def unique_names(records):
    names = {}
    for card in records:
        # Keep accents and meaningful symbols distinct when deduplicating.
        key = normalize_search(card['name'], fold_accents=False)
        if key not in names or (not representative_image(names[key]) and representative_image(card)):
            names[key] = card
    return {card['name']: card for card in names.values()}



def build_snapshot(records, provider='tcgdex', language='en'):
    entries = [dict(display_name=name, normalized_name=normalize_search(name),
                    representative_id=card['id'], representative_local_id=card['localId'],
                    representative_image=representative_image(card))
               for name, card in unique_names(records).items()]
    entries.sort(key=lambda entry: (entry['normalized_name'], entry['display_name']))
    return dict(provider=provider, language=language, schema_version=1,
                generated_at=datetime.now(timezone.utc).isoformat(), entries=entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', default='en')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    records = fetch_index('tcgdex', args.language)
    snapshot = build_snapshot(records, language=args.language)
    output = args.output or Path(__file__).resolve().parents[1] / 'data' / f'catalog_name_index_tcgdex_{args.language}.json'
    payload = json.dumps(snapshot, ensure_ascii=False, separators=(',', ':')) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.json.tmp')
    temporary.write_text(payload, encoding='utf-8', newline='\n')
    temporary.replace(output)
    print(f"Cards: {len(records)}; unique names: {len(snapshot['entries'])}; bytes: {output.stat().st_size}")


if __name__ == '__main__':
    main()
