"""Original cast and card portraits for the world of Nacarim."""
from pathlib import Path
from game_engine import base_id

ART_DIR = Path(__file__).resolve().parent / 'assets' / 'nacarim'
CAST = {
    'spark': ('Nilo', 'raposa', 'Forja'),
    'anchor': ('Tora', 'tartaruga marinha', 'Maré'),
    'sprout': ('Pipa', 'arganaz', 'Bosque'),
    'scout': ('Lume', 'coruja', 'Viajantes'),
    'ember': ('Brasa', 'panda-vermelho', 'Forja'),
    'current': ('Suri', 'lontra', 'Maré'),
    'root': ('Oru', 'tatu', 'Bosque'),
    'wanderer': ('Miri', 'lince', 'Viajantes'),
    'kiln': ('Faro', 'pangolim', 'Forja'),
    'tide': ('Aira', 'arraia', 'Maré'),
    'canopy': ('Varo', 'cervo', 'Bosque'),
    'comet': ('Astra', 'lebre', 'Viajantes'),
}


def portrait(card):
    """Return the bundled portrait for a stable game card ID."""
    return str(ART_DIR / f'{base_id(card)}.webp')
