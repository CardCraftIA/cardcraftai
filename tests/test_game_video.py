import unittest

from game_video import LABELS, game_html


class VideoGameTests(unittest.TestCase):
    def test_each_language_embeds_safe_game_configuration(self):
        for language, labels in LABELS.items():
            with self.subTest(language=language):
                html = game_html(language)
                self.assertIn(labels['title'], html)
                self.assertNotIn('/*CONFIG_JSON*/', html)
                self.assertIn('requestAnimationFrame(loop)', html)
                self.assertIn('data-key="ArrowUp"', html)


if __name__ == '__main__':
    unittest.main()
