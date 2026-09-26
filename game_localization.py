"""CardCraft Arena copy, independent from the engine's stable card IDs."""

CARD_NAMES = {
    'Português (BR)': ('Faísca', 'Âncora', 'Broto', 'Batedor', 'Brasa', 'Corrente', 'Raiz', 'Andarilho', 'Fornalha', 'Onda Alta', 'Copa Viva', 'Cometa'),
    'English': ('Spark', 'Anchor', 'Sprout', 'Scout', 'Ember', 'Current', 'Root', 'Wanderer', 'Kiln', 'High Tide', 'Living Canopy', 'Comet'),
    'Español': ('Chispa', 'Ancla', 'Brote', 'Explorador', 'Ascua', 'Corriente', 'Raíz', 'Errante', 'Horno', 'Marea Alta', 'Copa Viva', 'Cometa'),
    '日本語': ('火花', 'いかり', '新芽', '偵察者', '残り火', '潮流', '根', '旅人', '炉', '大潮', '生きた樹冠', '彗星'),
}
CARD_DESCRIPTIONS = {
    'Português (BR)': ('Acende a primeira jogada.', 'Segura uma arena disputada.', 'Cresce no momento certo.', 'Poder estável em qualquer arena.',
                       'Pressiona a Forja.', 'Ganha força na Maré.', 'Defende o Bosque.', 'Encontra seu lugar em qualquer terreno.',
                       'Seu calor muda a disputa.', 'Uma aposta forte na Maré.', 'Uma aposta forte no Bosque.', 'Força decisiva no fim da partida.'),
    'English': ('Ignites your opening move.', 'Holds a contested arena.', 'Grows at the right moment.', 'Reliable power in any arena.',
                'Pressures the Forge.', 'Gains power on the Reef.', 'Defends the Grove.', 'Finds a place on any terrain.',
                'Its heat turns the contest.', 'A strong play on the Reef.', 'A strong play in the Grove.', 'Decisive power at the end.'),
    'Español': ('Enciende tu primera jugada.', 'Resiste en una arena disputada.', 'Crece en el momento justo.', 'Fuerza estable en cualquier arena.',
                 'Presiona la Forja.', 'Gana fuerza en la Marea.', 'Defiende el Bosque.', 'Encuentra su lugar en cualquier terreno.',
                 'Su calor cambia la disputa.', 'Una jugada fuerte en la Marea.', 'Una jugada fuerte en el Bosque.', 'Fuerza decisiva al final.'),
    '日本語': ('初手に火をつける。', '競り合うアリーナを守る。', '好機に育つ。', 'どのアリーナでも安定した力。',
             '鍛冶場に圧力をかける。', '海辺で力を得る。', '森を守る。', 'どんな場所にも居場所を見つける。',
             '熱で戦況を変える。', '海辺での強い一手。', '森での強い一手。', '終盤の決め手。'),
}
CARD_IDS = ('spark', 'anchor', 'sprout', 'scout', 'ember', 'current', 'root', 'wanderer', 'kiln', 'tide', 'canopy', 'comet')
ARENA_NAMES = {
    'Português (BR)': {'forge': 'Forja', 'reef': 'Maré', 'grove': 'Bosque'},
    'English': {'forge': 'Forge', 'reef': 'Reef', 'grove': 'Grove'},
    'Español': {'forge': 'Forja', 'reef': 'Marea', 'grove': 'Bosque'},
    '日本語': {'forge': '鍛冶場', 'reef': '海辺', 'grove': '森'},
}
UI = {
    'Português (BR)': {'round': 'Rodada {n} / 6 · ⚡ {n}', 'score': 'Você {you} × {opponent} rival',
                       'card': 'Carta', 'arena': 'Arena', 'your_cards': 'Suas cartas', 'opponent_cards': 'Cartas do rival',
                       'demo': 'Esta é uma demonstração gratuita. Entre na sua conta para desafiar outra pessoa online.',
                       'sign_in': 'Entrar no CardCraftAI', 'share': 'Compartilhar demonstração solo', 'invite': 'Convite',
                       'previous_unavailable': 'Suas partidas anteriores não estão disponíveis agora.',
                       'create_error': 'Não foi possível criar a sala. Tente novamente.', 'join_error': 'Não foi possível entrar na sala.',
                       'save_error': 'Não foi possível salvar a jogada. Atualize a partida.', 'load_error': 'Não foi possível carregar a partida agora.',
                       'learned': 'Você praticou energia, mão, afinidade e controle de arenas — ideias comuns em jogos de cartas estratégicos.'},
    'English': {'round': 'Round {n} / 6 · ⚡ {n}', 'score': 'You {you} × {opponent} opponent',
                'card': 'Card', 'arena': 'Arena', 'your_cards': 'Your cards', 'opponent_cards': 'Opponent cards',
                'demo': 'This is a free demo. Sign in to challenge another player online.',
                'sign_in': 'Sign in to CardCraftAI', 'share': 'Share the solo demo', 'invite': 'Invite',
                'previous_unavailable': 'Your previous matches are unavailable right now.',
                'create_error': 'Could not create the room. Try again.', 'join_error': 'Could not join the room.',
                'save_error': 'Could not save that move. Refresh the match.', 'load_error': 'Could not load the match right now.',
                'learned': 'You practiced energy, hand, affinity and arena control — common ideas in strategic card games.'},
    'Español': {'round': 'Ronda {n} / 6 · ⚡ {n}', 'score': 'Tú {you} × {opponent} rival',
                 'card': 'Carta', 'arena': 'Arena', 'your_cards': 'Tus cartas', 'opponent_cards': 'Cartas del rival',
                 'demo': 'Esta es una demostración gratuita. Inicia sesión para desafiar a otra persona.',
                 'sign_in': 'Entrar en CardCraftAI', 'share': 'Compartir demostración solo', 'invite': 'Invitación',
                 'previous_unavailable': 'Tus partidas anteriores no están disponibles ahora.',
                 'create_error': 'No se pudo crear la sala. Inténtalo otra vez.', 'join_error': 'No se pudo entrar en la sala.',
                 'save_error': 'No se pudo guardar la jugada. Actualiza la partida.', 'load_error': 'No se pudo cargar la partida ahora.',
                 'learned': 'Practicaste energía, mano, afinidad y control de arenas: conceptos de juegos de cartas estratégicos.'},
    '日本語': {'round': 'ラウンド {n} / 6 · ⚡ {n}', 'score': 'あなた {you} × {opponent} 相手',
             'card': 'カード', 'arena': 'アリーナ', 'your_cards': 'あなたのカード', 'opponent_cards': '相手のカード',
             'demo': '無料体験版です。ほかの人との対戦にはログインしてください。',
             'sign_in': 'CardCraftAIにログイン', 'share': '一人用体験版を共有', 'invite': '招待',
             'previous_unavailable': '以前の対戦を現在読み込めません。',
             'create_error': '部屋を作成できません。もう一度お試しください。', 'join_error': '部屋に入れません。',
             'save_error': '手を保存できません。対戦を更新してください。', 'load_error': '対戦を読み込めません。',
             'learned': 'エネルギー、手札、相性、アリーナの支配を学びました。戦略カードゲームにも共通する考え方です。'},
}


def card_text(card, language='Português (BR)'):
    from game_characters import CAST
    index = CARD_IDS.index(card)
    title = CARD_NAMES.get(language, CARD_NAMES['English'])[index]
    return f'{CAST[card][0]} · {title}', CARD_DESCRIPTIONS.get(language, CARD_DESCRIPTIONS['English'])[index]


def arena_text(lane, language='Português (BR)'):
    return ARENA_NAMES.get(language, ARENA_NAMES['English'])[lane]


def ui(language, key, **values):
    return UI.get(language, UI['English'])[key].format(**values)


ERRORS = {
    'Não é sua vez.': ('Not your turn.', 'No es tu turno.', 'あなたの番ではありません。'),
    'Jogada inválida: confira sua mão, energia e arena.': ('Invalid move: check your hand, energy and arena.', 'Jugada inválida: revisa tu mano, energía y arena.', '手札、エネルギー、アリーナを確認してください。'),
    'Passe sem selecionar arena.': ('Pass without selecting an arena.', 'Pasa sin elegir arena.', 'パスするときはアリーナを選ばないでください。'),
    'Entre na sua conta para jogar online.': ('Sign in to play online.', 'Inicia sesión para jugar online.', 'オンライン対戦にはログインしてください。'),
    'Sua sessão expirou. Entre novamente.': ('Your session expired. Sign in again.', 'Tu sesión caducó. Vuelve a entrar.', 'セッションが切れました。再度ログインしてください。'),
    'Partida inválida.': ('Invalid match.', 'Partida inválida.', '無効な対戦です。'),
    'Partida não encontrada.': ('Match not found.', 'Partida no encontrada.', '対戦が見つかりません。'),
    'Você não participa desta partida.': ('You are not a participant in this match.', 'No participas en esta partida.', 'この対戦には参加していません。'),
    'Código de convite inválido.': ('Invalid invitation code.', 'Código de invitación inválido.', '招待コードが無効です。'),
    'Convite não encontrado.': ('Invitation not found.', 'Invitación no encontrada.', '招待が見つかりません。'),
    'Esta partida já começou.': ('This match has already started.', 'Esta partida ya comenzó.', 'この対戦はすでに始まっています。'),
    'Outro jogador entrou primeiro. Atualize a partida.': ('Another player joined first. Refresh the match.', 'Otra persona entró primero. Actualiza la partida.', 'ほかの人が先に参加しました。更新してください。'),
    'A partida ainda não está ativa.': ('The match is not active yet.', 'La partida aún no está activa.', '対戦はまだ始まっていません。'),
    'A partida mudou. Atualize antes de jogar.': ('The match changed. Refresh before playing.', 'La partida cambió. Actualiza antes de jugar.', '対戦が更新されました。手を出す前に更新してください。'),
    'Outra jogada chegou antes. Atualize a partida.': ('Another move arrived first. Refresh the match.', 'Llegó otra jugada primero. Actualiza la partida.', '先に別の手が入りました。更新してください。'),
}


def error_text(error, language):
    source = str(error)
    if language == 'Português (BR)':
        return source
    variants = ERRORS.get(source)
    if not variants:
        return UI.get(language, UI['English'])['load_error']
    return variants[{'English': 0, 'Español': 1, '日本語': 2}.get(language, 0)]
