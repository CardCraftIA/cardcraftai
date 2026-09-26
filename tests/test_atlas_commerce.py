import unittest
from types import SimpleNamespace

from atlas_access import claim_question
from chatbot import upgrade_message
from payment_assistant import reply
from paypal_gateway import PayPalGateway


class AtlasCommerceTests(unittest.TestCase):
    def test_rpc_result_must_be_explicit(self):
        class Client:
            def rpc(self, name):
                self.name = name
                return SimpleNamespace(execute=lambda: SimpleNamespace(data={'allowed': False, 'remaining': 0}))
        client = Client()
        self.assertFalse(claim_question(client)['allowed'])
        self.assertEqual(client.name, 'claim_atlas_question')
        with self.assertRaises(ValueError):
            claim_question(SimpleNamespace(rpc=lambda _: SimpleNamespace(execute=lambda: SimpleNamespace(data=[]))))

    def test_payment_helper_never_offers_unavailable_paypal(self):
        self.assertIn('ainda não está habilitado', reply('Posso pagar com PayPal?'))
        self.assertIn('BRL', reply('International checkout?', 'English'))
        self.assertIn('5 perguntas', upgrade_message('Português (BR)'))

    def test_paypal_requires_server_configuration(self):
        with self.assertRaises(ValueError):
            PayPalGateway('', '', '')


if __name__ == '__main__':
    unittest.main()
