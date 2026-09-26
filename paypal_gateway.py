"""PayPal subscription transport for a future verified server checkout.

Never enable purchases from this module alone: a webhook and an idempotent
subscription ledger must be deployed before showing approval links.
"""

from urllib.parse import urlparse

class PayPalGateway:
    def __init__(self, client_id, client_secret, webhook_id, *, sandbox=True):
        if not all((client_id, client_secret, webhook_id)):
            raise ValueError('PayPal server configuration incomplete')
        self.client_id, self.client_secret, self.webhook_id = client_id, client_secret, webhook_id
        self.base = 'https://api-m.sandbox.paypal.com' if sandbox else 'https://api-m.paypal.com'

    def token(self):
        import requests
        response = requests.post(self.base + '/v1/oauth2/token', auth=(self.client_id, self.client_secret),
                                 data={'grant_type': 'client_credentials'}, timeout=10)
        response.raise_for_status()
        return response.json()['access_token']

    def create_subscription(self, plan_id, custom_id, return_url, cancel_url):
        import requests
        if not plan_id or not custom_id or not all(urlparse(url).scheme == 'https' for url in (return_url, cancel_url)):
            raise ValueError('Invalid subscription request')
        response = requests.post(self.base + '/v1/billing/subscriptions',
                                 headers={'Authorization': 'Bearer ' + self.token(), 'Content-Type': 'application/json'},
                                 json={'plan_id': plan_id, 'custom_id': custom_id,
                                       'application_context': {'return_url': return_url, 'cancel_url': cancel_url}}, timeout=10)
        response.raise_for_status()
        data = response.json()
        approve = next((link.get('href') for link in data.get('links', []) if link.get('rel') == 'approve'), None)
        if not approve or urlparse(approve).hostname not in {'www.paypal.com', 'www.sandbox.paypal.com'}:
            raise ValueError('PayPal approval URL missing')
        return data['id'], approve

    def verify_webhook(self, headers, event):
        import requests
        required = ('paypal-transmission-id', 'paypal-transmission-time', 'paypal-transmission-sig',
                    'paypal-cert-url', 'paypal-auth-algo')
        normalized = {str(key).lower(): value for key, value in headers.items()}
        if any(not normalized.get(key) for key in required):
            raise ValueError('PayPal signature headers missing')
        response = requests.post(self.base + '/v1/notifications/verify-webhook-signature',
                                 headers={'Authorization': 'Bearer ' + self.token(), 'Content-Type': 'application/json'},
                                 json={'transmission_id': normalized['paypal-transmission-id'],
                                       'transmission_time': normalized['paypal-transmission-time'],
                                       'transmission_sig': normalized['paypal-transmission-sig'],
                                       'cert_url': normalized['paypal-cert-url'], 'auth_algo': normalized['paypal-auth-algo'],
                                       'webhook_id': self.webhook_id, 'webhook_event': event}, timeout=10)
        response.raise_for_status()
        return response.json().get('verification_status') == 'SUCCESS'
