import unittest

from game_cards import ABILITY, NUMBER, RARITY, ability_bonus
from game_engine import BASE_IDS, CARDS, base_id, new_game, score, variant_id


class AbilityTests(unittest.TestCase):
    def test_every_card_has_unique_catalog_number_and_localized_ability(self):
        self.assertEqual(len(CARDS), 120)
        self.assertEqual(len(set(NUMBER.values())), len(CARDS))
        self.assertEqual(set(RARITY), set(CARDS))
        for labels in ABILITY.values():
            self.assertEqual(set(labels), set(CARDS))

    def test_ten_distinct_power_levels_per_character_and_playable_decks(self):
        for character in BASE_IDS:
            editions = [variant_id(character, edition) for edition in range(1, 11)]
            self.assertEqual(len({CARDS[card][2] for card in editions}), 10)
            self.assertEqual(len({ABILITY['Português (BR)'][card][0] for card in editions}), 10)
            self.assertTrue(all(base_id(card) == character for card in editions))
        seen = set()
        for seed in range(80):
            game = new_game(seed)
            for player in game['players'].values():
                deck = player['hand'] + player['deck']
                self.assertEqual(len(deck), 12)
                self.assertEqual({base_id(card) for card in deck}, set(BASE_IDS))
                seen.update(deck)
        self.assertEqual(seen, set(CARDS))

    def test_contextual_bonus_changes_with_board(self):
        self.assertEqual(ability_bonus('root', ['root'], []), 2)
        self.assertEqual(ability_bonus('root', ['root'], ['scout']), 0)
        self.assertEqual(ability_bonus('sprout', ['sprout', 'root', 'canopy', 'scout'], []), 2)
        self.assertEqual(ability_bonus('comet', ['comet'], ['anchor']), 3)
        self.assertEqual(ability_bonus('comet', ['comet', 'scout'], ['anchor']), 0)
        self.assertEqual(ability_bonus('comet_v9', ['comet_v9'], ['anchor', 'scout']), 4)
        self.assertEqual(ability_bonus('comet_v9', ['comet_v9', 'root'], ['anchor', 'scout']), 0)

    def test_score_updates_for_both_players_as_cards_arrive(self):
        state = new_game(7)
        state['lanes']['grove']['a'] = ['root']
        initial = score(state)['grove']['a']
        state['lanes']['grove']['b'] = ['anchor']
        self.assertEqual(score(state)['grove']['a'], initial - 2)


if __name__ == '__main__':
    unittest.main()
