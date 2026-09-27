"""Nacarim starter set metadata and deterministic arena abilities."""
from game_engine import BASE_IDS, CARDS, base_id, variant_id

# Effects are scored from the current board, so solo and online resolve alike.
RARITY = {'spark': 'common', 'anchor': 'common', 'sprout': 'common', 'scout': 'common',
          'ember': 'uncommon', 'current': 'uncommon', 'root': 'uncommon', 'wanderer': 'uncommon',
          'kiln': 'rare', 'tide': 'rare', 'canopy': 'rare', 'comet': 'rare'}
for _character in BASE_IDS:
    for _edition in range(2, 11):
        RARITY[variant_id(_character, _edition)] = ('rare' if _edition >= 8 else 'uncommon' if _edition >= 5 else 'common')
NUMBER = {variant_id(character, edition): f'NAC-{index:03d}'
          for index, (character, edition) in enumerate(((character, edition) for character in BASE_IDS for edition in range(1, 11)), 1)}

ABILITY = {
    'Português (BR)': {
        'spark': ('Primeira Luz', '+1 se for sua primeira carta nesta arena.'),
        'anchor': ('Casco Firme', '+2 se o rival tiver mais cartas nesta arena.'),
        'sprout': ('Florescer', '+1 por outra carta sua nesta arena, até +2.'),
        'scout': ('Vigília', '+1 em qualquer arena.'),
        'ember': ('Fogo de Resposta', '+2 se o rival tiver duas ou mais cartas aqui.'),
        'current': ('Água em Movimento', '+2 quando você tiver duas ou mais cartas aqui.'),
        'root': ('Solo Seguro', '+2 enquanto o rival não tiver carta aqui.'),
        'wanderer': ('Passo Solitário', '+2 se esta for sua única carta aqui.'),
        'kiln': ('Calor Coletivo', '+1 por outra carta sua aqui, até +3.'),
        'tide': ('Encontro das Marés', '+2 se houver ao menos uma carta rival aqui.'),
        'canopy': ('Copa Compartilhada', '+1 por outra carta sua aqui, até +3.'),
        'comet': ('Última Estrela', '+3 se esta for sua única carta aqui e houver rival.'),
    },
    'English': {
        'spark': ('First Light', '+1 if this is your first card in this arena.'),
        'anchor': ('Steady Shell', '+2 if your opponent has more cards here.'),
        'sprout': ('Bloom', '+1 for each other friendly card here, up to +2.'),
        'scout': ('Watchful Eye', '+1 in any arena.'),
        'ember': ('Answering Flame', '+2 if your opponent has at least two cards here.'),
        'current': ('Moving Water', '+2 when you have at least two cards here.'),
        'root': ('Safe Ground', '+2 while your opponent has no card here.'),
        'wanderer': ('Lone Step', '+2 if this is your only card here.'),
        'kiln': ('Shared Heat', '+1 for each other friendly card here, up to +3.'),
        'tide': ('Meeting Tides', '+2 if an opposing card is here.'),
        'canopy': ('Shared Canopy', '+1 for each other friendly card here, up to +3.'),
        'comet': ('Last Star', '+3 if this is your only card here and an opponent is present.'),
    },
    'Español': {
        'spark': ('Primera Luz', '+1 si es tu primera carta en esta arena.'),
        'anchor': ('Caparazón Firme', '+2 si tu rival tiene más cartas aquí.'),
        'sprout': ('Florecer', '+1 por cada otra carta tuya aquí, hasta +2.'),
        'scout': ('Vigilia', '+1 en cualquier arena.'),
        'ember': ('Llama de Respuesta', '+2 si tu rival tiene dos o más cartas aquí.'),
        'current': ('Agua en Movimiento', '+2 cuando tengas dos o más cartas aquí.'),
        'root': ('Suelo Seguro', '+2 mientras tu rival no tenga cartas aquí.'),
        'wanderer': ('Paso Solitario', '+2 si es tu única carta aquí.'),
        'kiln': ('Calor Compartido', '+1 por cada otra carta tuya aquí, hasta +3.'),
        'tide': ('Encuentro de Mareas', '+2 si hay una carta rival aquí.'),
        'canopy': ('Copa Compartida', '+1 por cada otra carta tuya aquí, hasta +3.'),
        'comet': ('Última Estrella', '+3 si es tu única carta aquí y hay rival.'),
    },
    '日本語': {
        'spark': ('最初の光', 'このアリーナで最初に出した自分のカードなら+1。'),
        'anchor': ('堅い甲羅', '相手のカード枚数が多いなら+2。'),
        'sprout': ('開花', 'ここにある他の自分のカード1枚につき+1、最大+2。'),
        'scout': ('見張り', 'どのアリーナでも+1。'),
        'ember': ('応える炎', 'ここに相手のカードが2枚以上なら+2。'),
        'current': ('流れる水', 'ここに自分のカードが2枚以上なら+2。'),
        'root': ('安全な大地', 'ここに相手のカードがなければ+2。'),
        'wanderer': ('孤独な一歩', 'ここで自分のカードがこれだけなら+2。'),
        'kiln': ('分かち合う熱', 'ここにある他の自分のカード1枚につき+1、最大+3。'),
        'tide': ('潮の出会い', 'ここに相手のカードがあれば+2。'),
        'canopy': ('共に広がる樹冠', 'ここにある他の自分のカード1枚につき+1、最大+3。'),
        'comet': ('最後の星', '自分のカードがこれだけで、相手のカードがあれば+3。'),
    },
}

VARIANT_ABILITIES = {
    'Português (BR)': (
        ('Aurora', '+2 se for sua primeira carta nesta arena.'),
        ('Encontro', '+1 por outra carta sua aqui, até +3.'),
        ('Desafio', '+2 se o rival tiver mais cartas aqui.'),
        ('Bastião', '+2 enquanto o rival não tiver carta aqui.'),
        ('Duelo', '+3 se houver exatamente uma carta de cada lado aqui.'),
        ('Coro', '+1 por carta rival aqui, até +3.'),
        ('Convergência', '+3 se você tiver três ou mais cartas aqui.'),
        ('Virada', '+4 se for sua única carta e houver duas ou mais cartas rivais aqui.'),
        ('Apogeu', '+2 se você tiver quatro cartas aqui.'),
    ),
    'English': (
        ('Dawn', '+2 if this is your first card in this arena.'),
        ('Gathering', '+1 for each other friendly card here, up to +3.'),
        ('Challenge', '+2 if the opponent has more cards here.'),
        ('Bastion', '+2 while the opponent has no card here.'),
        ('Duel', '+3 if each side has exactly one card here.'),
        ('Chorus', '+1 per opposing card here, up to +3.'),
        ('Convergence', '+3 if you have at least three cards here.'),
        ('Turnabout', '+4 if this is your only card here against at least two opposing cards.'),
        ('Zenith', '+2 if you have four cards here.'),
    ),
    'Español': (
        ('Aurora', '+2 si es tu primera carta en esta arena.'),
        ('Encuentro', '+1 por otra carta tuya aquí, hasta +3.'),
        ('Desafío', '+2 si tu rival tiene más cartas aquí.'),
        ('Bastión', '+2 mientras tu rival no tenga cartas aquí.'),
        ('Duelo', '+3 si hay exactamente una carta de cada lado aquí.'),
        ('Coro', '+1 por carta rival aquí, hasta +3.'),
        ('Convergencia', '+3 si tienes tres o más cartas aquí.'),
        ('Giro', '+4 si es tu única carta frente a dos o más cartas rivales.'),
        ('Apogeo', '+2 si tienes cuatro cartas aquí.'),
    ),
    '日本語': (
        ('夜明け', 'このアリーナで最初の自分のカードなら+2。'),
        ('集い', 'ここにある他の自分のカード1枚につき+1、最大+3。'),
        ('挑戦', '相手のカード枚数が多ければ+2。'),
        ('砦', '相手のカードがなければ+2。'),
        ('決闘', '両者のカードがちょうど1枚ずつなら+3。'),
        ('合唱', '相手のカード1枚につき+1、最大+3。'),
        ('収束', '自分のカードが3枚以上なら+3。'),
        ('逆転', '自分のカードがこれだけで相手が2枚以上なら+4。'),
        ('頂点', '自分のカードが4枚なら+2。'),
    ),
}
for _language, _edition_text in VARIANT_ABILITIES.items():
    for _character in BASE_IDS:
        for _edition in range(2, 11):
            ABILITY[_language][variant_id(_character, _edition)] = _edition_text[_edition - 2]


def ability_bonus(card, own, opposing):
    """Pure board calculation; no hidden state or random rolls."""
    allies, enemies = len(own), len(opposing)
    if card != base_id(card):
        edition = int(card.rpartition('_v')[2])
        if edition == 2: return 2 * (own[0] == card)
        if edition == 3: return min(3, allies - 1)
        if edition == 4: return 2 * (enemies > allies)
        if edition == 5: return 2 * (enemies == 0)
        if edition == 6: return 3 * (allies == 1 and enemies == 1)
        if edition == 7: return min(3, enemies)
        if edition == 8: return 3 * (allies >= 3)
        if edition == 9: return 4 * (allies == 1 and enemies >= 2)
        if edition == 10: return 2 * (allies == 4)
    if card == 'spark': return int(own[0] == card)
    if card == 'anchor': return 2 * (enemies > allies)
    if card == 'sprout': return min(2, allies - 1)
    if card == 'scout': return 1
    if card == 'ember': return 2 * (enemies >= 2)
    if card == 'current': return 2 * (allies >= 2)
    if card == 'root': return 2 * (enemies == 0)
    if card == 'wanderer': return 2 * (allies == 1)
    if card == 'kiln': return min(3, allies - 1)
    if card == 'tide': return 2 * (enemies >= 1)
    if card == 'canopy': return min(3, allies - 1)
    if card == 'comet': return 3 * (allies == 1 and enemies >= 1)
    raise KeyError(card)
