import unittest

from game_adventure import action, new_encounter, targets


class QuestTests(unittest.TestCase):
    def test_movement_respects_bounds_and_does_not_mutate_previous_turn(self):
        start = new_encounter()
        moved = action(start, 'move', direction='up')
        self.assertEqual(start['position'], (2, 4))
        self.assertEqual(moved['position'], (2, 3))
        with self.assertRaises(ValueError):
            action(start, 'move', direction='down')

    def test_power_requires_range_and_recharges_on_movement(self):
        state = new_encounter('scout')
        state['enemies'][0]['position'] = (2, 2)
        state['enemies'][1]['position'] = (4, 1)
        self.assertEqual(targets(state, 'power'), [0])
        powered = action(state, 'power', target=0)
        self.assertEqual(powered['enemies'][0]['health'], 1)
        self.assertFalse(powered['power_ready'])
        with self.assertRaises(ValueError):
            action(powered, 'power', target=0)
        moved = action(powered, 'move', direction='left')
        self.assertTrue(moved['power_ready'])

    def test_defeating_last_enemy_ends_match_without_enemy_response(self):
        state = new_encounter()
        state['enemies'][0]['health'] = 0
        state['enemies'][1]['position'] = (2, 2)
        state['enemies'][1]['health'] = 2
        won = action(state, 'power', target=1)
        self.assertEqual(won['status'], 'won')
        self.assertEqual(won['health'], 8)
        with self.assertRaises(ValueError):
            action(won, 'move', direction='up')


if __name__ == '__main__':
    unittest.main()
