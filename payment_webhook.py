"""Server-side verification building block, not a deployed webhook or credit ledger.

An eventual endpoint must pass data.id from the URL, not a body-supplied status,
then fetch the payment from Mercado Pago. No credit is granted by this module.
"""
import hashlib
import hmac
import re
import time

import requests


class WebhookRejected(ValueError):
    """Safe diagnostic without provider payloads or credentials."""


def verify_signature(signature, request_id, payment_id, secret, *, now=None, tolerance=300):
    """Verify signed payment notification, including a bounded replay window.

Only numeric Payments API IDs are supported. Timestamp units may be seconds or
milliseconds; the original timestamp string must be retained in the HMAC input.
Persistent duplicate protection still belongs in the database transaction.
"""
    if not isinstance(secret, str) or not secret or not 0 < tolerance <= 3600:
        raise WebhookRejected('Invalid verification configuration')
    if not re.fullmatch(r'[0-9]{1,32}', str(payment_id)) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', str(request_id)):
        raise WebhookRejected('Invalid notification identifiers')
    parts = {}
    for field in str(signature).split(','):
        key, separator, value = field.strip().partition('=')
        if not separator or key in parts or key not in {'ts', 'v1'}:
            raise WebhookRejected('Invalid signature header')
        parts[key] = value
    ts, digest = parts.get('ts', ''), parts.get('v1', '')
    if not re.fullmatch(r'[0-9]{10}|[0-9]{13}', ts) or not re.fullmatch(r'[a-fA-F0-9]{64}', digest):
        raise WebhookRejected('Invalid signature header')
    timestamp = int(ts) / (1000 if len(ts) == 13 else 1)
    if abs((time.time() if now is None else now) - timestamp) > tolerance:
        raise WebhookRejected('Notification outside accepted time window')
    manifest = f'id:{payment_id};request-id:{request_id};ts:{ts};'
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, digest.lower()):
        raise WebhookRejected('Invalid notification signature')
    return str(payment_id)


def fetch_verified_payment(signature, request_id, payment_id, secret, access_token, *, now=None):
    """Authenticated lookup only after signature validation; no redirects/retries.

The caller must compare owner, currency, amount, reference, environment and
status to its server-owned purchase, then atomically deduplicate and fulfill.
"""
    verified_id = verify_signature(signature, request_id, payment_id, secret, now=now)
    if not access_token:
        raise WebhookRejected('Payment lookup is not configured')
    try:
        response = requests.get('https://api.mercadopago.com/v1/payments/' + verified_id,
                                headers={'Authorization': 'Bearer ' + access_token},
                                timeout=10, allow_redirects=False)
        if response.status_code != 200:
            raise WebhookRejected('Payment lookup unavailable')
        payment = response.json()
    except (requests.RequestException, ValueError):
        raise WebhookRejected('Payment lookup unavailable') from None
    if not isinstance(payment, dict) or str(payment.get('id')) != verified_id:
        raise WebhookRejected('Unexpected payment response')
    return payment
