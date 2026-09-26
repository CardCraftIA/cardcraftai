import unittest
from xml.etree import ElementTree

from game_art import AFFINITY, SCENES, card_svg
from game_engine import ARENAS, CARDS
from game_localization import ARENA_NAMES, CARD_DESCRIPTIONS, CARD_IDS, CARD_NAMES, UI, card_text, error_text, ui


class GameVisualTests(unittest.TestCase):
    def test_every_game_card_has_valid_self_contained_art(self):
        self.assertEqual(set(CARDS), set(SCENES))
        self.assertEqual(set(CARDS), set(AFFINITY))
        for card in CARDS:
            art = card_svg(card, card)
            root = ElementTree.fromstring(art)
            self.assertTrue(root.tag.endswith('svg'))
            self.assertNotIn('<script', art)
            self.assertNotIn('http://', art.replace('http://www.w3.org/2000/svg', ''))

    def test_every_language_has_all_cards_arenas_and_labels(self):
        self.assertEqual(set(CARDS), set(CARD_IDS))
        expected = set(UI['Português (BR)'])
        for language in CARD_NAMES:
            self.assertEqual(len(CARD_NAMES[language]), len(CARDS))
            self.assertEqual(len(CARD_DESCRIPTIONS[language]), len(CARDS))
            self.assertEqual(set(ARENA_NAMES[language]), {lane for lane, _, _ in ARENAS})
            self.assertEqual(set(UI[language]), expected)
            self.assertTrue(card_text('comet', language)[0])
            self.assertIn('2', ui(language, 'round', n=2))
        self.assertEqual(error_text(ValueError('Não é sua vez.'), 'English'), 'Not your turn.')


if __name__ == '__main__':
    unittest.main()
