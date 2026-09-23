from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock
import requests
from test_operational_safety import app_definitions


def no_cache(**kwargs):
    return lambda function: function


class CatalogRuntimeTests(unittest.TestCase):
    def executor(self, replies):
        http = Obj(get=Mock(side_effect=replies), RequestException=requests.RequestException)
        ns = app_definitions('_executar_requisicao_tcgdex', st=Obj(cache_data=no_cache), requests=http,
                             time=Obj(sleep=Mock()), TCGDEX_API_BASE='https://catalog.example.invalid')
        return ns['_executar_requisicao_tcgdex'], http

    def response(self, status=200, payload=None):
        response = Mock(status_code=status)
        response.json.return_value = payload
        return response

    def test_timeout_retry_is_bounded(self):
        execute, http = self.executor([requests.Timeout(), requests.Timeout()])
        with self.assertRaises(RuntimeError): execute('cards')
        self.assertEqual(http.get.call_count, 2)
        self.assertEqual(http.get.call_args.kwargs['timeout'], 12)

    def test_transient_retry_then_success(self):
        execute, http = self.executor([self.response(503), self.response(payload=[])])
        self.assertEqual(execute('cards'), [])
        self.assertEqual(http.get.call_count, 2)

    def test_not_found_is_distinct_from_invalid_json(self):
        execute, _ = self.executor([self.response(404)])
        self.assertIsNone(execute('cards/missing'))
        for payload in ('unexpected text', 7, None):
            execute, _ = self.executor([self.response(payload=payload)])
            with self.assertRaises(RuntimeError): execute('cards')

    def query(self, request):
        return app_definitions('consultar_catalogo_tcgdex', st=Obj(cache_data=no_cache),
            _set_id_catalogo_por_colecao=lambda *args: '', _set_id_catalogo_por_numero=lambda *args: '',
            _numero_principal_catalogo=lambda value: value, _similaridade_catalogo=lambda *args: 1,
            _numeros_catalogo_equivalentes=lambda a, b: a == b,
            _executar_requisicao_tcgdex=request, _adaptar_carta_tcgdex=lambda card, **kwargs: card,
            _resolver_set_tcgdex=Mock(return_value=None))['consultar_catalogo_tcgdex']

    def test_partial_detail_failure_preserves_valid_results_and_refresh_key(self):
        request = Mock(side_effect=[[{'id': 'a', 'name': 'Pikachu'}, {'id': 'b', 'name': 'Pikachu'}],
                                    RuntimeError('offline'), {'id': 'b', 'name': 'Pikachu'}])
        results = self.query(request)('Pikachu', cache_buster=9)
        self.assertEqual(results, [{'id': 'b', 'name': 'Pikachu'}])
        self.assertTrue(all(call.kwargs['cache_buster'] == 9 for call in request.call_args_list))
        self.assertEqual(request.call_args.kwargs['tentativas'], 1)

    def test_total_detail_failure_is_not_an_empty_result(self):
        request = Mock(side_effect=[[{'id': 'a', 'name': 'Pikachu'}], RuntimeError('offline')])
        with self.assertRaises(RuntimeError): self.query(request)('Pikachu')

    def test_duplicate_details_are_requested_once_and_card_without_image_is_kept(self):
        brief = {'id': 'a', 'name': 'Pikachu'}
        request = Mock(side_effect=[[brief, brief], brief])
        self.assertEqual(self.query(request)('Pikachu'), [brief])
        self.assertEqual(request.call_count, 2)

    def test_detail_request_count_has_a_hard_bound(self):
        records = [{'id': str(i), 'name': 'Pikachu'} for i in range(100)]
        request = Mock(side_effect=lambda path, **kwargs: records if path == 'cards' else {'id': path})
        self.assertEqual(len(self.query(request)('Pikachu', limite=1000)), 48)
        self.assertEqual(request.call_count, 49)

    def providers(self, primary, legacy):
        ns = app_definitions('buscar_cartas_catalogo_pokemon', consultar_catalogo_tcgdex=primary,
            consultar_catalogo_pokemon=legacy, consultar_catalogo_pokemon_por_numero=Mock(return_value=[]),
            consultar_catalogo_pokemon_por_nome_e_colecao=Mock(return_value=[]),
            ranquear_cartas_catalogo=lambda cards, **kwargs: cards)
        return ns['buscar_cartas_catalogo_pokemon']

    def test_valid_empty_primary_is_not_disguised_as_legacy_outage(self):
        search = self.providers(Mock(return_value=[]), Mock(side_effect=RuntimeError('legacy down')))
        self.assertEqual(search('Missing'), [])

    def test_legacy_fallback_and_both_providers_unavailable(self):
        search = self.providers(Mock(side_effect=RuntimeError('primary down')), Mock(return_value=[{'id': 'a'}]))
        self.assertEqual(search('Pikachu'), [{'id': 'a'}])
        search = self.providers(Mock(side_effect=RuntimeError('primary down')), Mock(side_effect=RuntimeError('legacy down')))
        with self.assertRaises(RuntimeError): search('Pikachu')
