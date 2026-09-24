import unittest

from community import _card_snapshot, _normalize_handle, _safe_https_url, _valid_handle


class CommunityHelpersTests(unittest.TestCase):
    def test_handle_normalization(self):
        self.assertEqual(_normalize_handle("  Card Crafter!  "), "card_crafter")
        self.assertEqual(_normalize_handle("Poké Master"), "pok_master")

    def test_handle_validation(self):
        self.assertTrue(_valid_handle("collector_123"))
        self.assertFalse(_valid_handle("AB"))
        self.assertFalse(_valid_handle("Bad-Handle"))

    def test_card_snapshot_only_keeps_public_card_fields(self):
        item = {
            "id": "private-row-id",
            "catalog_id": "sv3-025",
            "card_name": "Pikachu",
            "set_name": "151",
            "card_number": "025/165",
            "image_url": "https://example.com/pikachu.png",
            "condition": "Near Mint",
            "language": "English",
            "variant": "Reverse Holo",
            "notes": "private collector note",
            "quantity": 99,
        }
        snapshot = _card_snapshot(item)
        self.assertEqual(snapshot["card_name"], "Pikachu")
        self.assertEqual(snapshot["card_number"], "025/165")
        self.assertNotIn("notes", snapshot)
        self.assertNotIn("quantity", snapshot)
        self.assertNotIn("id", snapshot)

    def test_only_https_card_images_are_renderable(self):
        self.assertEqual(
            _safe_https_url("https://example.com/card.png"),
            "https://example.com/card.png",
        )
        self.assertEqual(_safe_https_url("http://example.com/card.png"), "")
        self.assertEqual(_safe_https_url("javascript:alert(1)"), "")


if __name__ == "__main__":
    unittest.main()
