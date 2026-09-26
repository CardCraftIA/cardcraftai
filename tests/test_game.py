import unittest
from copy import deepcopy

from game_engine import CARDS, bot_move, legal_moves, move, new_game, redacted, score
from game_online import Conflict, _side, authenticated_id, join_match, play_match, view_match


class EngineTests(unittest.TestCase):
    def test_full_solo_match_ends_and_remains_deterministic(self):
        def run():
            state = new_game(31)
            while state['status'] == 'active':
                if state['turn'] == 'b':
                    state = bot_move(state)
                else:
                    card, lane = (legal_moves(state, 'a') or [(None, None)])[0]
                    state = move(state, 'a', card, lane)
            return state
        game = run()
        self.assertEqual(game, run())
        self.assertEqual(len(game['log']), 12)
        self.assertEqual(game['round'], 6)
        self.assertIn(game['winner'], ('a', 'b', 'draw'))

    def test_forged_actions_do_not_mutate_state(self):
        state = new_game(12)
        original = deepcopy(state)
        for side, card, lane in [('b', None, None), ('a', 'comet', 'forge'), ('a', 'not-a-card', 'forge'),
                                 ('a', state['players']['b']['hand'][0], 'invalid'), ('a', None, 'forge')]:
            with self.assertRaises(ValueError):
                move(state, side, card, lane)
        self.assertEqual(state, original)

    def test_redaction_keeps_private_cards_hidden(self):
        state = new_game(71)
        view = redacted(state, 'a')
        self.assertEqual(view['players']['a']['hand'], state['players']['a']['hand'])
        self.assertEqual(view['players']['b']['hand'], [None] * 3)
        self.assertEqual(view['players']['a']['deck'], [None] * 9)
        self.assertEqual(view['players']['b']['deck'], [None] * 9)

    def test_affinity_and_tie_break(self):
        state = new_game(1)
        state['lanes']['forge']['a'] = ['spark']
        self.assertEqual(score(state)['forge']['a'], CARDS['spark'][2] + 2)


class OnlineBoundaryTests(unittest.TestCase):
    class FakeService:
        def __init__(self, row):
            self.row = row
            self.filters = []
            self.operation = None
        def table(self, name): return self
        def select(self, columns): return self
        def update(self, payload):
            self.operation = payload
            return self
        def eq(self, key, value):
            self.filters.append((key, value))
            return self
        def limit(self, count): return self
        def execute(self):
            if self.operation is not None:
                if ('version', self.row['version']) not in self.filters:
                    return type('Response', (), {'data': []})()
                self.row.update(self.operation)
                return type('Response', (), {'data': [self.row]})()
            return type('Response', (), {'data': [self.row]})()

    def test_stranger_cannot_view_or_move(self):
        from game_online import _side
        with self.assertRaises(PermissionError):
            _side({'player_a': 'a', 'player_b': 'b'}, 'attacker')
        with self.assertRaises(PermissionError):
            authenticated_id(None, None)

    def test_join_rejects_self_and_bad_codes(self):
        class Service:
            def table(self, name): return self
            def select(self, columns): return self
            def eq(self, key, value): return self
            def limit(self, count): return self
            def execute(self): return type('Response', (), {'data': [{'id': 'match', 'player_a': 'a',
                                                                        'player_b': None, 'status': 'waiting'}]})()
        with self.assertRaises(ValueError):
            join_match(Service(), 'b', 'bad code')
        self.assertEqual(join_match(Service(), 'a', '123456789A'), 'match')

    def test_play_rejects_stale_version_and_nonparticipant(self):
        import uuid
        ident = str(uuid.uuid4())
        state = new_game(3)
        service = self.FakeService({'id': ident, 'player_a': 'a', 'player_b': 'b',
                                    'status': 'active', 'version': 4, 'state': state})
        with self.assertRaises(PermissionError):
            play_match(service, 'stranger', ident, 4)
        with self.assertRaises(Conflict):
            play_match(service, 'a', ident, 3)
        card, lane = legal_moves(state, 'a')[0]
        view = play_match(service, 'a', ident, 4, card, lane)
        self.assertEqual(service.row['version'], 5)
        self.assertEqual(view['players']['b']['hand'], [None] * 3)


if __name__ == '__main__':
    unittest.main()
