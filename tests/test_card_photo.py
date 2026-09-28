from unittest import TestCase
from unittest.mock import patch

from PIL import Image

from card_photo import prepare_card_photo, unverified_collector_numbers


class CardPhotoTests(TestCase):
    def test_photo_is_bounded_and_source_is_untouched(self):
        source = Image.new('RGB', (2400, 1200), '#777777')
        prepared = prepare_card_photo(source, max_side=800)
        self.assertEqual(source.size, (2400, 1200))
        self.assertEqual(prepared.size, (800, 400))
        self.assertEqual(prepared.mode, 'RGB')

    def test_unavailable_ocr_never_asserts_a_number(self):
        with patch.dict('sys.modules', {'pytesseract': None}):
            self.assertEqual(unverified_collector_numbers(Image.new('RGB', (400, 600))), ())

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare_card_photo(Image.new('RGB', (400, 600)), max_side=10000)
