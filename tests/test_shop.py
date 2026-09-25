from unittest import TestCase
from pathlib import Path

from streamlit.testing.v1 import AppTest
from shop import ITEMS, partner_link, shop_payload, COPY, SHOP_HTML


class ShopTests(TestCase):
    def test_links_are_external_until_an_approved_affiliate_url_is_configured(self):
        plain, affiliate = partner_link('pokemon-cards', 'tcgplayer', 'Pokemon cards')
        self.assertFalse(affiliate)
        self.assertTrue(plain.startswith('https://www.tcgplayer.com/search/'))
        approved, affiliate = partner_link('pokemon-cards', 'tcgplayer', 'Pokemon cards',
                                           {'pokemon-cards:tcgplayer': 'https://www.tcgplayer.com/search/all/product?q=Pokemon&ref=approved'})
        self.assertTrue(affiliate)
        self.assertIn('ref=approved', approved)
        for bad in ('javascript:alert(1)', 'https://tcgplayer.com.evil.test/x', 'http://www.tcgplayer.com/x'):
            with self.subTest(bad=bad):
                url, is_affiliate = partner_link('pokemon-cards', 'tcgplayer', 'Pokemon cards',
                                                 {'pokemon-cards:tcgplayer': bad})
                self.assertFalse(is_affiliate)
                self.assertEqual(url, plain)

    def test_catalog_is_discovery_only_and_has_no_checkout_or_fake_prices(self):
        self.assertEqual(len(ITEMS), 12)
        self.assertTrue(all(len(item['links']) == 2 for item in shop_payload()))
        self.assertIn('não vende nem processa pagamentos', COPY['pt']['disclosure'])
        self.assertIn('localStorage', SHOP_HTML)
        self.assertNotIn('checkout', SHOP_HTML.lower())

    def test_public_shop_tab_renders_without_login_or_secrets(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=15)
        app.query_params['shop'] = '1'
        app.query_params['lang'] = 'pt'
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('html')), 1)
        self.assertFalse(app.text_input)
