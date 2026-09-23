import ast
import json
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest
from catalog_search import (IndexUnavailable, load_name_index, read_snapshot,
                            _cached_snapshot, representative_image)
from scripts.update_catalog_name_index import fetch_index, unique_names, build_snapshot
from search_utils import normalize_search, rank_names, rank_entries


def card(name='Pikachu', identity='base-1', image=''):
    return dict(id=identity, localId='1', name=name, image=image)


def response(data):
    result = Mock()
    result.json.return_value = data
    return result


class CatalogSearchTests(unittest.TestCase):
    def test_pagination_projects_only_brief_fields(self):
        get = Mock(side_effect=[response([dict(card(), secret='not part of index')]),
                                response([card('Pichu', 'base-2')]), response([])])
        result = fetch_index(language='pt-br', get=get)
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result[0]), {'id', 'localId', 'name', 'image'})
        self.assertEqual([call.kwargs['params']['pagination:page'] for call in get.call_args_list], [1, 2, 3])
        self.assertTrue(all(call.args[0] == 'https://api.tcgdex.net/v2/pt-br/cards' for call in get.call_args_list))

    def test_repeated_page_rejected(self):
        with self.assertRaises(IndexUnavailable):
            fetch_index(get=Mock(return_value=response([card()])))

    def test_invalid_or_empty_payload_rejected(self):
        for payload in ([], {}, [None], [{'id': 'x'}]):
            with self.subTest(payload=payload), self.assertRaises(IndexUnavailable):
                fetch_index(get=Mock(return_value=response(payload)))

    def test_partial_failure_does_not_return_partial_index(self):
        with self.assertRaises(IndexUnavailable):
            fetch_index(get=Mock(side_effect=[response([card()]), requests.Timeout()]))

    def test_malformed_json_and_http_failure(self):
        bad_json = response(None)
        bad_json.json.side_effect = ValueError()
        http_error = response(None)
        http_error.raise_for_status.side_effect = requests.HTTPError()
        for result in (bad_json, http_error):
            with self.assertRaises(IndexUnavailable):
                fetch_index(get=Mock(return_value=result))

    def test_invalid_source_does_not_call_network(self):
        get = Mock()
        for provider, language in (('other', 'en'), ('tcgdex', '../secrets')):
            with self.assertRaises(IndexUnavailable):
                fetch_index(provider, language, get)
        get.assert_not_called()

    def test_local_snapshot_works_without_network(self):
        with patch('requests.sessions.Session.request', side_effect=requests.ConnectionError()) as network:
            entries = load_name_index()
            self.assertGreater(len(entries), 4000)
            for query in ('Picachu', 'Pikacu', 'Pikatchu'):
                self.assertEqual(rank_entries(query, entries)[0]['display_name'], 'Pikachu')
            network.assert_not_called()

    def test_missing_snapshot(self):
        with TemporaryDirectory() as directory, patch('catalog_search.DATA_DIRECTORY', Path(directory)):
            with self.assertRaises(IndexUnavailable):
                load_name_index()

    def test_invalid_snapshot(self):
        valid = build_snapshot([card()])
        invalid = [None, {}, {**valid, 'schema_version': 99}, {**valid, 'language': 'fr'},
                   {**valid, 'entries': []}, {**valid, 'entries': [{}]}]
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'index.json'
            for payload in invalid:
                path.write_text(json.dumps(payload), encoding='utf-8')
                with self.subTest(payload=payload), self.assertRaises(IndexUnavailable):
                    read_snapshot(path)
            path.write_text('{broken', encoding='utf-8')
            with self.assertRaises(IndexUnavailable):
                read_snapshot(path)

    def test_cache_reuses_local_parse_and_invalidates_replacement(self):
        _cached_snapshot.clear()
        with TemporaryDirectory() as directory, patch('catalog_search.DATA_DIRECTORY', Path(directory)):
            path = Path(directory) / 'catalog_name_index_tcgdex_en.json'
            path.write_text(json.dumps(build_snapshot([card()])), encoding='utf-8')
            with patch('catalog_search.read_snapshot', wraps=read_snapshot) as read:
                load_name_index()
                load_name_index()
                self.assertEqual(read.call_count, 1)
                path.write_text(json.dumps(build_snapshot([card('Raichu')])) + ' ', encoding='utf-8')
                self.assertEqual(load_name_index()[0]['display_name'], 'Raichu')
                self.assertEqual(read.call_count, 2)
                with self.assertRaises(IndexUnavailable):
                    load_name_index(language='fr')
        _cached_snapshot.clear()

    def test_snapshot_has_only_compact_normalized_fields(self):
        snapshot = build_snapshot([card(), card('PIKACHU', 'x2')])
        self.assertEqual(len(snapshot['entries']), 1)
        self.assertEqual(set(snapshot['entries'][0]), {'display_name', 'normalized_name',
                         'representative_id', 'representative_local_id', 'representative_image'})
        self.assertEqual(snapshot['entries'][0]['normalized_name'], 'pikachu')

    def test_base_name_priority_and_pre_normalized_ranking(self):
        entries = build_snapshot([card(name, str(i)) for i, name in enumerate(
            ['Pikachu V', 'Pikachu δ', "___________'s Pikachu", 'Pikachu', 'Pichu'])])['entries']
        with patch('search_utils.normalize_search', wraps=normalize_search) as normalize:
            self.assertEqual(rank_entries('Pikacu', entries)[0]['display_name'], 'Pikachu')
            self.assertEqual(normalize.call_count, 1)

    def test_name_dedup_and_representative_image(self):
        records = [card(), card('PIKACHU', 'base-2', 'https://assets.tcgdex.net/en/base/2'),
                   card('Nidoran♀', 'n1'), card('Nidoran♂', 'n2')]
        names = unique_names(records)
        self.assertEqual(len(names), 3)
        self.assertTrue(representative_image(names['PIKACHU']).endswith('/low.webp'))
        self.assertEqual(representative_image(card(image='https://evil.test/image')), '')

    def test_typo_examples(self):
        for query in ('Picachu', 'Pikacu', 'Pikatchu'):
            self.assertEqual(rank_names(query, ['Pikachu', 'Pichu', 'Raichu'])[0], 'Pikachu')

    def test_normalization_and_identity_symbols(self):
        self.assertEqual(normalize_search('  ＰＯＫÉＭＯＮ--  V '), 'pokemon v')
        self.assertNotEqual(normalize_search('Nidoran♀'), normalize_search('Nidoran♂'))
        self.assertNotEqual(normalize_search('ガ'), normalize_search('カ'))
        self.assertEqual(rank_names('Nidoran♀', ['Nidoran♂']), [])

    def test_ranking_limit_and_cutoff(self):
        result = rank_names('Pikachu', ['Flying Pikachu', 'Pikachu V', 'Pikachu', 'Pikacu'])
        self.assertEqual(result, ['Pikachu', 'Pikachu V', 'Flying Pikachu', 'Pikacu'])
        self.assertLessEqual(len(rank_names('Pika', ['Pikachu ' + str(i) for i in range(10)])), 5)
        self.assertEqual(rank_names('zzzzzz', ['Pikachu']), [])
        self.assertEqual(rank_names('pi', ['Pikachu']), [])


class CatalogSearchUITests(unittest.TestCase):
    def app(self, fail_index=False):
        source = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
        functions = '\n\n'.join(ast.get_source_segment(source, node) for node in ast.parse(source).body
                                if isinstance(node, ast.FunctionDef) and node.name in
                                ('limpar_selecao_catalogo_nome', 'escolher_sugestao_catalogo_nome'))
        start = source.index('elif pagina == "search":') + len('elif pagina == "search":')
        end = source.index('    st.subheader(\n        t("specialized_analysis", idioma)', start)
        # Exercise the actual search-page code, without authentication, secrets or AI.
        setup = '''
import streamlit as st
from catalog_search import render_suggestions
idioma = 'English'
def t(key, *args, **kwargs): return key
def buscar_cartas_catalogo_pokemon(**kwargs):
    st.session_state['calls'] = st.session_state.get('calls', []) + [kwargs]
    if st.session_state.get('fail_catalog'): raise RuntimeError('offline')
    return []
def _status_http_catalogo_erro(error): return None
st.session_state.setdefault('catalogo_resultados_nome', [])
st.session_state.setdefault('catalogo_consulta_nome', None)
st.session_state.setdefault('creditos', 5)
'''
        self.loader = patch('catalog_search.load_name_index', side_effect=IndexUnavailable() if fail_index else None,
                            return_value=build_snapshot([card(), card('Pichu', 'p2')])['entries'])
        self.loader.start()
        self.addCleanup(self.loader.stop)
        return AppTest.from_string(textwrap.dedent(setup) + functions + '\n' + textwrap.dedent(source[start:end]), default_timeout=10).run()

    def test_click_changes_name_but_search_stays_explicit(self):
        app = self.app()
        app.text_input(key='termo_busca').set_value('Picachu').run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Pikachu').click().run()
        self.assertEqual(app.text_input(key='termo_busca').value, 'Pikachu')
        self.assertNotIn('calls', app.session_state)
        self.assertIsNone(app.session_state['catalogo_selecionada_nome'])
        self.assertEqual(app.session_state['creditos'], 5)
        app.button(key='btn_buscar_catalogo_nome').click().run()
        self.assertEqual(app.session_state['calls'][0]['nome'], 'Pikachu')
        self.assertTrue(any(w.value == 'search_no_matches' for w in app.warning))

    def test_exact_normalized_name_hides_suggestions_but_typos_still_show(self):
        app = self.app()
        for query in ('Picachu', 'Pikachu', '  PIKACHU  ', 'pikatchu'):
            with self.subTest(query=query):
                app.text_input(key='termo_busca').set_value(query).run()
                self.assertFalse(app.exception)
                expected = normalize_search(query) != 'pikachu'
                self.assertEqual(any(c.value == 'search_did_you_mean' for c in app.caption), expected)
                self.assertEqual(any(b.label == 'Pikachu' for b in app.button), expected)
                if not expected:
                    self.assertFalse(app.get('imgs'))
                    self.assertFalse(any(c.value == 'search_representative_image' for c in app.caption))
                self.assertFalse(app.button(key='btn_buscar_catalogo_nome').disabled)
                self.assertNotIn('calls', app.session_state)

    def test_cold_failure_keeps_manual_search_and_separate_errors(self):
        app = self.app(fail_index=True)
        app.text_input(key='termo_busca').set_value('Picachu').run()
        self.assertTrue(any(c.value == 'search_suggestions_unavailable' for c in app.caption))
        self.assertFalse(app.warning)
        app.session_state['fail_catalog'] = True
        app.button(key='btn_buscar_catalogo_nome').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state['calls']), 1)
        self.assertTrue(any(e.value == 'search_catalog_unavailable' for e in app.error))
        self.assertFalse(any(w.value == 'search_no_matches' for w in app.warning))

    def test_typing_sequence_recalculates_locally_without_catalog_calls(self):
        app = self.app()
        with patch('requests.sessions.Session.request', side_effect=requests.ConnectionError()) as network:
            for query in ('Picachu', 'Pikacu', 'Pikatchu'):
                app.text_input(key='termo_busca').set_value(query).run()
                self.assertFalse(app.exception)
                self.assertTrue(any(b.label == 'Pikachu' for b in app.button))
                self.assertNotIn('calls', app.session_state)
                self.assertEqual(app.session_state['creditos'], 5)
            network.assert_not_called()
