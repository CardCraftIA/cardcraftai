import importlib.util
from pathlib import Path
import unittest
import hashlib
import json
import tempfile
from unittest.mock import Mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ingest_catalog_snapshot.py"
SPEC = importlib.util.spec_from_file_location("ingest_catalog_snapshot", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CatalogCoreTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "schema_version": 1,
            "provider": "tcgdex",
            "source_key": "base1-58",
            "game_slug": "pokemon",
            "local_id": "58",
            "set": {
                "source_id": "base1",
                "code": "BS",
                "names": {"en": "Base Set", "pt": "Coleção Básica"},
                "series_source_id": "base",
                "series_names": {"en": "Base"},
                "release_date": "1999-01-09",
                "card_count": {"official": 102},
                "third_party": {"tcgplayer": 604},
                "attributes": {},
            },
            "card": {
                "category": "Pokemon",
                "rarity": "Common",
                "illustrator": "Mitsuhiro Arita",
                "hp": 40,
                "dex_ids": [25],
                "attributes": {"types": ["Lightning"], "stage": "Basic"},
            },
            "localizations": [
                {
                    "language": "en",
                    "name": "Pikachu",
                    "set_name": "Base Set",
                    "series_name": "Base",
                    "description": "Mouse Pokémon",
                    "image_base_url": "https://assets.tcgdex.net/en/base/base1/58",
                    "image_small_url": "https://assets.tcgdex.net/en/base/base1/58/low.webp",
                    "image_url": "https://assets.tcgdex.net/en/base/base1/58/high.webp",
                }
            ],
            "variants": [
                {
                    "variant_key": "normal:unlimited:standard:abcdef123456",
                    "variant_type": "normal",
                    "subtype": "unlimited",
                    "size": "standard",
                    "stamps": [],
                    "external_ids": {"tcgplayer": 42402},
                    "attributes": {},
                }
            ],
        }

    def test_normalize_search_folds_latin_accents_but_keeps_gender_symbols(self):
        self.assertEqual(module.normalize_search("  PokÉMON  "), "pokemon")
        self.assertNotEqual(module.normalize_search("Nidoran♀"), module.normalize_search("Nidoran♂"))

    def test_canonical_keys_are_stable(self):
        self.assertEqual(module.canonical_set_key(self.record), "cc:pokemon:set:base1")
        self.assertEqual(module.canonical_card_key(self.record), "cc:pokemon:card:base1-58")

    def test_set_row_keeps_localized_names_as_provenance(self):
        row = module.build_set_row(self.record)
        self.assertEqual(row["name"], "Base Set")
        self.assertEqual(row["code"], "BS")
        self.assertEqual(row["printed_total"], 102)
        self.assertEqual(row["attributes"]["localized_names"]["pt"], "Coleção Básica")

    def test_card_row_does_not_flatten_variant_identity(self):
        row = module.build_card_row(self.record, "set-uuid")
        self.assertEqual(row["collector_number"], "58")
        self.assertEqual(row["rarity"], "Common")
        self.assertEqual(row["dex_ids"], [25])
        self.assertEqual(row["set_id"], "set-uuid")
        self.assertNotIn("variants", row["attributes"])

    def test_localization_and_variant_are_separate_entities(self):
        localizations = module.build_localization_rows(self.record, "card-uuid")
        variants = module.build_variant_rows(self.record, "card-uuid")
        self.assertEqual(localizations[0]["name"], "Pikachu")
        self.assertEqual(localizations[0]["language"], "en")
        self.assertEqual(variants[0]["subtype"], "unlimited")
        self.assertEqual(variants[0]["external_ids"]["tcgplayer"], 42402)

    def test_quality_rewards_rich_records(self):
        self.assertGreaterEqual(module.data_quality(self.record), 90)

    def test_snapshot_requires_matching_checksum_revision_and_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / 'cards.jsonl'
            snapshot.write_text(json.dumps(self.record) + '\n', encoding='utf-8')
            (root / 'source-revision.txt').write_text('a' * 40 + '\n', encoding='utf-8')
            (root / 'TCGDEX-LICENSE.txt').write_text('MIT License\n', encoding='utf-8')
            digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
            (root / 'SHA256SUMS').write_text(f'{digest}  {snapshot.name}\n', encoding='utf-8')
            self.assertEqual(module.verify_snapshot(snapshot, require_provenance=True)['sha256'], digest)
            snapshot.write_text(snapshot.read_text() + 'tampered\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                module.verify_snapshot(snapshot, require_provenance=True)

    def test_import_rejects_reviewed_canonical_record_before_writing(self):
        client = Mock()
        client.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
            {'canonical_key': module.canonical_card_key(self.record),
             'verification_status': 'community_verified', 'source_count': 2}
        ]
        with self.assertRaisesRegex(ValueError, 'requires review'):
            module.ingest_batch(client, 1, [self.record], 10)
        client.table.return_value.upsert.assert_not_called()


if __name__ == "__main__":
    unittest.main()
