"""Code-native power scenes composed around each original animal portrait.

Ten visual stages are derived from the same character portrait. The stage
effects are original SVG shapes, rendered consistently in the catalog and game.
"""
from base64 import b64encode
from functools import lru_cache
from html import escape
from pathlib import Path

from game_engine import CARDS, base_id
from game_characters import ART_DIR, CAST
from game_art import SCENES

REGION_COLORS = {
    'forge': ('#ff9e56', '#ffdc8a'),
    'reef': ('#56c9f2', '#c3f9ff'),
    'grove': ('#8ddb82', '#dcffac'),
    None: ('#bfa2fa', '#fff0b6'),
}
STAGE_COLORS = ('#d9bb87', '#ffbe69', '#93e6f2', '#ff748f', '#6bdfae',
                '#cf9af9', '#ffd86c', '#9be9e4', '#ff8d64', '#fff4bc')


def _stage(card):
    return 1 if card == base_id(card) else int(card.rpartition('_v')[2])


def _effect(stage, color, bright):
    """Distinct power manifestations, all kept outside the character's face."""
    center = '<circle cx="360" cy="377" r="42" fill="url(#orb)" filter="url(#glow)"/>'
    if stage == 1:
        return '<path d="M44 590Q250 570 468 590" fill="none" stroke="%s" stroke-width="5" opacity=".7"/>' % color
    if stage == 2:  # opening flare
        return center + f'<path d="M360 280v-85m0 360v-85m-96-93h-90m370 0h-90M290 307l-69-69m278 278-69-69M430 307l69-69m-278 278 69-69" stroke="{bright}" stroke-width="8" stroke-linecap="round" filter="url(#glow)"/>'
    if stage == 3:  # linked companions
        return f'<path d="M76 490Q158 322 286 454T458 365" fill="none" stroke="{color}" stroke-width="13" filter="url(#glow)"/><circle cx="96" cy="472" r="22" fill="{bright}"/><circle cx="286" cy="454" r="18" fill="{bright}"/><circle cx="452" cy="369" r="26" fill="{bright}"/>'
    if stage == 4:  # counterstrike
        return f'<path d="M92 530 212 377 171 371 313 207 280 353 339 340 197 562 220 433Z" fill="{color}" stroke="{bright}" stroke-width="5" filter="url(#glow)"/>'
    if stage == 5:  # protective bastion
        return f'<path d="M260 205 428 269v147q-12 111-168 182Q105 527 92 416V269Z" fill="none" stroke="{bright}" stroke-width="11" filter="url(#glow)"/><path d="M260 250 385 297v114q-8 82-125 143" fill="none" stroke="{color}" stroke-width="5"/>'
    if stage == 6:  # opposed duel
        return f'<circle cx="146" cy="340" r="48" fill="url(#orb)"/><circle cx="382" cy="340" r="48" fill="url(#orb)"/><path d="M178 330 349 355M178 355 349 330" stroke="{bright}" stroke-width="14" filter="url(#glow)"/><path d="M246 282 274 400" stroke="white" stroke-width="5"/>'
    if stage == 7:  # voices in a chorus
        return ''.join(f'<path d="M{40+i*14} {500-i*12}Q{175+i*11} {290-i*22} {452-i*8} {380+i*16}" fill="none" stroke="{bright if i%2 else color}" stroke-width="{3+i}" opacity=".8" filter="url(#glow)"/>' for i in range(5))
    if stage == 8:  # converging sigils
        return f'<path d="M257 180 449 511H65Z" fill="none" stroke="{bright}" stroke-width="9" filter="url(#glow)"/><path d="M257 526 74 254h366Z" fill="none" stroke="{color}" stroke-width="8"/><circle cx="257" cy="354" r="73" fill="none" stroke="{bright}" stroke-width="7"/>'
    if stage == 9:  # rising power in a reversal
        return f'<path d="M38 558Q177 460 250 473T478 230M72 603Q245 496 315 498T490 310" fill="none" stroke="{bright}" stroke-width="22" filter="url(#glow)"/><path d="M468 215 484 318 397 280Z" fill="{color}"/>'
    # stage 10: a radiant finale
    return center + f'<circle cx="258" cy="363" r="186" fill="none" stroke="{bright}" stroke-width="10" filter="url(#glow)"/><circle cx="258" cy="363" r="139" fill="none" stroke="{color}" stroke-width="5" stroke-dasharray="14 20"/><path d="M258 134 281 329 471 363 281 395 258 593 234 395 45 363 234 329Z" fill="none" stroke="{bright}" stroke-width="10" filter="url(#glow)"/>'


@lru_cache(maxsize=140)
def evolution_svg(card):
    if card not in CARDS:
        raise KeyError(card)
    character = base_id(card)
    stage = _stage(card)
    color, bright = REGION_COLORS[CARDS[card][3]]
    accent = STAGE_COLORS[stage - 1]
    image = b64encode((Path(ART_DIR) / f'{character}.jpg').read_bytes()).decode('ascii')
    effect = _effect(stage, accent, bright)
    # Main portrait is visible; the power scene surrounds its body and foreground.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="512" height="720" viewBox="0 0 512 720" role="img" aria-label="{escape(CAST[character][0])}, stage {stage}">
<title>{escape(CAST[character][0])} · {stage:02d}</title>
<defs><clipPath id="window"><rect x="16" y="54" width="480" height="590" rx="20"/></clipPath>
<linearGradient id="veil" x2="1" y2="1"><stop stop-color="{color}" stop-opacity=".28"/><stop offset=".52" stop-color="{accent}" stop-opacity=".02"/><stop offset="1" stop-color="{accent}" stop-opacity=".37"/></linearGradient>
<radialGradient id="orb"><stop stop-color="#ffffff" stop-opacity=".98"/><stop offset=".4" stop-color="{bright}" stop-opacity=".85"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<linearGradient id="shine" x2="1" y2="1"><stop stop-color="{accent}"/><stop offset="1" stop-color="{bright}"/></linearGradient>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect width="512" height="720" rx="30" fill="#10162b"/>
<g clip-path="url(#window)"><image xlink:href="data:image/jpeg;base64,{image}" x="16" y="12" width="480" height="720" preserveAspectRatio="xMidYMid slice"/>
<rect x="16" y="54" width="480" height="590" fill="url(#veil)"/>
<g opacity="{min(.9, .37 + stage*.055):.2f}">{effect}</g>
<g transform="translate(330 490) scale(.42)" opacity=".9" filter="url(#glow)">{SCENES[character]}</g></g>
<rect x="10" y="10" width="492" height="700" rx="26" fill="none" stroke="{accent}" stroke-width="8"/>
<rect x="20" y="20" width="472" height="680" rx="20" fill="none" stroke="{bright}" stroke-opacity=".65" stroke-width="2"/>
<path d="M36 56h440M36 646h440" stroke="{accent}" stroke-width="4"/>
<rect x="176" y="651" width="160" height="41" rx="20" fill="#11172d" stroke="{accent}" stroke-width="3"/>
<text x="256" y="679" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="23" fill="{bright}">NAC · {stage:02d}/10</text>
</svg>'''
