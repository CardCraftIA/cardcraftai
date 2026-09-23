"""Local public name snapshot. No catalog requests occur in the suggestion path."""
import json
import re
from pathlib import Path

import streamlit as st
from search_utils import normalize_search, rank_entries
from security_utils import safe_public_image

INDEX_TTL = 24 * 60 * 60
DATA_DIRECTORY = Path(__file__).resolve().parent / 'data'


class IndexUnavailable(RuntimeError):
    pass


def representative_image(card):
    url = card.get('image', '').rstrip('/')
    if safe_public_image(url, ('assets.tcgdex.net',)):
        return url + '/low.webp'
    return ''


def read_snapshot(path, provider='tcgdex', language='en'):
    try:
        snapshot = json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1 or snapshot.get('provider') != provider or snapshot.get('language') != language or not isinstance(snapshot.get('generated_at'), str):
            raise ValueError('Invalid metadata')
        entries = snapshot.get('entries')
        if not isinstance(entries, list) or not entries:
            raise ValueError('Empty snapshot')
        fields = ('display_name', 'normalized_name', 'representative_id', 'representative_local_id', 'representative_image')
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict) or any(not isinstance(entry.get(key), str) for key in fields):
                raise ValueError('Invalid entry')
            if not all(entry[key].strip() for key in fields[:3]) or entry['display_name'] in seen:
                raise ValueError('Invalid name')
            if entry['normalized_name'] != normalize_search(entry['display_name']):
                raise ValueError('Invalid normalized name')
            seen.add(entry['display_name'])
            image = entry['representative_image']
            if image and not safe_public_image(image, ('assets.tcgdex.net',)):
                raise ValueError('Invalid image source')
        return entries
    except (OSError, ValueError, TypeError) as error:
        raise IndexUnavailable('Local snapshot unavailable') from error


@st.cache_data(ttl=INDEX_TTL, max_entries=16, show_spinner=False)
def _cached_snapshot(path, modified_ns, size, provider, language):
    # File signature invalidates the public cache when the snapshot is replaced.
    return read_snapshot(path, provider, language)


def load_name_index(provider='tcgdex', language='en'):
    if provider != 'tcgdex' or not re.fullmatch(r'[a-z]{2}(?:-[a-z]{2})?', language):
        raise IndexUnavailable('Unsupported index source')
    path = DATA_DIRECTORY / f'catalog_name_index_{provider}_{language}.json'
    try:
        stat = path.stat()
    except OSError as error:
        raise IndexUnavailable('Local snapshot unavailable') from error
    return _cached_snapshot(str(path), stat.st_mtime_ns, stat.st_size, provider, language)


def render_suggestions(st, query, translate, on_choose, provider='tcgdex', language='en'):
    normalized_query = normalize_search(query)
    if len(normalized_query) < 3:
        return
    try:
        entries = load_name_index(provider, language)
    except IndexUnavailable:
        st.caption(translate('search_suggestions_unavailable'))
        return
    if any(entry['normalized_name'] == normalized_query for entry in entries):
        return
    suggestions = rank_entries(query, entries)
    names = {entry['display_name']: entry for entry in suggestions}
    if not suggestions:
        return
    st.caption(translate('search_did_you_mean'))
    for column, name in zip(st.columns(len(suggestions)), names):
        with column:
            image = names[name]['representative_image']
            if image:
                st.image(image, width=80)
            else:
                st.caption(translate('search_image_unavailable'))
            st.button(name, key=f'catalog_suggest:{provider}:{language}:{names[name]["representative_id"]}',
                      on_click=on_choose, args=(name,))
    st.caption(translate('search_representative_image'))
