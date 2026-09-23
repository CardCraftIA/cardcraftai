import unittest
from copy import deepcopy
from search_utils import normalize_search, search_collection, suggest_collection_names, rank_names


class SearchTests(unittest.TestCase):
    def test_public_and_private_candidates_stay_separate(self):
        self.assertEqual(rank_names('Picachu', ['Pikachu', 'Pichu']), ['Pikachu', 'Pichu'])
        self.assertEqual(suggest_collection_names([{'card_name': 'Pichu'}], 'Picachu'), ['Pichu'])
        self.assertEqual(suggest_collection_names([], 'Picachu'), [])

    def setUp(self):
        self.item = dict(card_name='Pikachu', set_name='Pokémon Base', card_number='SM211/248',
                         condition='Near Mint', language='Português (Brasil)', variant='Edição-antiga',
                         notes='secret-only-notes')

    def test_exact_case_and_whitespace(self):
        for query in ('Pikachu', 'pikachu', '  PIKACHU  ', 'Near   Mint'):
            self.assertEqual(search_collection([self.item], query), [self.item])

    def test_all_six_fields_and_legacy_values(self):
        for query in ('Pikachu', 'pokemon base', 'SM211/248', 'near mint', 'portugues brasil', 'edicao antiga'):
            self.assertEqual(search_collection([self.item], query), [self.item])

    def test_accents_unicode_and_symbols(self):
        self.assertEqual(normalize_search('ＰＯＫÉＭＯＮ'), 'pokemon')
        self.assertEqual(normalize_search('Poke\u0301mon'), 'pokemon')
        self.assertNotEqual(normalize_search('Nidoran♀'), normalize_search('Nidoran♂'))
        self.assertNotEqual(normalize_search('ガ'), normalize_search('カ'))

    def test_number_keeps_prefix_and_denominator(self):
        self.assertEqual(search_collection([self.item], '#SM211/248'), [self.item])
        for query in ('SM211/249', 'M211/248'):
            self.assertEqual(search_collection([self.item], query), [])

    def test_notes_are_excluded_and_records_unchanged(self):
        original = deepcopy(self.item)
        self.assertEqual(search_collection([self.item], 'secret-only-notes'), [])
        self.assertEqual(suggest_collection_names([self.item], 'secret-only-notes'), [])
        self.assertEqual(self.item, original)

    def test_exact_precedes_substring(self):
        extended = dict(self.item, card_name='Pikachu V')
        self.assertEqual(search_collection([extended, self.item], 'Pikachu'), [self.item, extended])
        self.assertEqual(suggest_collection_names([self.item], 'Pika'), [])

    def test_typos_suggest_without_matching(self):
        for query in ('Picachu', 'Pikacu', 'Pikatchu'):
            self.assertEqual(search_collection([self.item], query), [])
            self.assertEqual(suggest_collection_names([self.item], query), ['Pikachu'])

    def test_low_similarity_and_short_query(self):
        for query in ('zzzzzz', 'Pi'):
            self.assertEqual(suggest_collection_names([self.item], query), [])

    def test_suggestions_deduplicate_and_limit(self):
        items = [dict(self.item, card_name='Pikachu' + suffix) for suffix in ('', ' A', ' B', ' C', ' D', ' E')]
        suggestions = suggest_collection_names(items + items, 'Pikacu')
        self.assertEqual(len(suggestions), 5)
        self.assertEqual(len(set(suggestions)), 5)

    def test_gender_is_not_corrected_to_another_identity(self):
        item = dict(self.item, card_name='Nidoran♂')
        self.assertEqual(suggest_collection_names([item], 'Nidoran♀'), [])
