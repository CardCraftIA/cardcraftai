import unittest

from game_cards import ABILITY, NUMBER, RARITY, ability_bonus
from game_engine import CARDS, new_game, score


class AbilityTests(unittest.TestCase):
    def test_every_card_has_unique_catalog_number_and_localized_ability(self):
        self.assertEqual(len(set(NUMBER.values())), len(CARDS))
        self.assertEqual(set(RARITY), set(CARDS))
        for labels in ABILITY.values():
            self.assertEqual(set(labels), set(CARDS))

    def test_contextual_bonus_changes_with_board(self):
        self.assertEqual(ability_bonus('root', ['root'], []), 2)
        self.assertEqual(ability_bonus('root', ['root'], ['scout']), 0)
        self.assertEqual(ability_bonus('sprout', ['sprout', 'root', 'canopy', 'scout'], []), 2)
        self.assertEqual(ability_bonus('comet', ['comet'], ['anchor']), 3)
        self.assertEqual(ability_bonus('comet', ['comet', 'scout'], ['anchor']), 0)

    def test_score_updates_for_both_players_as_cards_arrive(self):
        state = new_game(7)
        state['lanes']['grove']['a'] = ['root']
        initial = score(state)['grove']['a']
        state['lanes']['grove']['b'] = ['anchor']
        self.assertEqual(score(state)['grove']['a'], initial - 2)


if __name__ == '__main__':
    unittest.main()
