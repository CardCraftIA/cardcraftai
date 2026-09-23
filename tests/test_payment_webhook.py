import hashlib
import hmac
from unittest import TestCase
from unittest.mock import Mock, patch

from payment_webhook import WebhookRejected, verify_signature, fetch_verified_payment


class WebhookVerificationTests(TestCase):
    secret = 'FAKE_WEBHOOK_TEST_SECRET'
    now = 1704908010

    def signature(self, ts='1704908010'):
        manifest = f'id:1234;request-id:test-request;ts:{ts};'
        digest = hmac.new(self.secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
        return f'ts={ts},v1={digest}'

    def test_valid_seconds_and_milliseconds(self):
        for ts in ('1704908010', '1704908010000'):
            self.assertEqual(verify_signature(self.signature(ts), 'test-request', '1234', self.secret, now=self.now), '1234')

    def test_tampering_rejected_before_network(self):
        with patch('payment_webhook.requests.get') as get:
            for request, identity, secret in [('other', '1234', self.secret), ('test-request', '1235', self.secret), ('test-request', '1234', 'wrong')]:
                with self.assertRaises(WebhookRejected):
                    fetch_verified_payment(self.signature(), request, identity, secret, 'fake-access', now=self.now)
            get.assert_not_called()

    def test_missing_duplicate_and_malformed_headers_rejected(self):
        for header in ('', 'v1=abc', self.signature() + ',ts=1704908010', 'ts=garbage,v1=abc'):
            with self.assertRaises(WebhookRejected):
                verify_signature(header, 'test-request', '1234', self.secret, now=self.now)

    def test_old_and_future_notifications_rejected(self):
        for now in (self.now - 301, self.now + 301):
            with self.assertRaises(WebhookRejected):
                verify_signature(self.signature(), 'test-request', '1234', self.secret, now=now)

    def test_untrusted_resource_path_rejected(self):
        for identity in ('../users', 'https://evil.invalid', '1234?token=x'):
            with self.assertRaises(WebhookRejected):
                verify_signature(self.signature(), 'test-request', identity, self.secret, now=self.now)

    def test_signed_notification_fetches_authoritative_provider_record(self):
        response = Mock(status_code=200)
        response.json.return_value = {'id': 1234, 'status': 'pending'}
        with patch('payment_webhook.requests.get', return_value=response) as get:
            payment = fetch_verified_payment(self.signature(), 'test-request', '1234', self.secret, 'fake-access', now=self.now)
        self.assertEqual(payment['status'], 'pending')
        self.assertEqual(get.call_args.args[0], 'https://api.mercadopago.com/v1/payments/1234')
        self.assertFalse(get.call_args.kwargs['allow_redirects'])
        self.assertEqual(get.call_args.kwargs['timeout'], 10)

    def test_provider_failures_do_not_return_payload_or_credentials(self):
        for code, payload in ((302, {}), (500, {}), (200, {'id': 9999}), (200, [])):
            response = Mock(status_code=code)
            response.json.return_value = payload
            with patch('payment_webhook.requests.get', return_value=response):
                with self.assertRaises(WebhookRejected) as raised:
                    fetch_verified_payment(self.signature(), 'test-request', '1234', self.secret, 'FAKE_ACCESS_SENTINEL', now=self.now)
                self.assertNotIn('FAKE_ACCESS_SENTINEL', str(raised.exception))
