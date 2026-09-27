"""Nacarim 3D game embedded in a Streamlit HTML component."""
import json
from pathlib import Path

LABELS = {
    'Português (BR)': {'title': 'Nacarim: Guardiões da Luz 3D'},
    'English': {'title': 'Nacarim: Guardians of Light 3D'},
    'Español': {'title': 'Nacarim: Guardianes de la Luz 3D'},
    '日本語': {'title': 'ナカリム：光の守護者 3D'},
}


def game_html(language='Português (BR)'):
    template = (Path(__file__).resolve().parent / 'assets' / 'nacarim' /
                'video_game_3d.html').read_text(encoding='utf-8')
    return template.replace('/*LANGUAGE*/', json.dumps(language, ensure_ascii=False))


def render_video_game(st, language='Português (BR)'):
    st.components.v1.html(game_html(language), height=780, scrolling=False)
