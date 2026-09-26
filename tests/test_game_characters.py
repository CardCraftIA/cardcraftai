from pathlib import Path
import unittest

from game_characters import CAST, portrait
from game_engine import CARDS
from game_localization import CARD_IDS, card_text
from game_story import STORY


class CharacterTests(unittest.TestCase):
    def test_every_playable_card_has_original_portrait_and_localized_identity(self):
        self.assertEqual(set(CARDS), set(CAST))
        self.assertEqual(set(CARDS), set(CARD_IDS))
        for card in CARDS:
            self.assertTrue(Path(portrait(card)).is_file())
            self.assertGreater(Path(portrait(card)).stat().st_size, 10_000)
            for language in STORY:
                name, description = card_text(card, language)
                self.assertIn(CAST[card][0], name)
                self.assertTrue(description)

    def test_pilot_has_six_panels_in_each_language(self):
        self.assertTrue(all(len(chapter['panels']) == 6 for chapter in STORY.values()))
