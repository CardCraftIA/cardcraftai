"""PayPal subscription transport for a future verified server checkout.

Never enable purchases from this module alone: a webhook and an idempotent
subscription ledger must be deployed before showing approval links.
"""

from urllib.parse import urlparse
import re

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
        if not re.fullmatch(r'P-[A-Za-z0-9]{8,40}', str(plan_id or '')) or not re.fullmatch(r'[A-Za-z0-9_-]{8,127}', str(custom_id or '')):
            raise ValueError('Invalid subscription request')
        parsed_urls = [urlparse(str(url)) for url in (return_url, cancel_url)]
        if any(url.scheme != 'https' or not url.hostname or url.username or url.password or url.fragment
               for url in parsed_urls) or parsed_urls[0].hostname != parsed_urls[1].hostname:
            raise ValueError('Invalid subscription request')
        response = requests.post(self.base + '/v1/billing/subscriptions',
                                 headers={'Authorization': 'Bearer ' + self.token(), 'Content-Type': 'application/json'},
                                 json={'plan_id': plan_id, 'custom_id': custom_id,
                                       'application_context': {'return_url': return_url, 'cancel_url': cancel_url}}, timeout=10)
        response.raise_for_status()
        data = response.json()
        approve = next((link.get('href') for link in data.get('links', []) if link.get('rel') == 'approve'), None)
        expected_host = 'www.sandbox.paypal.com' if self.base.endswith('sandbox.paypal.com') else 'www.paypal.com'
        approved = urlparse(str(approve or ''))
        if approved.scheme != 'https' or approved.hostname != expected_host or approved.username or approved.password:
            raise ValueError('PayPal approval URL missing')
        return data['id'], approve

    def subscription(self, subscription_id):
        """Read provider state; a browser redirect is never proof of payment."""
        import requests
        if not re.fullmatch(r'I-[A-Za-z0-9]{8,40}', str(subscription_id or '')):
            raise ValueError('Invalid subscription ID')
        response = requests.get(self.base + '/v1/billing/subscriptions/' + subscription_id,
                                headers={'Authorization': 'Bearer ' + self.token()}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('id') != subscription_id:
            raise ValueError('Subscription ID mismatch')
        return data

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
