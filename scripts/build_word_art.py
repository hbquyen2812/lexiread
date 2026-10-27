"""Original small SVG objects, matching the existing LexiRead illustration palette."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'static' / 'illustrations' / 'words'
DRAWINGS = {
    'book': '<path d="M33 47q25-10 47 4 23-14 47-4v70q-25-9-47 5-24-14-47-5Z" fill="#fffdf4"/><path d="M80 52v68M43 65h25m-25 12h25m24-12h24m-24 12h24"/>',
    'calendar': '<rect x="38" y="42" width="84" height="80" rx="12" fill="#fffdf4"/><path d="M38 63h84"/><path d="M56 34v18m48-18v18" stroke-width="7"/><path d="m61 91 13 12 27-30" stroke="#689372" stroke-width="7"/>',
    'clock': '<circle cx="80" cy="81" r="43" fill="#fffdf4"/><path d="M80 52v30l20 12" stroke-width="6"/><path d="M80 43v4m38 34h-4M80 119v-4M42 81h4"/>',
    'coffee': '<path d="M42 65h68v28q0 26-34 26T42 93Z" fill="#d8996f"/><path d="M111 70h9q24 22-10 30M35 125h82M65 49q-12-9 0-21m24 21q-12-9 0-21" fill="none"/><path d="M64 85v3m22-3v3m-17 11q8 7 16 0"/>',
    'apple': '<path d="M79 57q-38-27-45 13c-6 42 28 61 46 47 18 14 52-5 46-47-7-40-45-13-47-13Z" fill="#d68e76"/><path d="M80 55q-2-18 9-28"/><path d="M82 40q25-24 35-2-19 17-35 2" fill="#92ac7d"/><path d="M54 75q-7 11-3 23" stroke="#ffe4cc" stroke-width="7"/>',
    'house': '<path d="m26 75 54-45 54 45" fill="#d8996f"/><path d="M38 67v58h84V67" fill="#fffdf4"/><path d="M68 125V91h26v34" fill="#aac4ac"/><rect x="48" y="79" width="13" height="16" rx="2" fill="#ebc97f"/>',
    'plant': '<path d="m53 95 8 38h39l9-38Z" fill="#d8996f"/><path d="M80 95V47"/><path d="M80 80Q33 83 41 48q33 1 39 32M80 61q0-36 36-31 4 28-36 31" fill="#94ae83"/>',
    'laptop': '<rect x="35" y="37" width="92" height="70" rx="8" fill="#aac4ac"/><rect x="43" y="45" width="76" height="53" rx="3" fill="#fffdf4"/><path d="m35 108-13 18h119l-14-18" fill="#aac4ac"/><path d="M60 117h43M56 62h47m-47 13h30"/>',
    'letter': '<rect x="27" y="48" width="106" height="73" rx="10" fill="#fffdf4"/><path d="m28 52 52 42 52-42M29 117l35-33m67 33L97 84"/><path d="M109 31h15m-7-7v14" stroke="#d8996f"/>',
    'receipt': '<path d="M47 27h66v109l-11-7-11 7-11-7-11 7-11-7-11 7Z" fill="#fffdf4"/><path d="M60 49h39M60 62h27M60 80h13m18 0h8M60 96h13m18 0h8"/>',
    'travel': '<rect x="37" y="50" width="86" height="78" rx="13" fill="#ebc97f"/><path d="M62 49V33h36v16M57 55v68m45-68v68M55 129v5m52-5v5"/><rect x="72" y="74" width="16" height="24" rx="3" fill="#fffdf4" transform="rotate(-13 80 86)"/>',
    'people': '<circle cx="60" cy="57" r="19" fill="#ebcfa5"/><circle cx="103" cy="63" r="16" fill="#d8996f"/><path d="M25 119V98q35-35 70 0v21Z" fill="#aac4ac"/><path d="M95 92q30-9 39 17v12H95" fill="#ebc97f"/><path d="M54 56h1m10 0h1m-11 9q5 4 10 0"/>',
    'cards': '<rect x="45" y="32" width="72" height="98" rx="10" fill="#aac4ac" transform="rotate(13 81 81)"/><rect x="35" y="37" width="72" height="98" rx="10" fill="#fffdf4" transform="rotate(-9 71 86)"/><path d="m64 66 7-14 7 14 15 2-11 10 3 15-14-7-13 7 2-15-10-10Z" fill="#ebc97f" stroke-width="2"/><path d="M52 108h32"/>',
    'compass': '<circle cx="80" cy="85" r="42" fill="#fffdf4"/><path d="M69 43V29h22v14" fill="#ebc97f"/><path d="m98 61-9 32-29 17 11-34Z" fill="#d8996f"/><path d="m98 61-18 24-20 25"/><circle cx="80" cy="85" r="4" fill="#365e50"/>',
    'folder': '<path d="M26 52V43h43l14 14h51v68H26Z" fill="#aac4ac"/><path d="m26 66 12 60h96l8-60Z" fill="#fffdf4"/><path d="m68 91 12-12 12 12m-12-12v32" stroke="#d8996f" stroke-width="5"/>',
    'pencil': '<path d="m42 113 8-26 54-54 19 19-54 54Z" fill="#ebc97f"/><path d="m50 87 19 19M42 113l17-5m40-69 19 19M58 92l46-46"/><path d="m104 33 8-8q4-4 8 0l11 11q4 4 0 8l-8 8Z" fill="#d8996f"/>',
}

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for key, body in DRAWINGS.items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" width="160" height="160"><rect width="160" height="160" rx="32" fill="#f1f3e9"/><circle cx="124" cy="31" r="13" fill="#efe0bd"/><ellipse cx="80" cy="135" rx="48" ry="6" fill="#dfe7d9"/><g stroke="#456557" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>\n'
        (ROOT / f'{key}.svg').write_text(svg, encoding='utf-8')
    print(f'Wrote {len(DRAWINGS)} original word illustrations.')

if __name__ == '__main__':
    main()
