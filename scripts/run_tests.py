"""Run the entire suite without credentials or outbound network access."""
from pathlib import Path
import ipaddress
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

REAL_CONNECT = socket.socket.connect
REAL_CREATE_CONNECTION = socket.create_connection


def loopback_address(address):
    try:
        return isinstance(address, tuple) and ipaddress.ip_address(address[0]).is_loopback
    except ValueError:
        return False


def local_connect(sock, address):
    # Windows asyncio uses a loopback socket pair for its internal wake-up pipe.
    if sock.family == getattr(socket, 'AF_UNIX', None) or loopback_address(address):
        return REAL_CONNECT(sock, address)
    raise AssertionError('External network disabled in tests')


def local_connection(address, *args, **kwargs):
    if address[0] != 'localhost' and not loopback_address(address):
        raise AssertionError('External network disabled in tests')
    return REAL_CREATE_CONNECTION(address, *args, **kwargs)


def main():
    # Mocks in individual tests may supply responses, but accidental real I/O fails.
    with patch('socket.socket.connect', new=local_connect), \
         patch('socket.create_connection', new=local_connection), \
         patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP disabled in tests')):
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(main())
