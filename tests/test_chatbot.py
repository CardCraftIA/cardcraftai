from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import chatbot


class ChatbotTests(TestCase):
    def test_local_exact_match_answers_without_external_or_ai(self):
        client = Mock()
        client.rpc.return_value.execute.return_value.data = [{
            'card_id': 'card-1', 'card_name': 'Pikachu', 'set_name': 'Base Set',
            'collector_number': '58', 'rarity': 'Common', 'illustrator': 'Arita',
            'source_count': 1,
        }]
        client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
            {'category': 'Pokemon', 'hp': 40}]
        external = Mock()
        result = chatbot.answer('What is its rarity?', 'Pikachu', None, client, 'owner-1', 'English', external)
        self.assertIn('Base Set', result['text'])
        self.assertIn('Common', result['text'])
        self.assertEqual(result['source'], 'CardCraft catalog')
        external.assert_not_called()
        self.assertNotIn('needs_ai', result)

    def test_ambiguous_edition_is_never_silently_chosen(self):
        client = Mock()
        client.rpc.return_value.execute.return_value.data = [
            {'card_id': 'a', 'card_name': 'Pikachu', 'set_name': 'Base Set', 'collector_number': '58'},
            {'card_id': 'b', 'card_name': 'Pikachu', 'set_name': 'Jungle', 'collector_number': '60'},
        ]
        result = chatbot.answer('Tell me about this card', 'Pikachu', None, client, 'owner-1', 'English')
        self.assertIn('Several editions', result['text'])
        client.table.assert_not_called()

    def test_set_and_number_resolve_edition(self):
        client = Mock()
        client.rpc.return_value.execute.return_value.data = [
            {'card_id': 'a', 'card_name': 'Pikachu', 'set_name': 'Base Set', 'collector_number': '58', 'rarity': 'Common', 'illustrator': ''},
            {'card_id': 'b', 'card_name': 'Pikachu', 'set_name': 'Jungle', 'collector_number': '60', 'rarity': 'Common', 'illustrator': ''},
        ]
        client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
        result = chatbot.answer('Tell me about this card', 'Pikachu', None, client, 'owner-1', 'English',
                                set_name='Base Set', card_number='58')
        self.assertIn('Base Set', result['text'])
        self.assertNotIn('Several editions', result['text'])

    def test_private_collection_is_owner_filtered_and_never_sent_to_ai(self):
        client = Mock()
        with patch('chatbot.load_collection_items', return_value=[{
            'catalog_id': 'a', 'quantity': 2, 'set_name': 'Base Set', 'wishlist': False,
            'card_name': 'Pikachu', 'card_number': '58', 'notes': 'private',
        }]) as load:
            result = chatbot.answer('How many cards in my collection?', '', None, client, 'owner-1', 'English')
            load.assert_called_once_with(client, 'owner-1')
            self.assertIn('2 copies', result['text'])
            self.assertNotIn('private', result['text'])
            self.assertNotIn('needs_ai', result)

    def test_value_and_best_price_never_use_ai_or_invent_amounts(self):
        client = Mock()
        with patch('chatbot.load_collection_items', return_value=[]):
            value = chatbot.answer('Value of my collection?', '', None, client, 'owner-1', 'English')
        self.assertIn('reliable total value is unavailable', value['text'])
        self.assertNotIn('needs_ai', value)
        with patch('chatbot.lookup_local', return_value=[]):
            best = chatbot.answer('Where to buy at the best price?', 'Pikachu', None, client, 'owner-1', 'English')
        self.assertIn('cannot check live inventory', best['text'])
        self.assertEqual(len(best['links']), 2)
        self.assertNotIn('needs_ai', best)

    def test_dated_market_reference_excludes_stale_and_undated_values(self):
        now = datetime.now(timezone.utc).isoformat()
        stale = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        card = {'source': 'external', 'tcgplayer': {'updatedAt': now,
                'prices': {'normal': {'market': 12.50}, 'holofoil': {'market': None}}},
                'cardmarket': {'updatedAt': stale, 'prices': {'trendPrice': 99}}}
        refs = chatbot.reference_prices(card)
        self.assertEqual(len(refs), 1)
        self.assertIn('USD 12.50', refs[0])
        self.assertNotIn('Cardmarket', refs[0])

    def test_gemini_general_only_and_no_private_context(self):
        ai = Mock()
        ai.interactions.create.return_value = SimpleNamespace(output_text='A general explanation')
        self.assertEqual(chatbot.ask_ai(ai, 'test-model', 'What is holo?', 'English'), 'A general explanation')
        prompt = ai.interactions.create.call_args.kwargs['input']
        self.assertIn('Do not claim access to a live catalog', prompt)
        self.assertNotIn('private notes', prompt)
