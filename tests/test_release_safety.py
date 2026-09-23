import io
import unittest
from types import SimpleNamespace as Obj
from unittest.mock import Mock, patch

from PIL import Image
from auth_state import accept_session, clear_identity, confirmed_email, restore_session
from image_utils import load_upload
from payment_utils import package_code, safe_checkout_url
from security_utils import redact_diagnostic, safe_public_image
from ui_messages import install_messages, LANGUAGES
from test_operational_safety import app_definitions, Session


def auth_response(confirmed=True, session=True):
    return Obj(user=Obj(id='owner', email='test@example.invalid',
                        email_confirmed_at='server timestamp' if confirmed else None),
               session=Obj(access_token='FAKE_ACCESS', refresh_token='FAKE_REFRESH') if session else None)


class AuthenticationTests(unittest.TestCase):
    def test_unconfirmed_signup_never_grants_access(self):
        state = Session(user_id='stale-owner', access_token='stale')
        self.assertFalse(accept_session(state, auth_response(False, False)))
        self.assertEqual(state.auth_status, 'email_unconfirmed')
        self.assertIsNone(state.user_id)

    def test_confirmed_response_saves_server_identity(self):
        state = Session()
        self.assertTrue(accept_session(state, auth_response()))
        self.assertEqual(state.auth_status, 'authenticated')
        self.assertEqual(state.user_id, 'owner')

    def test_phone_confirmation_is_not_email_confirmation(self):
        self.assertFalse(confirmed_email(Obj(email='a@example.invalid', confirmed_at='phone-only', email_confirmed_at=None)))

    def test_incomplete_refresh_clears_previous_identity(self):
        for response in (None, Obj(user=None, session=None), auth_response(session=False)):
            state = Session(access_token='old', refresh_token='old', user_id='old-owner', email_confirmado=True)
            client = Mock()
            client.auth.set_session.return_value = response
            self.assertFalse(restore_session(client, state))
            self.assertIsNone(state.user_id)
            self.assertFalse(state.email_confirmado)

    def test_refresh_updates_both_tokens(self):
        state = Session(access_token='old', refresh_token='old')
        client = Mock()
        client.auth.set_session.return_value = auth_response()
        self.assertTrue(restore_session(client, state))
        self.assertEqual(state.access_token, 'FAKE_ACCESS')
        self.assertEqual(state.refresh_token, 'FAKE_REFRESH')

    def test_account_change_or_expiry_clears_previous_private_results(self):
        for response in (auth_response(), None):
            state = Session(user_id='previous-owner', resultado_analise='private result', collection_baseline_old={'notes': 'private'})
            accept_session(state, response)
            self.assertIsNone(state.resultado_analise)
            self.assertNotIn('collection_baseline_old', state)

    def test_same_user_refresh_preserves_current_work(self):
        state = Session(user_id='owner', resultado_analise='current result', collection_search_owner='Pika')
        accept_session(state, auth_response())
        self.assertEqual(state.resultado_analise, 'current result')
        self.assertEqual(state.collection_search_owner, 'Pika')

    def test_expired_and_auth_service_error_are_distinct(self):
        for code, expected in (('refresh_token_not_found', 'expired'), ('network_error', 'error'), ('email_not_confirmed', 'email_unconfirmed')):
            error = RuntimeError('private diagnostic')
            error.code = code
            client = Mock()
            client.auth.set_session.side_effect = error
            state = Session(access_token='old', refresh_token='old')
            self.assertFalse(restore_session(client, state))
            self.assertEqual(state.auth_status, expected)
            self.assertIsNone(state.access_token)

    def test_missing_token_pair_never_calls_auth(self):
        client = Mock()
        state = Session(access_token='old', refresh_token=None, user_id='old-owner')
        self.assertFalse(restore_session(client, state))
        self.assertEqual(state.auth_status, 'expired')
        client.auth.set_session.assert_not_called()

    def test_logout_clears_private_state_but_keeps_language(self):
        state = Session(collection_search_owner='private name', collection_baseline_owner={'notes': 'private'},
                        senha_login='fake password', idioma_interface='Español')
        ns = app_definitions('limpar_sessao', st=Obj(session_state=state), clear_identity=clear_identity)
        ns['limpar_sessao']()
        self.assertNotIn('collection_baseline_owner', state)
        self.assertNotIn('senha_login', state)
        self.assertEqual(state.idioma_interface, 'Español')
        self.assertEqual(state.auth_status, 'signed_out')

    def test_recovery_clears_url_token_on_success_and_error(self):
        for success in (True, False):
            state = Session(recovery_link_processed=None, modo_recuperacao_senha=False)
            query = {'token_hash': 'fake-one-time-token', 'type': 'recovery', 'language': 'en'}
            client = Mock()
            client.auth.verify_otp.return_value = auth_response()
            if not success:
                client.auth.verify_otp.side_effect = RuntimeError('invalid token')
            ns = app_definitions('processar_link_recuperacao_senha', st=Obj(session_state=state, query_params=query),
                                 supabase=client, salvar_sessao=lambda response: accept_session(state, response),
                                 limpar_sessao=lambda: clear_identity(state), t=lambda key: key)
            ns['processar_link_recuperacao_senha']()
            self.assertNotIn('token_hash', query)
            self.assertEqual(query, {'language': 'en'})
            self.assertEqual(state.modo_recuperacao_senha, success)


class PaymentTests(unittest.TestCase):
    def checkout(self, payload=None, status=200):
        response = Mock(status_code=status, ok=status == 200)
        response.json.return_value = payload if payload is not None else {
            'ok': True, 'checkout_url': 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=fake',
            'preference_id': 'fake', 'package': {'code': 'STARTER_10', 'currency': 'BRL'}}
        http = Mock()
        http.post.return_value = response
        ns = app_definitions('criar_preferencia_mercadopago', usuario_logado=lambda: True,
            st=Obj(session_state=Session(access_token='FAKE_ACCESS')), SUPABASE_URL='https://project.example.invalid',
            SUPABASE_KEY='FAKE_PUBLIC', requests=http, validate_package_code=package_code,
            safe_checkout_url=safe_checkout_url)
        return ns, http

    def test_backend_receives_only_package_code_not_price_or_user_id(self):
        ns, http = self.checkout()
        result = ns['criar_preferencia_mercadopago'](' starter_10 ')
        self.assertEqual(http.post.call_args.kwargs['json'], {'package_code': 'STARTER_10'})
        self.assertEqual(http.post.call_args.kwargs['timeout'], 20)
        self.assertEqual(result['preference_id'], 'fake')

    def test_invalid_package_never_calls_backend(self):
        ns, http = self.checkout()
        for code in ('', '../package', 'A' * 65):
            with self.assertRaises(ValueError):
                ns['criar_preferencia_mercadopago'](code)
        http.post.assert_not_called()

    def test_untrusted_checkout_urls_are_rejected(self):
        for url in ('https://evil.invalid/checkout/', 'javascript:alert(1)',
                    'https://www.mercadopago.com.br.evil.invalid/checkout/',
                    'https://user@www.mercadopago.com.br/checkout/', 'https://[broken',
                    'https://www.mercadopago.com.br:444/checkout/'):
            self.assertFalse(safe_checkout_url(url))
        self.assertTrue(safe_checkout_url('https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=fake'))

    def test_wrong_package_currency_and_host_are_rejected(self):
        for changes in ({'package': {'code': 'OTHER'}}, {'package': {'currency': 'USD'}},
                        {'checkout_url': 'https://evil.invalid/checkout/'}, {'preference_id': ''}):
            payload = {'ok': True, 'checkout_url': 'https://www.mercadopago.com.br/checkout/v1/redirect', 'preference_id': 'fake'}
            ns, _ = self.checkout({**payload, **changes})
            with self.assertRaises(RuntimeError):
                ns['criar_preferencia_mercadopago']('STARTER_10')

    def test_provider_error_never_exposes_payload(self):
        ns, _ = self.checkout({'error': 'PRIVATE_PROVIDER_SENTINEL'}, 500)
        with self.assertRaises(RuntimeError) as error:
            ns['criar_preferencia_mercadopago']('STARTER_10')
        self.assertNotIn('PRIVATE_PROVIDER_SENTINEL', str(error.exception))

    def test_payment_return_is_visual_only_even_if_spoofed(self):
        for status in ('success', 'pending', 'failure', 'approved', 'rejected'):
            state = Session(creditos=5)
            query = {'payment': status, 'credits': '999', 'status': 'approved'}
            ns = app_definitions('processar_retorno_mercadopago', st=Obj(session_state=state, query_params=query))
            ns['processar_retorno_mercadopago']()
            self.assertEqual(state.creditos, 5)
            if status in ('success', 'pending', 'failure'):
                self.assertEqual(state.payment_return_status, status)
                self.assertFalse(query)
            else:
                self.assertNotIn('payment_return_status', state)


class UploadTests(unittest.TestCase):
    def upload(self, fmt='PNG', size=(16, 12), **kwargs):
        file = io.BytesIO()
        Image.new('RGB', size).save(file, format=fmt, **kwargs)
        file.name = 'card.' + {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp', 'GIF': 'gif'}[fmt]
        file.type = 'image/' + fmt.lower()
        file.size = len(file.getvalue())
        file.seek(0)
        return file

    def test_supported_formats_decode_to_rgb_without_metadata(self):
        for fmt in ('JPEG', 'PNG', 'WEBP'):
            decoded = load_upload(self.upload(fmt))
            self.assertEqual(decoded.mode, 'RGB')
            self.assertEqual(decoded.size, (16, 12))
            self.assertFalse(decoded.info)

    def test_corruption_extension_and_mime_are_rejected(self):
        for change in ('corrupt', 'extension', 'mime', 'unsupported'):
            upload = self.upload('GIF' if change == 'unsupported' else 'PNG')
            if change == 'corrupt': upload = io.BytesIO(b'not an image')
            if change == 'extension': upload.name = 'card.jpg'
            if change == 'mime': upload.type = 'text/html'
            with self.assertRaises(ValueError): load_upload(upload)

    def test_bytes_and_pixels_are_bounded_before_decoding(self):
        with self.assertRaises(ValueError): load_upload(self.upload(), max_bytes=10)
        upload = self.upload()
        with patch('PIL.Image.Image.load', side_effect=AssertionError('Decoded before dimension check')):
            with self.assertRaises(ValueError): load_upload(upload, max_pixels=100)

    def test_declared_size_cannot_bypass_real_limit(self):
        upload = self.upload()
        upload.size = 1
        with self.assertRaises(ValueError): load_upload(upload, max_bytes=10)

    def test_exif_orientation_is_applied_and_private_metadata_removed(self):
        exif = Image.Exif()
        exif[274] = 6
        exif[270] = 'PRIVATE_SENTINEL'
        image = load_upload(self.upload('JPEG', exif=exif))
        self.assertEqual(image.size, (12, 16))
        self.assertFalse(image.getexif())

    def test_invalid_upload_cannot_reach_paid_analysis(self):
        from test_operational_safety import SOURCE
        from streamlit.testing.v1 import AppTest
        import textwrap
        start = SOURCE.index('            tamanho_arquivo = int(')
        end = SOURCE.index('\n        else:\n', start)
        body = textwrap.dedent(SOURCE[start:end])
        setup = '''
import io
import streamlit as st
from image_utils import load_upload
uploaded_file = io.BytesIO(b'not an image')
MAX_UPLOAD_BYTES = 1024
MAX_UPLOAD_MB = 1
IMAGE_PREVIEW_WIDTH = 100
creditos = 5
idioma = 'English'
def t(key, *args, **kwargs): return key
def executar_analise_com_credito(**kwargs): raise AssertionError('Paid analysis must not run')
'''
        app = AppTest.from_string(textwrap.dedent(setup) + body).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.error[0].value, 'image_open_failed')
        self.assertFalse(app.button)


class DiagnosticAndLocaleTests(unittest.TestCase):
    def test_full_app_stops_safely_when_secrets_are_absent(self):
        from pathlib import Path
        from streamlit.testing.v1 import AppTest
        with patch('streamlit.secrets', {}):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertFalse(app.button)

    def test_unknown_credentials_in_diagnostics_are_redacted(self):
        text = 'Bearer FAKE_BEARER_VALUE refresh_token=FAKE_REFRESH_VALUE password=fake-password'
        result = redact_diagnostic(text)
        for secret in ('FAKE_BEARER_VALUE', 'FAKE_REFRESH_VALUE', 'fake-password'):
            self.assertNotIn(secret, result)

    def test_bad_image_url_does_not_crash(self):
        for url in ('https://[invalid', 'https://user:pass@assets.tcgdex.net/image', 'http://assets.tcgdex.net/image'):
            self.assertEqual(safe_public_image(url), '')

    def test_release_messages_available_in_four_languages(self):
        tables = {language: {} for language in LANGUAGES}
        install_messages(tables)
        for language in LANGUAGES:
            for key in ('auth_expired', 'auth_error', 'auth_email_unconfirmed', 'analysis_busy', 'legal_check_failed'):
                self.assertTrue(tables[language][key])
        self.assertEqual(tables['Español']['collection_ui:My collection'], 'Mi colección')
        self.assertIn('{count}', tables['日本語']['collection_ui:{count} entries found'])
