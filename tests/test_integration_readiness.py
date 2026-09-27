import unittest
from unittest.mock import patch
import sys
from types import SimpleNamespace

from integration_readiness import brevo_readiness, checkout_enabled, paypal_readiness
from paypal_gateway import PayPalGateway


class IntegrationReadinessTests(unittest.TestCase):
    def test_brevo_requires_real_delivery_evidence(self):
        self.assertFalse(all(brevo_readiness({'BREVO_SENDER_EMAIL': 'hello@example.com'}).values()))

    def test_paypal_settings_cannot_enable_checkout(self):
        settings = {'PAYPAL_CLIENT_ID': 'id', 'PAYPAL_CLIENT_SECRET': 'secret', 'PAYPAL_WEBHOOK_ID': 'wh',
                    'PAYPAL_WEBHOOK_URL': 'https://test.example.com/hooks/paypal', 'PAYPAL_PLAN_ID': 'P-0123456789',
                    'PAYPAL_LEDGER_VERIFIED': 'true', 'PAYPAL_SANDBOX_SCENARIOS_PASSED': 'true'}
        self.assertTrue(all(paypal_readiness(settings).values()))
        self.assertFalse(checkout_enabled(settings))

    def test_paypal_rejects_mixed_environment_approval_and_mismatched_lookup(self):
        gateway = PayPalGateway('id', 'secret', 'wh', sandbox=True)
        gateway.token = lambda: 'fake'
        class Response:
            def __init__(self, value): self.value = value
            def raise_for_status(self): pass
            def json(self): return self.value
        with patch.dict(sys.modules, {'requests': SimpleNamespace(post=lambda *a, **k: Response({'id': 'I-12345678', 'links': [
                {'rel': 'approve', 'href': 'https://www.paypal.com/checkoutnow?token=1'}]}))}):
            with self.assertRaises(ValueError):
                gateway.create_subscription('P-12345678', 'order_1234', 'https://test.example.com/return', 'https://test.example.com/cancel')
        with patch.dict(sys.modules, {'requests': SimpleNamespace(get=lambda *a, **k: Response({'id': 'I-DIFFERENT'}))}):
            with self.assertRaises(ValueError):
                gateway.subscription('I-12345678')


if __name__ == '__main__':
    unittest.main()
