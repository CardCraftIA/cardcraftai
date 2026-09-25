from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from commercial import admin_ids, summarize, commercial_insights
from shop import tracked_path, resolve_tracked, shop_payload
from shop_tracking import process_outbound


class IntelligenceTests(TestCase):
    def test_signed_link_and_fixed_marketplace_target(self):
        path = tracked_path('pokemon-cards', 'tcgplayer', 'newsletter', 'Pikachu 58', 'server-only-key')
        from urllib.parse import parse_qs
        params = {key: value[0] for key, value in parse_qs(path[1:]).items()}
        result = resolve_tracked(params, 'server-only-key')
        self.assertEqual(result[1]['campaign'], 'newsletter')
        self.assertIn('Pikachu+58', result[0])
        for changed in ({**params, 'c': 'other'}, {**params, 'out': 'pokemon-cards.amazon_br'},
                        {**params, 'sig': '0' * 64}):
            self.assertIsNone(resolve_tracked(changed, 'server-only-key'))
        self.assertRaises(ValueError, tracked_path, 'pokemon-cards', 'tcgplayer', 'bad campaign', '', 'server-only-key')

    def test_shop_links_are_internal_when_tracking_is_available(self):
        links = shop_payload(tracking_secret='server-only-key')[0]['links']
        self.assertTrue(all(link['url'].startswith('?out=') for link in links))
        self.assertFalse(any(link['affiliate'] for link in links))

    def test_click_is_recorded_without_visitor_identity_and_redirects(self):
        from urllib.parse import parse_qs
        path = tracked_path('magic-cards', 'amazon_br', secret='server-only-key')
        params = {key: value[0] for key, value in parse_qs(path[1:]).items()}
        st, client = Mock(), Mock()
        self.assertTrue(process_outbound(st, params, 'server-only-key', 'https://test.supabase.co',
                                         'server-key', lambda *_: client))
        event = client.table.return_value.insert.call_args.args[0]
        self.assertEqual(set(event), {'item_id', 'partner', 'campaign', 'is_affiliate'})
        self.assertNotIn('user_id', event)
        st.link_button.assert_called_once()
        self.assertFalse(process_outbound(st, {**params, 'sig': 'invalid'}, 'server-only-key',
                                          'https://test.supabase.co', 'server-key', lambda *_: client))
        self.assertEqual(client.table.return_value.insert.call_count, 1)

    def test_analytics_counts_clicks_only_and_admin_is_explicit(self):
        daily, items, partners, campaigns = summarize([
            {'occurred_at': '2026-09-25T12:00:00Z', 'item_id': 'pokemon-cards', 'partner': 'tcgplayer', 'campaign': 'shop'},
            {'occurred_at': '2026-09-25T13:00:00Z', 'item_id': 'pokemon-cards', 'partner': 'tcgplayer', 'campaign': 'shop'},
        ])
        self.assertEqual(daily['2026-09-25'], 2)
        self.assertEqual(items['pokemon-cards'], 2)
        self.assertEqual(partners['tcgplayer'], 2)
        from datetime import date
        recent, prior, change, top_item, top_partner = commercial_insights(
            {'2026-09-25': 2, '2026-09-17': 4}, items, partners, date(2026, 9, 25))
        self.assertEqual((recent, prior, change), (2, 4, -50))
        self.assertEqual(admin_ids('owner-id, second-id'), {'owner-id', 'second-id'})
        self.assertEqual(admin_ids(None), set())
        sql = next((Path(__file__).resolve().parents[1] / 'supabase/migrations').glob('*shop_outbound_analytics.sql')).read_text()
        self.assertIn('enable row level security', sql)
        self.assertIn('revoke all on public.shop_outbound_events from anon, authenticated', sql)

    def test_public_redirect_records_event_without_app_login(self):
        from urllib.parse import parse_qs
        path = tracked_path('pokemon-cards', 'tcgplayer', secret='fixture-signing-key')
        params = {key: value[0] for key, value in parse_qs(path[1:]).items()}
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=15)
        app.query_params.update(params)
        fake = Mock()
        with patch('streamlit.secrets', {'SHOP_LINK_SIGNING_KEY': 'fixture-signing-key',
                                         'SUPABASE_SERVICE_ROLE_KEY': 'fixture-service-key',
                                         'SUPABASE_URL': 'https://fixture.invalid'}), \
             patch('supabase.create_client', return_value=fake):
            app.run()
        self.assertFalse(app.exception)
        self.assertFalse(app.text_input)
        self.assertEqual(fake.table.return_value.insert.call_count, 1)
        self.assertEqual(fake.table.return_value.insert.call_args.args[0]['item_id'], 'pokemon-cards')
