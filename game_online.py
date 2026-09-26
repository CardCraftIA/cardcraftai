"""Server-only persistence for CardCraft Arenas online matches."""
from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timezone

from game_engine import move, new_game, redacted

TABLE = 'cardcraft_game_matches'


class Conflict(ValueError):
    pass


def authenticated_id(auth_client, access_token):
    if not access_token:
        raise PermissionError('Entre na sua conta para jogar online.')
    try:
        user = auth_client.auth.get_user(access_token).user
        return str(uuid.UUID(str(user.id)))
    except (AttributeError, ValueError, TypeError):
        raise PermissionError('Sua sessão expirou. Entre novamente.') from None


def create_match(service, user_id):
    code = secrets.token_hex(5).upper()
    data = {'invite_code': code, 'player_a': user_id, 'status': 'waiting', 'version': 1}
    result = service.table(TABLE).insert(data).execute().data
    if not result:
        raise RuntimeError('Não foi possível abrir a partida.')
    return result[0]


def _by_id(service, match_id):
    try:
        match_id = str(uuid.UUID(str(match_id)))
    except ValueError:
        raise ValueError('Partida inválida.') from None
    rows = service.table(TABLE).select('*').eq('id', match_id).limit(1).execute().data or []
    if not rows:
        raise ValueError('Partida não encontrada.')
    return rows[0]


def _side(row, user_id):
    if row['player_a'] == user_id:
        return 'a'
    if row['player_b'] == user_id:
        return 'b'
    raise PermissionError('Você não participa desta partida.')


def join_match(service, user_id, code):
    code = str(code).strip().upper()
    if not re.fullmatch(r'[0-9A-F]{10}', code):
        raise ValueError('Código de convite inválido.')
    rows = service.table(TABLE).select('*').eq('invite_code', code).limit(1).execute().data or []
    if not rows:
        raise ValueError('Convite não encontrado.')
    row = rows[0]
    if row['player_a'] == user_id:
        return row['id']
    if row.get('player_b') == user_id:
        return row['id']
    if row['status'] != 'waiting' or row.get('player_b'):
        raise ValueError('Esta partida já começou.')
    state = new_game()
    saved = (service.table(TABLE).update({'player_b': user_id, 'status': 'active',
                                          'state': state, 'version': row['version'] + 1,
                                          'updated_at': datetime.now(timezone.utc).isoformat()})
             .eq('id', row['id']).eq('version', row['version']).eq('status', 'waiting')
             .is_('player_b', 'null').select('id,version').execute().data)
    if not saved:
        raise Conflict('Outro jogador entrou primeiro. Atualize a partida.')
    return row['id']


def view_match(service, user_id, match_id):
    row = _by_id(service, match_id)
    side = _side(row, user_id)
    return {'id': row['id'], 'code': row['invite_code'], 'status': row['status'],
            'side': side, 'version': row['version'],
            'state': redacted(row['state'], side) if row['status'] != 'waiting' else None}


def play_match(service, user_id, match_id, expected_version, card=None, lane=None):
    row = _by_id(service, match_id)
    side = _side(row, user_id)
    if row['status'] != 'active':
        raise ValueError('A partida ainda não está ativa.')
    if row['version'] != expected_version:
        raise Conflict('A partida mudou. Atualize antes de jogar.')
    next_state = move(row['state'], side, card, lane)
    saved = (service.table(TABLE).update({'state': next_state, 'status': next_state['status'],
                                          'version': expected_version + 1,
                                          'updated_at': datetime.now(timezone.utc).isoformat()})
             .eq('id', row['id']).eq('version', expected_version).eq('status', 'active')
             .select('id,version').execute().data)
    if not saved:
        raise Conflict('Outra jogada chegou antes. Atualize a partida.')
    return redacted(next_state, side)


def recent_matches(service, user_id):
    """Only return room identifiers for the authenticated participant."""
    rows = (service.table(TABLE).select('id,invite_code,status,updated_at')
            .or_(f'player_a.eq.{user_id},player_b.eq.{user_id}')
            .order('updated_at', desc=True).limit(8).execute().data or [])
    return rows
