"""Fail-closed session handling. Only Supabase Auth responses grant access."""


def clear_identity(state, status='signed_out'):
    for key in list(state):
        if key.startswith('collection_'):
            del state[key]
    for key in ('resultado_analise', 'resultado_tipo', 'analysis_run_id_atual',
                'analysis_request_id_atual', 'analysis_tipo_atual', 'checkout_preference',
                'catalogo_selecionada_foto', 'catalogo_selecionada_nome'):
        state[key] = None
    state['catalogo_resultados_nome'] = []
    state['analysis_in_progress'] = False
    for key in ('access_token', 'refresh_token', 'user_id', 'user_email'):
        state[key] = None
    state['email_confirmado'] = False
    state['auth_status'] = status


def confirmed_email(user):
    # `confirmed_at` alone can refer to phone confirmation, not email.
    return bool(user and getattr(user, 'email', None) and getattr(user, 'email_confirmed_at', None))


def accept_session(state, response):
    user = getattr(response, 'user', None)
    session = getattr(response, 'session', None)
    if not confirmed_email(user) or not session or not getattr(user, 'id', None):
        clear_identity(state, 'email_unconfirmed' if user and not confirmed_email(user) else 'error')
        return False
    access = getattr(session, 'access_token', None)
    refresh = getattr(session, 'refresh_token', None)
    if not access or not refresh:
        clear_identity(state, 'error')
        return False
    if state.get('user_id') != user.id:
        clear_identity(state)
    state.update(access_token=access, refresh_token=refresh, user_id=user.id,
                 user_email=user.email, email_confirmado=True, auth_status='authenticated')
    return True


def auth_error_status(error):
    code = getattr(error, 'code', '')
    if code == 'email_not_confirmed':
        return 'email_unconfirmed'
    if code in {'refresh_token_not_found', 'refresh_token_already_used', 'session_expired',
                'session_not_found', 'bad_jwt', 'invalid_jwt'}:
        return 'expired'
    return 'error'


def restore_session(client, state):
    access, refresh = state.get('access_token'), state.get('refresh_token')
    if not access and not refresh:
        clear_identity(state, state.get('auth_status', 'signed_out'))
        return False
    if not access or not refresh:
        clear_identity(state, 'expired')
        return False
    try:
        return accept_session(state, client.auth.set_session(access, refresh))
    except Exception as error:
        clear_identity(state, auth_error_status(error))
        return False
