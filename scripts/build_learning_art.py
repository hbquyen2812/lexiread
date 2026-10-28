"""Original, local SVG scenes for the learning guide. No external images or runtime services."""
from pathlib import Path
from build_word_art import DRAWINGS

ROOT = Path(__file__).resolve().parents[1] / 'static/illustrations/scenes'
SCENES = {
    'guide': ('#edf2e8', 'book', 'compass', 'pencil'),
    'recall': ('#f8eee1', 'cards', 'people', 'book'),
    'spacing': ('#e9f1ec', 'calendar', 'clock', 'plant'),
    'feedback': ('#f6eee5', 'pencil', 'book', 'cards'),
    'video': ('#eaf0f5', 'laptop', 'coffee', 'pencil'),
    'grammar': ('#f2eee7', 'book', 'pencil', 'plant'),
    'words': ('#edf2e8', 'cards', 'apple', 'coffee'),
    'import': ('#e9f1ec', 'folder', 'laptop', 'cards'),
}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, (color, main, left, right) in SCENES.items():
        bodies = ''.join(f'<g transform="translate({x} {y}) scale({scale})">{DRAWINGS[key]}</g>'
                         for key, x, y, scale in [(left, 22, 74, .9), (main, 180, 10, 1.35), (right, 397, 71, .9)])
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 240" width="560" height="240">
<rect width="560" height="240" rx="24" fill="{color}"/>
<circle cx="280" cy="116" r="101" fill="#fffdf4" opacity=".8"/>
<path d="M50 191q65 24 110-4m231 0q65 24 110-4" fill="none" stroke="#ccdacc" stroke-width="3" stroke-linecap="round"/>
<g fill="#dbb570"><circle cx="173" cy="56" r="5"/><circle cx="410" cy="44" r="5"/><path d="m365 188 4-10 4 10 10 4-10 4-4 10-4-10-10-4Z"/></g>
<g stroke="#456557" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{bodies}</g>
</svg>'''
        (ROOT/f'{name}.svg').write_text(svg, encoding='utf-8')
    print(f'Wrote {len(SCENES)} original learning scenes.')


if __name__ == '__main__':
    main()
