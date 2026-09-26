"""Original vector illustrations for the twelve CardCraft Arena cards."""
from html import escape

PALETTES = {
    'forge': ('#ffb25b', '#7e284d', '#251633'),
    'reef': ('#71e4f1', '#176699', '#102b50'),
    'grove': ('#b7ec79', '#2a7968', '#123d40'),
    'neutral': ('#d5c2ff', '#634caa', '#22254c'),
}

# Each scene is a self-contained silhouette, with no trademarked creatures/art.
SCENES = {
    'spark': '<path d="M151 180C99 157 108 116 151 69c-5 30 34 39 22 72 23-16 15-41 12-51 48 53 18 100-34 90Z" fill="url(#shine)"/><path d="M151 164c-23-15-15-33 1-51-3 17 22 20 12 39 10-5 10-14 9-18 10 17-2 33-22 30Z" fill="#fff4d0"/>',
    'anchor': '<circle cx="160" cy="72" r="14" fill="none" stroke="url(#shine)" stroke-width="9"/><path d="M160 87v84M123 112h74M118 147c0 51 84 51 84 0m-84 0-12 13m96-13 12 13" fill="none" stroke="url(#shine)" stroke-width="11" stroke-linecap="round"/><path d="M79 183c31-18 57-9 81 2s51 12 82-3" fill="none" stroke="#b8f8ff" stroke-width="5" opacity=".65"/>',
    'sprout': '<path d="M160 188V113" stroke="url(#shine)" stroke-width="12" stroke-linecap="round"/><path d="M157 121C111 123 91 97 96 68c30-2 55 11 61 53Zm8 10c46-9 62-37 56-68-36 3-58 27-56 68Z" fill="url(#shine)"/><path d="M102 188c24-19 42-11 58 0 18-11 40-19 59 0" fill="none" stroke="#c9f6ac" stroke-width="5"/>',
    'scout': '<circle cx="160" cy="125" r="70" fill="none" stroke="url(#shine)" stroke-width="5"/><circle cx="160" cy="125" r="47" fill="none" stroke="#dcd0ff" opacity=".65"/><path d="m160 66 20 58-20 59-20-59Z" fill="url(#shine)"/><circle cx="160" cy="125" r="9" fill="#fff"/><path d="M160 42v15m0 138v15M77 125h15m136 0h15" stroke="#ddd5ff" stroke-width="5"/>',
    'ember': '<path d="M109 169c-35-37-11-86 17-108-8 34 7 45 17 54 12-21 5-45 10-67 43 41 80 103 30 130-23 14-52 11-74-9Z" fill="url(#shine)"/><path d="M148 174c-19-19-4-40 13-62-4 22 28 31 16 51-8 15-20 17-29 11Z" fill="#fff0c0"/><circle cx="215" cy="77" r="5" fill="#ffd889"/><circle cx="91" cy="117" r="4" fill="#ffd889"/>',
    'current': '<path d="M53 137c45-50 84-55 119-21 34 33 57 28 95-7-31 64-77 84-120 47-27-24-55-20-94-19Z" fill="url(#shine)"/><path d="M54 169c36-22 67-18 98 5 35 25 73 15 109-12" fill="none" stroke="#c5fbff" stroke-width="8" stroke-linecap="round"/><circle cx="216" cy="76" r="13" fill="#d3ffff" opacity=".75"/>',
    'root': '<path d="M160 58v92m0-5-53 43m53-43 53 43m-53-24-26 30m26-30 27 30" fill="none" stroke="url(#shine)" stroke-width="14" stroke-linecap="round"/><path d="M132 83c-24-25-22-46-9-55 23 8 31 29 32 51m10-5c10-30 29-43 51-42 2 24-13 44-47 51" fill="url(#shine)"/>',
    'wanderer': '<circle cx="160" cy="106" r="61" fill="none" stroke="url(#shine)" stroke-width="6"/><path d="m160 46 11 54 53 11-53 11-11 54-11-54-53-11 53-11Z" fill="url(#shine)"/><circle cx="160" cy="111" r="14" fill="#fff"/><path d="M68 185q92-44 184 0" fill="none" stroke="#b7b0ed" stroke-width="5"/>',
    'kiln': '<path d="M89 177V91l71-39 71 39v86Z" fill="url(#shine)"/><path d="M104 102h112v61H104Z" fill="#3c2342"/><path d="M159 151c-22-13-16-33 0-53-1 17 21 24 12 41 7-4 9-11 8-16 13 21-2 39-20 28Z" fill="#fff1c5"/><path d="M93 176h134" stroke="#ffe2ac" stroke-width="9"/>',
    'tide': '<path d="M48 151c28-47 69-74 94-66 27 9 18 48 45 49 23 2 42-23 81-45-13 62-51 96-111 94-53-2-79-12-109-32Z" fill="url(#shine)"/><path d="M43 176c45-29 80-22 112-4 31 17 68 13 118-11" fill="none" stroke="#d2ffff" stroke-width="7"/><circle cx="207" cy="60" r="17" fill="#dcffff" opacity=".8"/>',
    'canopy': '<path d="M160 179v-64" stroke="#c6ed9a" stroke-width="14" stroke-linecap="round"/><path d="M92 118c-26-31-5-70 28-70 17-29 57-30 75-2 42-6 65 43 34 70-24 21-44 15-69 10-29 15-52 13-68-8Z" fill="url(#shine)"/><path d="M82 181q78-25 156 0" fill="none" stroke="#d4ffba" stroke-width="6"/><circle cx="118" cy="78" r="7" fill="#f5ffd5"/><circle cx="202" cy="88" r="7" fill="#f5ffd5"/>',
    'comet': '<path d="M45 173c51-57 91-71 139-76" stroke="url(#shine)" stroke-width="22" stroke-linecap="round" opacity=".5"/><path d="M63 186c38-37 76-56 112-64" stroke="#f7ddff" stroke-width="7" stroke-linecap="round" opacity=".8"/><circle cx="210" cy="94" r="39" fill="url(#shine)"/><circle cx="201" cy="87" r="14" fill="#fff" opacity=".8"/><circle cx="82" cy="67" r="3" fill="#fff"/><circle cx="113" cy="43" r="3" fill="#fff"/>',
}

AFFINITY = {'spark': 'forge', 'anchor': 'reef', 'sprout': 'grove', 'scout': 'neutral',
            'ember': 'forge', 'current': 'reef', 'root': 'grove', 'wanderer': 'neutral',
            'kiln': 'forge', 'tide': 'reef', 'canopy': 'grove', 'comet': 'neutral'}


def card_svg(card, title=''):
    if card not in SCENES:
        raise ValueError('Unknown game illustration')
    glow, middle, dark = PALETTES[AFFINITY[card]]
    title = escape(title or card)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 220" width="320" height="220" role="img" aria-label="{title}">
<title>{title}</title><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="{dark}"/><stop offset="1" stop-color="{middle}"/></linearGradient>
<linearGradient id="shine" x2="1" y2="1"><stop stop-color="{glow}"/><stop offset="1" stop-color="#fff4e0"/></linearGradient>
<radialGradient id="halo"><stop stop-color="{glow}" stop-opacity=".35"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient></defs>
<rect width="320" height="220" rx="18" fill="url(#bg)"/><circle cx="160" cy="115" r="120" fill="url(#halo)"/>
<path d="M18 23h284M18 197h284" stroke="{glow}" stroke-opacity=".27" stroke-width="2"/>
<g>{SCENES[card]}</g><rect x="5" y="5" width="310" height="210" rx="14" fill="none" stroke="{glow}" stroke-opacity=".55" stroke-width="2"/>
</svg>'''
