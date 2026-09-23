"""Validate checkout transport fields; pricing and fulfillment stay server-owned."""
import re
from urllib.parse import urlsplit


def package_code(value):
    code = str(value or '').strip().upper()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9_]{0,63}', code):
        raise ValueError('Invalid package code')
    return code


def safe_checkout_url(value):
    try:
        url = str(value or '').strip()
        parts = urlsplit(url)
        return bool(parts.scheme == 'https' and parts.hostname in {
            'www.mercadopago.com.br', 'sandbox.mercadopago.com.br'
        } and not parts.username and not parts.password and parts.port in (None, 443)
            and parts.path.startswith('/checkout/') and not any(ord(c) < 32 for c in url))
    except ValueError:
        return False
