import unittest
from types import SimpleNamespace

from google_auth import PendingGoogleAuth, canonical_app_url


class FakeAuth:
    def __init__(self):
        self.oauth_args = None
        self.code = None

    def sign_in_with_oauth(self, args):
        self.oauth_args = args
        return SimpleNamespace(url="https://example.supabase.co/auth/v1/authorize?provider=google")

    def exchange_code_for_session(self, args):
        self.code = args
        return "session"


class GoogleAuthTests(unittest.TestCase):
    def test_one_use_browser_bound_exchange(self):
        auth = FakeAuth()
        pending = PendingGoogleAuth()
        url = pending.begin(SimpleNamespace(auth=auth), "https://cardcraftai-test.streamlit.app", "cookie-one", "Português (BR)")
        self.assertIn("provider=google", url)
        redirect = auth.oauth_args["options"]["redirect_to"]
        state = redirect.split("google_state=", 1)[1]
        with self.assertRaises(ValueError):
            pending.finish(state, "code", "cookie-two")
        self.assertEqual(pending.finish(state, "code", "cookie-one"), ("session", "Português (BR)"))
        self.assertEqual(auth.code, {"auth_code": "code"})
        with self.assertRaises(ValueError):
            pending.finish(state, "code", "cookie-one")

    def test_redirect_is_canonical(self):
        self.assertEqual(canonical_app_url("https://cardcraftai-test.streamlit.app/"), "https://cardcraftai-test.streamlit.app/")
        for invalid in ("http://example.com", "https://example.com/evil", "https://evil.com@trusted.com", "https://example.com?next=evil"):
            with self.assertRaises(ValueError):
                canonical_app_url(invalid)


if __name__ == "__main__":
    unittest.main()
