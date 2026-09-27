import unittest

from development_assistant import RepositoryReader, approved_repositories, development_reply


class FakeResponse:
    def __init__(self, value): self.value = value
    def raise_for_status(self): pass
    def json(self): return self.value


class FakeSession:
    def __init__(self): self.calls = []
    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if '/git/trees/' in url:
            return FakeResponse({'tree': [{'type': 'blob', 'path': 'README.md'},
                                          {'type': 'blob', 'path': '.env'},
                                          {'type': 'tree', 'path': 'src'}]})
        return FakeResponse({'default_branch': 'main', 'description': 'Game tools'})


class DevelopmentAssistantTests(unittest.TestCase):
    def test_repository_allowlist_precedes_every_network_request(self):
        session = FakeSession()
        reader = RepositoryReader('test-token', 'CardCraftIA/cardcraftai', session)
        with self.assertRaises(PermissionError):
            reader.inspect('other/private')
        self.assertFalse(session.calls)
        self.assertEqual(reader.inspect('CardCraftIA/cardcraftai')['files'][:1], ['README.md'])
        self.assertTrue(all(url.startswith('https://api.github.com/repos/CardCraftIA/cardcraftai') for url, _ in session.calls))

    def test_bad_repository_names_are_rejected(self):
        self.assertEqual(approved_repositories('owner/repo,https://evil.test/x,../outside'), ('owner/repo',))

    def test_ai_only_receives_inventory_and_plan_instruction(self):
        class AI:
            class interactions:
                @staticmethod
                def create(**kwargs):
                    assert 'do not claim' in kwargs['input'].lower()
                    return type('Answer', (), {'output_text': 'Inspect README, then draft a PR.'})()
        self.assertIn('draft a PR', development_reply(AI(), 'test-model', 'How do we integrate?', {'files': ['README.md']}))


if __name__ == '__main__':
    unittest.main()
