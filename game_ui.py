"""Playable CardCraft Arenas solo and private online rooms."""
from __future__ import annotations

from html import escape

from game_engine import ARENAS, CARDS, bot_move, legal_moves, move, new_game, score
from game_art import card_svg
from game_localization import arena_text, card_text, error_text, ui
from game_online import Conflict, authenticated_id, create_match, join_match, play_match, recent_matches, view_match

WORDS = {
    'Português (BR)': ('🎮 Arena CardCraft', 'Solo contra o bot', 'Online com convite', 'Nova partida',
                       'Criar sala', 'Entrar na sala', 'Código de convite', 'Jogar carta', 'Passar',
                       'Sua mão', 'Sua vez', 'Aguardando o adversário', 'Você venceu!', 'Oponente venceu.', 'Empate!',
                       'Copie o código e envie a outra pessoa. Ambos precisam estar logados.', 'Sair da sala', 'Atualizar partida'),
    'English': ('🎮 CardCraft Arena', 'Solo versus bot', 'Online by invitation', 'New match',
                'Create room', 'Join room', 'Invitation code', 'Play card', 'Pass',
                'Your hand', 'Your turn', 'Waiting for opponent', 'You won!', 'Opponent won.', 'Draw!',
                'Share this code with another signed-in player.', 'Leave room', 'Refresh match'),
    'Español': ('🎮 Arena CardCraft', 'Solo contra bot', 'Online con invitación', 'Nueva partida',
                 'Crear sala', 'Entrar en sala', 'Código de invitación', 'Jugar carta', 'Pasar',
                 'Tu mano', 'Tu turno', 'Esperando rival', '¡Ganaste!', 'Ganó el rival.', '¡Empate!',
                 'Comparte el código con otra persona que haya iniciado sesión.', 'Salir de la sala', 'Actualizar partida'),
    '日本語': ('🎮 CardCraftアリーナ', 'ボットと対戦', '招待で対人戦', '新しい対戦',
             '部屋を作成', '部屋に参加', '招待コード', 'カードを出す', 'パス',
             '手札', 'あなたの番', '相手を待っています', '勝利！', '相手の勝利', '引き分け',
             'ログイン済みの友達に招待コードを共有してください。', '退出', '更新'),
}

STYLE = """<style>
.cc-arena{background:linear-gradient(135deg,#182a43,#171b35);border:1px solid #394766;border-radius:20px;padding:1rem 1.3rem;margin:.35rem 0 1rem;box-shadow:0 16px 36px #0002}
.cc-arena strong{font-size:1.2rem;color:#f7f2ff}.cc-arena p{color:#afc0d7;margin:.4rem 0}
.cc-card{background:linear-gradient(150deg,#352b64,#162e49);border:1px solid #7666a8;border-radius:16px;padding:.8rem;min-height:7rem;margin:.35rem 0;color:#e9e9ff}
.cc-card b{color:white}.cc-card small{color:#b4d3ea}
</style>"""

RULES = {
    'Português (BR)': ('Seis rodadas · três arenas · uma carta por rodada · vença duas arenas. Cartas originais do CardCraftAI.',
                       '📖 Como jogar', 'A energia cresce a cada rodada. Escolha uma carta da mão e uma arena. '
                       'Uma carta com afinidade pela arena recebe +2 de força. Cada pessoa joga uma carta ou passa por rodada. '
                       'Após seis rodadas, vence quem liderar mais arenas; em empate, vale a força total. '
                       'Estas cartas são peças digitais originais, não cartas oficiais dos TCGs presentes no catálogo. Jogo gratuito, sem créditos ou compras.'),
    'English': ('Six rounds · three arenas · one card per round · win two arenas. Original CardCraftAI cards.',
                '📖 How to play', 'Your energy grows each round. Choose a card from your hand and an arena. '
                'A matching arena adds +2 power. Each player plays one card or passes per round. '
                'After six rounds, win the most arenas; ties use total power. '
                'These are original digital game pieces, not official cards from the TCG catalog. Free game, with no credits or purchases.'),
    'Español': ('Seis rondas · tres arenas · una carta por ronda · gana dos arenas. Cartas originales de CardCraftAI.',
                 '📖 Cómo jugar', 'La energía aumenta cada ronda. Elige una carta de tu mano y una arena. '
                 'La afinidad de arena añade +2 de fuerza. Cada persona juega una carta o pasa por ronda. '
                 'Tras seis rondas, gana quien domine más arenas; los empates usan la fuerza total. '
                 'Estas cartas digitales son originales; no son cartas oficiales del catálogo TCG. Gratis, sin créditos ni compras.'),
    '日本語': ('6ラウンド・3つのアリーナ・毎ラウンド1枚。2つのアリーナを取ろう。CardCraftAI独自のカードです。',
             '📖 遊び方', 'ラウンドごとにエネルギーが増えます。手札とアリーナを選んでください。'
             '得意なアリーナではパワーが2増えます。各プレイヤーは毎ラウンド1枚出すかパスします。'
             '6ラウンド後、勝ったアリーナが多い方が勝利。同数なら合計パワーで決着します。'
             'このカードは独自のデジタルゲーム用で、TCGカタログの公式カードではありません。無料で遊べます。'),
}


def _card_name(card, language):
    name, _ = card_text(card, language)
    _, cost, power, affinity, _ = CARDS[card]
    return f'{name} · ⚡{cost} · ✦{power}' + (' · ' + next(icon for key, _, icon in ARENAS if key == affinity) if affinity else '')


def _board(st, state, side, labels, prefix, submit, language):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.progress(min(state['round'], 6) / 6, text=ui(language, 'round', n=state['round']))
    totals = score(state)
    columns = st.columns(3)
    for column, (lane, _, icon) in zip(columns, ARENAS):
        ours, theirs = totals[lane][side], totals[lane]['b' if side == 'a' else 'a']
        with column:
            played = state['lanes'][lane][side]
            rival = state['lanes'][lane]['b' if side == 'a' else 'a']
            title = arena_text(lane, language)
            st.markdown(f'<div class="cc-arena"><strong>{icon} {escape(title)}</strong>'
                        f'<p>{escape(ui(language, "score", you=ours, opponent=theirs))}</p></div>', unsafe_allow_html=True)
            if played:
                st.caption(ui(language, 'your_cards'))
                st.image([card_svg(card, card_text(card, language)[0]) for card in played], width=88)
            if rival:
                st.caption(ui(language, 'opponent_cards'))
                st.image([card_svg(card, card_text(card, language)[0]) for card in rival], width=88)
    if state['status'] == 'finished':
        winner = state['winner']
        st.success(labels[12] if winner == side else labels[14] if winner == 'draw' else labels[13])
        st.info(ui(language, 'learned'))
        return
    if state['turn'] != side:
        st.info(labels[11])
        return
    st.subheader(labels[9])
    choices = sorted(set(card for card, _ in legal_moves(state, side)))
    hand = state['players'][side]['hand']
    cards = st.columns(min(3, max(1, len(hand))))
    for index, card in enumerate(hand):
        name, description = card_text(card, language)
        _, cost, power, affinity, _ = CARDS[card]
        with cards[index % len(cards)]:
            st.image(card_svg(card, name), width='stretch')
            st.markdown(f'<div class="cc-card"><b>{escape(name)}</b><br>⚡ {cost} · ✦ {power}'
                        f'<br><small>{escape(description)}</small></div>', unsafe_allow_html=True)
    if choices:
        chosen = st.selectbox(ui(language, 'card'), choices, format_func=lambda card: _card_name(card, language), key=prefix + '_card')
        lanes = [lane for card, lane in legal_moves(state, side) if card == chosen]
        destination = st.selectbox(ui(language, 'arena'), lanes, format_func=lambda lane: next(icon + ' ' + arena_text(lane, language) for key, _, icon in ARENAS if key == lane), key=prefix + '_lane')
        if st.button(labels[7], key=prefix + '_play', type='primary'):
            submit(chosen, destination)
            st.rerun()
    if st.button(labels[8], key=prefix + '_pass'):
        submit(None, None)
        st.rerun()


def render_solo(st, language='Português (BR)', guest=False):
    labels = WORDS.get(language, WORDS['English'])
    intro, help_title, instructions = RULES.get(language, RULES['English'])
    st.header(labels[0])
    st.caption(intro)
    with st.expander(help_title, expanded=False):
        st.write(instructions)
    if guest:
        st.info(ui(language, 'demo'))
        st.markdown(f'[{ui(language, "sign_in")}](./)')
    key = 'cardcraft_solo_game'
    if key not in st.session_state or st.button(labels[3], key='new_cardcraft_solo'):
        st.session_state[key] = new_game()
    state = st.session_state[key]
    def solo_submit(card, lane):
        next_state = move(st.session_state[key], 'a', card, lane)
        while next_state['status'] == 'active' and next_state['turn'] == 'b':
            next_state = bot_move(next_state)
        st.session_state[key] = next_state
    _board(st, state, 'a', labels, 'solo', solo_submit, language)


def render_game(st, auth_client, service, access_token, language='Português (BR)'):
    labels = WORDS.get(language, WORDS['English'])
    st.header(labels[0])
    st.caption(RULES.get(language, RULES['English'])[0])
    st.markdown(f'[{ui(language, "share")}](?arena=1)')
    solo_tab, online_tab = st.tabs((labels[1], labels[2]))
    with solo_tab:
        render_solo(st, language)
    with online_tab:
        try:
            user_id = authenticated_id(auth_client, access_token)
        except PermissionError as error:
            st.error(error_text(error, language))
            return
        match_key = 'cardcraft_online_match_' + user_id
        if not st.session_state.get(match_key):
            try:
                past = recent_matches(service, user_id)
                for old in past:
                    if old['status'] in ('waiting', 'active') and st.button('↩ ' + old['invite_code'], key='resume_' + old['id']):
                        st.session_state[match_key] = old['id']
                        st.rerun()
            except Exception:
                st.caption(ui(language, 'previous_unavailable'))
            left, right = st.columns(2)
            with left:
                if st.button(labels[4], key='game_create'):
                    try:
                        st.session_state[match_key] = create_match(service, user_id)['id']
                        st.rerun()
                    except Exception:
                        st.error(ui(language, 'create_error'))
            with right:
                code = st.text_input(labels[6], max_chars=10, key='game_join_code')
                if st.button(labels[5], key='game_join'):
                    try:
                        st.session_state[match_key] = join_match(service, user_id, code)
                        st.rerun()
                    except (ValueError, Conflict) as error:
                        st.warning(error_text(error, language))
                    except Exception:
                        st.error(ui(language, 'join_error'))
            return
        if st.button(labels[16], key='game_leave'):
            st.session_state.pop(match_key, None)
            st.rerun()

        @st.fragment(run_every='4s')
        def live_match():
            try:
                # Recheck signed-in identity before every privileged read/write.
                current_id = authenticated_id(auth_client, access_token)
                match = view_match(service, current_id, st.session_state[match_key])
                if match['status'] == 'waiting':
                    st.info(labels[11])
                    st.code(match['code'])
                    st.caption(labels[15])
                    return
                st.caption(ui(language, 'invite') + ': ' + match['code'])
                def online_submit(card, lane):
                    try:
                        play_match(service, current_id, match['id'], match['version'], card, lane)
                    except (ValueError, Conflict) as error:
                        st.warning(error_text(error, language))
                    except Exception:
                        st.error(ui(language, 'save_error'))
                _board(st, match['state'], match['side'], labels, 'online_' + match['id'], online_submit, language)
            except (ValueError, PermissionError) as error:
                st.warning(error_text(error, language))
            except Exception:
                st.error(ui(language, 'load_error'))
        live_match()
