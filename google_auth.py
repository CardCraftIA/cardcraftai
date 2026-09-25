"""Short lived, one use Google OAuth requests for the Streamlit server.

The PKCE verifier remains in the server process. The callback is bound to the
browser's Streamlit XSRF cookie and is never allowed to choose a redirect URL.
"""

import hashlib
import hmac
import secrets
import threading
import time
from urllib.parse import urlparse


OAUTH_TTL_SECONDS = 900


def canonical_app_url(value):
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("A URL pública do app deve usar HTTPS.")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Configure apenas a origem pública do app.")
    return parsed.geturl().rstrip("/") + "/"


def browser_binding(cookie):
    if not cookie:
        return None
    return hashlib.sha256(str(cookie).encode()).digest()


class PendingGoogleAuth:
    def __init__(self):
        self._lock = threading.Lock()
        self._pending = {}

    def begin(self, client, redirect_to, cookie, idioma):
        binding = browser_binding(cookie)
        state = secrets.token_urlsafe(32)
        # A separate client keeps the library's PKCE verifier private to this flow.
        response = client.auth.sign_in_with_oauth({
            "provider": "google", "options": {"redirect_to": redirect_to + "?google_state=" + state}
        })
        url = getattr(response, "url", None)
        if not url or not str(url).startswith("https://"):
            raise ValueError("O provedor Google não está disponível.")
        with self._lock:
            self._prune()
            self._pending[state] = (client, binding, time.monotonic() + OAUTH_TTL_SECONDS, idioma)
        return url

    def _prune(self):
        now = time.monotonic()
        for key, (_, _, expires, _) in list(self._pending.items()):
            if expires <= now:
                del self._pending[key]

    def finish(self, state, code, cookie):
        binding = browser_binding(cookie)
        with self._lock:
            self._prune()
            item = self._pending.get(state)
            if not item or (item[1] is not None and (binding is None or not hmac.compare_digest(item[1], binding))):
                raise ValueError("O acesso expirou. Tente entrar com Google novamente.")
            # Consume before exchanging: callback replay cannot use this request again.
            del self._pending[state]
        if not code:
            raise ValueError("O acesso com Google foi cancelado.")
        client, _, _, idioma = item
        return client.auth.exchange_code_for_session({"auth_code": code}), idioma
