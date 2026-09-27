"""Small solo tactics encounter in the original Nacarim world."""
from copy import deepcopy

from game_characters import CAST

SIZE = 5
HEROES = ('spark', 'anchor', 'sprout', 'scout')
POWERS = {
    'spark': ('Chama da Forja', 2, 3),
    'anchor': ('Onda da Maré', 2, 3),
    'sprout': ('Raízes do Bosque', 2, 3),
    'scout': ('Luz Errante', 3, 2),
}
POWER_NAMES = {
    'English': ('Forge Flame', 'Tidal Wave', 'Grove Roots', 'Wanderer Light'),
    'Español': ('Llama de la Forja', 'Ola de la Marea', 'Raíces del Bosque', 'Luz Errante'),
    '日本語': ('鍛冶場の炎', '潮の波', '森の根', '旅人の光'),
}
HERO_ICONS = {'spark': '🦊', 'anchor': '🐢', 'sprout': '🐭', 'scout': '🦉'}


def new_encounter(hero='spark'):
    if hero not in HEROES:
        raise ValueError('Personagem desconhecido.')
    return {'hero': hero, 'position': (2, 4), 'health': 8, 'max_health': 8,
            'power_ready': True, 'turn': 0, 'status': 'active',
            'enemies': [{'position': (0, 0), 'health': 3},
                        {'position': (4, 0), 'health': 3}], 'event': 'start'}


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def targets(state, kind):
    reach = 1 if kind == 'attack' else POWERS[state['hero']][1]
    return [i for i, enemy in enumerate(state['enemies'])
            if 0 < enemy['health'] and distance(state['position'], enemy['position']) <= reach]


def action(state, kind, direction=None, target=None):
    """Apply one valid action and one enemy response, without mutating input."""
    if state['status'] != 'active':
        raise ValueError('Partida encerrada.')
    result = deepcopy(state)
    if kind == 'move':
        shifts = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        if direction not in shifts:
            raise ValueError('Direção inválida.')
        dx, dy = shifts[direction]
        x, y = result['position']
        place = (x + dx, y + dy)
        if not all(0 <= n < SIZE for n in place) or any(e['position'] == place for e in result['enemies']):
            raise ValueError('Caminho bloqueado.')
        result['position'] = place
        result['power_ready'] = True
        result['event'] = 'move'
    elif kind in ('attack', 'power'):
        if not isinstance(target, int) or target not in targets(result, kind):
            raise ValueError('Alvo fora de alcance.')
        if kind == 'power' and not result['power_ready']:
            raise ValueError('Poder em recarga: mova-se para recuperá-lo.')
        result['enemies'][target]['health'] = max(0, result['enemies'][target]['health'] -
                                                 (1 if kind == 'attack' else POWERS[result['hero']][2]))
        if kind == 'power':
            result['power_ready'] = False
        result['event'] = kind
    else:
        raise ValueError('Ação inválida.')
    result['turn'] += 1
    if not any(enemy['health'] for enemy in result['enemies']):
        result['status'] = 'won'
        return result
    occupied = {e['position'] for e in result['enemies'] if e['health']}
    for enemy in result['enemies']:
        if not enemy['health']:
            continue
        if distance(enemy['position'], result['position']) == 1:
            result['health'] = max(0, result['health'] - 1)
        else:
            x, y = enemy['position']
            candidates = ((x, y + 1), (x - 1, y), (x + 1, y), (x, y - 1))
            possible = [p for p in candidates if all(0 <= n < SIZE for n in p)
                        and p != result['position'] and p not in occupied]
            if possible:
                new_position = min(possible, key=lambda p: distance(p, result['position']))
                if distance(new_position, result['position']) < distance(enemy['position'], result['position']):
                    occupied.remove(enemy['position'])
                    enemy['position'] = new_position
                    occupied.add(new_position)
    if result['health'] == 0:
        result['status'] = 'lost'
    return result


COPY = {
    'Português (BR)': ('⚔️ Jornada de Nacarim', 'Controle seu personagem, use poderes e derrote duas sombras.', 'Escolha seu personagem', 'Iniciar jornada', 'Nova jornada', 'Mover', 'Golpe próximo', 'Poder', 'Pronto', 'Recarrega ao mover', 'Vitória! As sombras recuaram.', 'Fim da jornada. Tente outra estratégia.', 'Turno', 'Vida', 'Sombras', 'Escolha um alvo', 'Norte', 'Sul', 'Oeste', 'Leste'),
    'English': ('⚔️ Nacarim Quest', 'Control your hero, use powers, and defeat two shadows.', 'Choose your hero', 'Start quest', 'New quest', 'Move', 'Close strike', 'Power', 'Ready', 'Recharge by moving', 'Victory! The shadows retreated.', 'Quest over. Try another strategy.', 'Turn', 'Health', 'Shadows', 'Choose a target', 'North', 'South', 'West', 'East'),
    'Español': ('⚔️ Aventura de Nacarim', 'Controla a tu héroe, usa poderes y derrota a dos sombras.', 'Elige tu héroe', 'Iniciar aventura', 'Nueva aventura', 'Mover', 'Golpe cercano', 'Poder', 'Listo', 'Recarga al moverte', '¡Victoria! Las sombras se retiraron.', 'Fin de la aventura. Prueba otra estrategia.', 'Turno', 'Vida', 'Sombras', 'Elige un objetivo', 'Norte', 'Sur', 'Oeste', 'Este'),
    '日本語': ('⚔️ ナカリムの冒険', 'キャラクターを動かし、力を使って影を倒そう。', 'キャラクターを選ぶ', '冒険を始める', '新しい冒険', '移動', '近接攻撃', '能力', '使用可能', '移動すると再使用可能', '勝利！影は退いた。', '冒険終了。別の作戦を試そう。', 'ターン', '体力', '影', '相手を選ぶ', '北', '南', '西', '東'),
}


def render_quest(st, language='Português (BR)'):
    from game_characters import portrait
    labels = COPY.get(language, COPY['English'])
    key = 'nacarim_quest'
    st.subheader(labels[0])
    st.caption(labels[1])
    if key not in st.session_state:
        hero = st.selectbox(labels[2], HEROES, format_func=lambda h: CAST[h][0], key='quest_hero')
        st.image(portrait(hero), width=160)
        if st.button(labels[3], key='quest_start', type='primary'):
            st.session_state[key] = new_encounter(hero)
            st.rerun()
        return
    state = st.session_state[key]
    if st.button(labels[4], key='quest_restart'):
        st.session_state.pop(key)
        st.rerun()
    st.image(portrait(state['hero']), width=130)
    st.caption(f"{CAST[state['hero']][0]} · {labels[12]} {state['turn']} · {labels[13]} {state['health']}/{state['max_health']} · {labels[14]} {sum(e['health'] > 0 for e in state['enemies'])}")
    st.progress(state['health'] / state['max_health'])
    tiles = []
    for y in range(SIZE):
        line = []
        for x in range(SIZE):
            enemy = next((e for e in state['enemies'] if e['health'] and e['position'] == (x, y)), None)
            line.append(HERO_ICONS[state['hero']] if state['position'] == (x, y)
                        else '👤' if enemy else '·')
        tiles.append('　'.join(line))
    st.code('\n'.join(tiles), language=None)
    if state['status'] != 'active':
        st.success(labels[10]) if state['status'] == 'won' else st.warning(labels[11])
        return
    power_name = (POWER_NAMES[language][HEROES.index(state['hero'])]
                  if language in POWER_NAMES else POWERS[state['hero']][0])
    st.caption(f"{labels[7]}: {power_name} · {labels[8] if state['power_ready'] else labels[9]}")
    direction = st.columns(4)
    for col, (name, label) in zip(direction, zip(('up', 'down', 'left', 'right'), labels[16:20])):
        if col.button(label, key='quest_' + name):
            try:
                st.session_state[key] = action(state, 'move', direction=name)
                st.rerun()
            except ValueError:
                pass
    kind = st.radio(labels[15], ('attack', 'power'), format_func=lambda x: labels[6 if x == 'attack' else 7], horizontal=True, key='quest_kind')
    available = targets(state, kind) if kind == 'attack' or state['power_ready'] else []
    if available:
        target = st.selectbox(labels[15], available, format_func=lambda i: f"{labels[14]} {i + 1} · ♥ {state['enemies'][i]['health']}", key='quest_target')
        if st.button(labels[6 if kind == 'attack' else 7], key='quest_act', type='primary'):
            st.session_state[key] = action(state, kind, target=target)
            st.rerun()
