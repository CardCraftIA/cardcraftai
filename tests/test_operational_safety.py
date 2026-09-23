"""Exercise critical orchestration with fakes, never importing the live app."""
import ast
import importlib
from pathlib import Path
from types import SimpleNamespace
import time
import unittest
from unittest.mock import Mock
import uuid
from security_utils import redact_diagnostic

SOURCE = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')


def app_definitions(*names, **namespace):
    nodes = [node for node in ast.parse(SOURCE).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'app.py', 'exec'), namespace)
    return namespace


class Session(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class OperationalSafetyTests(unittest.TestCase):
    def test_runtime_imports_resolve_without_initializing_live_app(self):
        for node in ast.parse(SOURCE).body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    importlib.import_module(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    if not hasattr(module, alias.name):
                        # `from package import submodule` loads it on demand.
                        importlib.import_module(node.module + '.' + alias.name)

    def analysis(self):
        state = Session()
        ns = app_definitions(
            'CardCraftOperationalError', '_sanitizar_detalhe_tecnico',
            '_classificar_erro_gemini', '_mensagem_falha_credito_pos_analise',
            'executar_analise_com_credito', '_executar_analise_reservada',
            st=SimpleNamespace(session_state=state), uuid=uuid, time=time,
            redact_diagnostic=redact_diagnostic, t=lambda key, *args: key,
            GEMINI_API_KEY='', SUPABASE_KEY='', SUPABASE_SERVICE_ROLE_KEY='',
            POKEMON_TCG_API_KEY='', AI_MODEL='fake-model',
            reservar_credito=Mock(), iniciar_registro_analise=Mock(return_value='run'),
            analisar_carta=Mock(return_value=({'name': 'Pikachu'}, 'fake-model')),
            devolver_credito=Mock(), falhar_registro_analise=Mock(),
            concluir_registro_analise=Mock(), atualizar_modelo_registro_analise=Mock(),
            concluir_uso_credito=Mock(return_value=True))
        return ns, state

    def test_identity_lock_failure_refunds_and_records_once(self):
        ns, _ = self.analysis()
        with self.assertRaises(RuntimeError):
            ns['executar_analise_com_credito']('English', resultado_transformer=Mock(side_effect=ValueError('bad identity')))
        ns['devolver_credito'].assert_called_once()
        ns['falhar_registro_analise'].assert_called_once()
        self.assertEqual(ns['falhar_registro_analise'].call_args.args[1], 'selected_catalog_identity_lock_failed')
        ns['concluir_uso_credito'].assert_not_called()
        self.assertEqual(ns['reservar_credito'].call_args.args[1], ns['devolver_credito'].call_args.args[0])

    def test_reentrant_analysis_does_not_reserve_twice(self):
        ns, state = self.analysis()
        def analyze(**kwargs):
            self.assertTrue(state.analysis_in_progress)
            with self.assertRaises(RuntimeError):
                ns['executar_analise_com_credito']('English')
            return {'name': 'Pikachu'}, 'fake-model'
        ns['analisar_carta'].side_effect = analyze
        ns['executar_analise_com_credito']('English')
        ns['reservar_credito'].assert_called_once()
        self.assertFalse(state.analysis_in_progress)
        self.assertEqual(state.analysis_request_id_atual, str(ns['reservar_credito'].call_args.args[1]))

    def test_reservation_failure_never_calls_ai_and_releases_busy_state(self):
        ns, state = self.analysis()
        ns['reservar_credito'].side_effect = RuntimeError('reservation unavailable')
        with self.assertRaises(RuntimeError): ns['executar_analise_com_credito']('English')
        ns['analisar_carta'].assert_not_called()
        ns['devolver_credito'].assert_not_called()
        self.assertFalse(state.analysis_in_progress)
        self.assertTrue(state.analysis_request_id_atual)

    def test_audit_start_failure_refunds_before_any_ai_call(self):
        ns, _ = self.analysis()
        ns['iniciar_registro_analise'].side_effect = RuntimeError('audit unavailable')
        with self.assertRaises(RuntimeError): ns['executar_analise_com_credito']('English')
        ns['devolver_credito'].assert_called_once()
        ns['analisar_carta'].assert_not_called()

    def test_audit_completion_failure_still_charges_once_without_repeating_ai(self):
        ns, _ = self.analysis()
        ns['concluir_registro_analise'].side_effect = RuntimeError('audit unavailable')
        ns['executar_analise_com_credito']('English')
        ns['analisar_carta'].assert_called_once()
        ns['concluir_uso_credito'].assert_called_once()
        ns['devolver_credito'].assert_not_called()

    def test_failed_refund_does_not_claim_success_or_retry(self):
        ns, state = self.analysis()
        ns['devolver_credito'].side_effect = RuntimeError('internal sentinel')
        with self.assertRaises(RuntimeError) as raised:
            ns['executar_analise_com_credito']('English', resultado_transformer=Mock(side_effect=ValueError()))
        ns['devolver_credito'].assert_called_once()
        self.assertNotIn('internal sentinel', str(raised.exception))
        self.assertIn('não pôde ser confirmado', state.aviso_credito)

    def test_success_reserves_and_completes_same_request_once(self):
        ns, _ = self.analysis()
        ns['executar_analise_com_credito']('English')
        ns['reservar_credito'].assert_called_once()
        ns['concluir_uso_credito'].assert_called_once()
        self.assertEqual(ns['reservar_credito'].call_args.args[1], ns['concluir_uso_credito'].call_args.args[0])
        ns['devolver_credito'].assert_not_called()

    def test_completion_failure_never_repeats_analysis_or_refunds(self):
        ns, state = self.analysis()
        ns['concluir_uso_credito'].side_effect = RuntimeError('internal sentinel')
        self.assertEqual(ns['executar_analise_com_credito']('English'), {'name': 'Pikachu'})
        ns['analisar_carta'].assert_called_once()
        ns['devolver_credito'].assert_not_called()
        self.assertNotIn('internal sentinel', state.aviso_credito)

    def test_technical_redaction_includes_session_tokens(self):
        ns, state = self.analysis()
        state.update(access_token='FAKE_ACCESS_SENTINEL', refresh_token='FAKE_REFRESH_SENTINEL')
        ns['GEMINI_API_KEY'] = 'FAKE_API_SENTINEL'
        self.assertEqual(ns['_sanitizar_detalhe_tecnico'](
            'FAKE_API_SENTINEL FAKE_ACCESS_SENTINEL FAKE_REFRESH_SENTINEL'),
            '[REDACTED] [REDACTED] [REDACTED]')

    def test_package_loading_error_has_no_backend_details(self):
        client = Mock()
        client.table.side_effect = RuntimeError('BACKEND_CREDENTIAL_SENTINEL')
        ns = app_definitions('buscar_pacotes_ativos', supabase=client, PRICING_CURRENCIES=['BRL'])
        with self.assertRaises(RuntimeError) as raised:
            ns['buscar_pacotes_ativos']()
        self.assertNotIn('BACKEND_CREDENTIAL_SENTINEL', str(raised.exception))
