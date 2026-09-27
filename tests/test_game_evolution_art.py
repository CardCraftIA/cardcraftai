import unittest
from xml.etree import ElementTree
from hashlib import sha256
from game_characters import ART_DIR

from game_engine import BASE_IDS, CARDS, variant_id
from game_evolution_art import evolution_svg


class EvolutionArtTests(unittest.TestCase):
    def test_all_120_cards_have_distinct_power_art_with_embedded_portraits(self):
        self.assertEqual(len(CARDS), 120)
        for character in BASE_IDS:
            scenes = [evolution_svg(variant_id(character, edition)) for edition in range(1, 11)]
            self.assertEqual(len(set(scenes)), 10)
            poses = [(ART_DIR / 'poses' / f'{variant_id(character, edition)}.jpg').read_bytes()
                     for edition in range(2, 11)]
            self.assertEqual(len({sha256(pose).digest() for pose in poses}), 9)
            for scene in scenes:
                root = ElementTree.fromstring(scene)
                self.assertTrue(root.tag.endswith('svg'))
                self.assertIn('data:image/jpeg;base64,', scene)
                self.assertNotIn('<script', scene)


if __name__ == '__main__':
    unittest.main()
