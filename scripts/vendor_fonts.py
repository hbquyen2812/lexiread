"""Vendor official Noto font builds and subset Latin/Vietnamese for local serving.

Maintenance only: requires fonttools[woff]. No font download happens in the app.
"""
from pathlib import Path
import re
from urllib.request import Request, urlopen
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'static/fonts'
TEMP = ROOT / 'data/private/font-build'
CSS_URL = 'https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&family=Noto+Serif:wght@500;600&display=swap'


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0 Chrome/131.0.0.0 Safari/537.36'}), timeout=30) as response:
        return response.read()


def vendor_ui_font():
    """Keep Vietnamese UI fonts local, with the upstream redistribution license."""
    DEST.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    base = 'https://raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/'
    faces = []
    for weight, name in [(400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')]:
        source = TEMP / f'BeVietnamPro-{name}.ttf'
        source.write_bytes(fetch(base + source.name))
        font = TTFont(source)
        font.flavor = 'woff2'
        output = DEST / f'be-vietnam-pro-{weight}.woff2'
        font.save(output)
        faces.append(f"@font-face{{font-family:'Be Vietnam Pro';font-style:normal;font-weight:{weight};font-display:swap;src:url('/static/fonts/{output.name}') format('woff2')}}")
        print(output.name, output.stat().st_size)
    (DEST / 'bevietnampro-OFL.txt').write_text(fetch(base + 'OFL.txt').decode('utf-8'), encoding='utf-8')
    path = ROOT / 'static/fonts.css'
    current = [line for line in path.read_text(encoding='utf-8').splitlines() if "font-family:'Be Vietnam Pro'" not in line]
    path.write_text('\n'.join(current + faces) + '\n', encoding='utf-8')


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    css = fetch(CSS_URL).decode()
    faces = []
    for block in re.findall(r'@font-face\s*\{([^}]+)\}', css):
        family = re.search(r"font-family:\s*'([^']+)'", block)[1]
        weight = re.search(r'font-weight:\s*(\d+)', block)[1]
        url = re.search(r'src:\s*url\((https://fonts.gstatic.com/[^)]+)\)', block)[1]
        slug = family.lower().replace(' ', '-') + '-' + weight
        source = TEMP / (slug + '.ttf')
        source.write_bytes(fetch(url))
        font = TTFont(source)
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = ['*']
        sub = subset.Subsetter(options=opts)
        sub.populate(unicodes=[i for a,b in [(0,0x24f),(0x300,0x36f),(0x1e00,0x1eff),(0x2000,0x206f),(0x20a0,0x20cf)] for i in range(a,b+1)])
        sub.subset(font)
        font.flavor = 'woff2'
        output = DEST / (slug + '.woff2')
        font.save(output)
        faces.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;src:url('/static/fonts/{output.name}') format('woff2')}}")
        print(output.name, output.stat().st_size)
    for family in ('notosans', 'notoserif'):
        license_text=fetch('https://raw.githubusercontent.com/google/fonts/main/ofl/' + family + '/OFL.txt').decode('utf-8')
        (DEST / (family + '-OFL.txt')).write_text('\n'.join(line.rstrip() for line in license_text.splitlines())+'\n',encoding='utf-8')
    (ROOT / 'static/fonts.css').write_text('\n'.join(faces)+'\n', encoding='utf-8')
    vendor_ui_font()


if __name__ == '__main__':
    main()
