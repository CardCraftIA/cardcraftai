"""Self-contained real-time Nacarim action game for Streamlit's sandboxed iframe."""
import json
from base64 import b64encode
from pathlib import Path


LABELS = {
    'Português (BR)': dict(title='Nacarim: Guardiões da Luz', intro='Mova-se, lance poderes e proteja as pontes das sombras.', choose='Escolha seu guardião', start='Jogar', restart='Jogar novamente', move='Mover: WASD ou setas', run='Correr: Shift', attack='Ataque: espaço', special='Poder: E', goal='Dissipe 12 sombras para salvar a ponte.', health='Vida', defeated='Sombras', power='Poder', ready='Pronto', victory='A ponte está segura!', defeat='As sombras venceram desta vez.', pause='Pausar', resume='Continuar', paused='Jogo pausado', controls='Controles na tela', up='Cima', down='Baixo', left='Esquerda', right='Direita'),
    'English': dict(title='Nacarim: Guardians of Light', intro='Move, cast powers, and protect the bridges from the shadows.', choose='Choose your guardian', start='Play', restart='Play again', move='Move: WASD or arrows', run='Run: Shift', attack='Attack: space', special='Power: E', goal='Dispel 12 shadows to save the bridge.', health='Health', defeated='Shadows', power='Power', ready='Ready', victory='The bridge is safe!', defeat='The shadows won this time.', pause='Pause', resume='Resume', paused='Game paused', controls='On-screen controls', up='Up', down='Down', left='Left', right='Right'),
    'Español': dict(title='Nacarim: Guardianes de la Luz', intro='Muévete, usa poderes y protege los puentes de las sombras.', choose='Elige tu guardián', start='Jugar', restart='Jugar de nuevo', move='Mover: WASD o flechas', run='Correr: Shift', attack='Ataque: espacio', special='Poder: E', goal='Disipa 12 sombras para salvar el puente.', health='Vida', defeated='Sombras', power='Poder', ready='Listo', victory='¡El puente está a salvo!', defeat='Las sombras ganaron esta vez.', pause='Pausa', resume='Continuar', paused='Juego en pausa', controls='Controles en pantalla', up='Arriba', down='Abajo', left='Izquierda', right='Derecha'),
    '日本語': dict(title='ナカリム：光の守護者', intro='移動して力を放ち、影から橋を守ろう。', choose='守護者を選ぶ', start='遊ぶ', restart='もう一度', move='移動: WASD または矢印', run='走る: Shift', attack='攻撃: スペース', special='能力: E', goal='影を12体退けて橋を守ろう。', health='体力', defeated='影', power='能力', ready='使用可能', victory='橋を守った！', defeat='今回は影に負けた。', pause='一時停止', resume='再開', paused='一時停止中', controls='画面の操作', up='上', down='下', left='左', right='右'),
}
FULLSCREEN_LABELS = {
    'Português (BR)': ('⛶ Tela cheia', 'Sair da tela cheia', 'Tela cheia indisponível'),
    'English': ('⛶ Fullscreen', 'Exit fullscreen', 'Fullscreen unavailable'),
    'Español': ('⛶ Pantalla completa', 'Salir de pantalla completa', 'Pantalla completa no disponible'),
    '日本語': ('⛶ 全画面', '全画面を終了', '全画面を使用できません'),
}


def game_html(language='Português (BR)'):
    labels = LABELS.get(language, LABELS['English']).copy()
    labels.update(zip(('fullscreen', 'exitFullscreen', 'fullscreenUnavailable'),
                      FULLSCREEN_LABELS.get(language, FULLSCREEN_LABELS['English'])))
    art_dir = Path(__file__).resolve().parent / 'assets' / 'nacarim'
    template = (art_dir / 'video_game.html').read_text(encoding='utf-8')
    sprite_url = 'data:image/webp;base64,' + b64encode((art_dir / 'nilo-sprites-v1.webp').read_bytes()).decode('ascii')
    return (template.replace('/*CONFIG_JSON*/', json.dumps(labels, ensure_ascii=False))
            .replace('/*NILO_SPRITE*/', json.dumps(sprite_url)))


def render_video_game(st, language='Português (BR)'):
    st.components.v1.html(game_html(language), height=790, scrolling=False)
