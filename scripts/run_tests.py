"""Run the entire suite without credentials or outbound network access."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True


def main():
    # Mocks in individual tests may supply responses, but accidental real I/O fails.
    with patch('socket.socket.connect', side_effect=AssertionError('Network disabled in tests')), \
         patch('socket.create_connection', side_effect=AssertionError('Network disabled in tests')), \
         patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP disabled in tests')):
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(main())
