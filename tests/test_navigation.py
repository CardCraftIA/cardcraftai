"""Full app rendering with explicit fakes: never evidence of deployed RLS/Auth."""
from pathlib import Path
import ast
from types import SimpleNamespace as Obj
from unittest import TestCase
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest
from auth_state import clear_identity
from test_operational_safety import app_definitions, Session
from test_operational_safety import SOURCE
from ui_messages import LANGUAGES


class Query:
    def __init__(self, table, fail_purchases=False):
        self.table = table
        self.fail_purchases = fail_purchases

    def __getattr__(self, name):
        return lambda *args, **kwargs: self

    def execute(self):
        if self.table == 'purchases' and self.fail_purchases:
            raise RuntimeError('PRIVATE_DIAGNOSTIC_SENTINEL')
        data = {'profiles': {'id': 'fixture-owner', 'email': 'fixture@example.invalid', 'credits': 5, 'plan': 'free'},
                'legal_acceptances': [{'id': 'fixture-acceptance'}]}.get(self.table, [])
        return Obj(data=data)


class NavigationTests(TestCase):
    def render_app(self, page, language='English', fail_purchases=False, subsequent=(), shortcut=None):
        fake = Mock()
        fake.auth.set_session.return_value = Obj(
            user=Obj(id='fixture-owner', email='fixture@example.invalid', email_confirmed_at='confirmed-by-fake'),
            session=Obj(access_token='FAKE_ACCESS', refresh_token='FAKE_REFRESH'))
        fake.table.side_effect = lambda table: Query(table, fail_purchases)
        fake.rpc.side_effect = AssertionError('Rendering must not charge, refund or mutate')
        ai = Mock()
        secrets = dict(SUPABASE_URL='https://fixture.invalid', SUPABASE_KEY='fake',
                       SUPABASE_SERVICE_ROLE_KEY='fake', GEMINI_API_KEY='fake', COLLECTIONS_ENABLED=True,
                       COMMUNITY_ENABLED=True)
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=15)
        for key, value in dict(user_id='fixture-owner', access_token='FAKE_ACCESS', refresh_token='FAKE_REFRESH',
                               idioma_interface=language, pagina_interface=page, pagina_navegacao_widget=page).items():
            app.session_state[key] = value
        with patch('streamlit.secrets', secrets), patch('supabase.create_client', return_value=fake), \
                patch('google.genai.Client', return_value=ai):
            app.run()
            for destination in subsequent:
                app.sidebar.radio[0].set_value(destination).run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state['pagina_interface'], destination)
                self.assertEqual(app.sidebar.metric[0].value, '5')
            if shortcut:
                next(button for button in app.button if button.key == f'home_open_{shortcut}').click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state['pagina_interface'], shortcut)
                self.assertEqual(app.sidebar.radio[0].value, shortcut)
                self.assertEqual(app.sidebar.metric[0].value, '5')
        self.assertFalse(app.exception, [error.message for error in app.exception])
        fake.rpc.assert_not_called()
        ai.models.generate_content.assert_not_called()
        self.assertEqual(app.sidebar.radio[0].value, shortcut or (subsequent[-1] if subsequent else page))
        if page not in ('community', 'home'):
            self.assertTrue(app.header)
        return app

    def test_every_authenticated_route_in_all_four_languages(self):
        for language in LANGUAGES:
            for page in ('home', 'chatbot', 'community', 'photo', 'search', 'collection', 'account', 'plans', 'terms', 'privacy'):
                with self.subTest(language=language, page=page):
                    app = self.render_app(page, language)
                    self.assertFalse(app.error)
                    if page == 'chatbot':
                        self.assertFalse(any(item.key and item.key.startswith('cardcraft_chat_card_') for item in app.text_input))
                        self.assertFalse(any(item.key and item.key.startswith('cardcraft_chat_set_') for item in app.text_input))
                        self.assertFalse(any(item.key and item.key.startswith('cardcraft_chat_number_') for item in app.text_input))
                    self.assertEqual(app.sidebar.metric[0].value, '5')
                    if page == 'collection' and language in ('Español', '日本語'):
                        expected = '🃏 Mi colección' if language == 'Español' else '🃏 マイコレクション'
                        self.assertIn(expected, app.sidebar.radio[0].options)

    def test_sidebar_navigation_callbacks_preserve_credit_balance(self):
        self.render_app('home', subsequent=('chatbot', 'community', 'search', 'collection', 'account', 'plans', 'terms', 'privacy', 'photo', 'home'))

    def test_home_shortcut_opens_community_without_consuming_credits(self):
        self.render_app('home', language='Português (BR)', shortcut='community')

    def test_purchase_outage_is_not_presented_as_empty_history(self):
        app = self.render_app('account', fail_purchases=True)
        self.assertIn('Purchase history is temporarily unavailable.', app.warning[0].value)
        self.assertFalse(any('PRIVATE_DIAGNOSTIC_SENTINEL' in e.value for e in app.warning))
        client = Mock()
        client.table.side_effect = RuntimeError('private')
        ns = app_definitions('buscar_compras_usuario', supabase=client, usuario_logado=lambda: True,
                             st=Obj(session_state=Session(user_id='fixture-owner')))
        self.assertIsNone(ns['buscar_compras_usuario']())

    def test_identity_cleanup_removes_previous_photo_evidence_and_history(self):
        state = Session(catalogo_validacao_foto_resultado={'private': 'prior analysis'},
                        historico_catalog_status='prior status', analise_reaberta_historico=True,
                        aviso_auditoria='prior diagnostic', ultima_recuperacao_runs='prior timestamp')
        clear_identity(state)
        self.assertNotIn('catalogo_validacao_foto_resultado', state)
        self.assertNotIn('historico_catalog_status', state)
        self.assertFalse(state.analise_reaberta_historico)
        self.assertIsNone(state.aviso_auditoria)
        self.assertIsNone(state.ultima_recuperacao_runs)

    def test_post_analysis_catalog_error_never_displays_diagnostics(self):
        handler = next(node for node in ast.walk(ast.parse(SOURCE))
                       if isinstance(node, ast.ExceptHandler) and node.name == 'erro_catalogo_pos_analise')
        state = Session()
        ns = dict(st=Obj(session_state=state), idioma='English',
                  erro_catalogo_pos_analise=RuntimeError('PRIVATE_DIAGNOSTIC_SENTINEL'),
                  t=lambda key, language: 'Safe translated catalog audit warning')
        exec(compile(ast.Module(body=handler.body, type_ignores=[]), 'app.py', 'exec'), ns)
        self.assertEqual(state.aviso_auditoria, 'Safe translated catalog audit warning')
