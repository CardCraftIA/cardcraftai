"""Redact technical diagnostics before storage; never format secrets for the UI."""
import re
from urllib.parse import urlsplit


def safe_public_image(value, hosts=('assets.tcgdex.net', 'images.pokemontcg.io')):
    try:
        url = str(value or '')
        parsed = urlsplit(url)
        if (parsed.scheme == 'https' and parsed.hostname in hosts and
                not parsed.username and not parsed.password and parsed.port in (None, 443)
                and not any(ord(c) < 32 for c in url)):
            return url
    except ValueError:
        pass
    return ''


def redact_diagnostic(value, known_secrets=(), limit=4000):
    text = str(value or '')
    for secret in sorted((str(s) for s in known_secrets if s and len(str(s)) >= 8), key=len, reverse=True):
        text = text.replace(secret, '[REDACTED]')
    text = re.sub(r'(?i)\bBearer\s+[^\s,;]+', 'Bearer [REDACTED]', text)
    text = re.sub(r'\beyJ[\w-]+\.[\w-]+\.[\w-]+', '[REDACTED]', text)
    text = re.sub(r'(?i)((?:access_token|refresh_token|token_hash|password|apikey|api_key|secret|authorization)[\s"\x27]*[:=][\s"\x27]*)[^\s&;,"\x27}]+', r'\1[REDACTED]', text)
    text = re.sub(r'(https?://)[^\s/@]+:[^\s/@]+@', r'\1[REDACTED]@', text)
    return text[:limit]
