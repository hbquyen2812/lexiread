"""Original lightweight SVG illustrations for Lexivela's word-pattern lessons."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'static/illustrations/patterns'
ART = {
    'verb-noun': '''<path d="M143 178h60v-30h60v-30h60V88h73v90Z" fill="#c5d9ba"/><path d="M356 89V45m0 0h49l-12 15 12 15h-49" fill="#dca47c"/><circle cx="246" cy="80" r="19" fill="#efc69c"/><path d="M235 100q17-8 29 5l19 29-15 9-19-25-11 31-25 15-10-14 21-15Z" fill="#467b67"/><path d="m251 141 14 25 27 1m-57-15-8 27m20-100v2m10-2v2m-11 7q5 4 9 0" fill="none"/><path d="m174 96 7-9m-20 27-10-2" stroke="#c59758"/>''',
    'adjective-noun': '''<path d="M164 83q-10-26 17-32 3-30 32-26 28-6 40 24 31-2 33 25 0 15-20 15H183q-16 1-19-6Z" fill="#ccdadf"/><path d="m187 107-6 14m39-14-6 14m39-14-6 14m-82 15-6 14m48-10-6 14" stroke="#7b9bb3"/><path d="M236 134q57-91 113 0-19-10-38 0-18-11-38 0-18-9-37 0Z" fill="#e5b66f"/><path d="M292 91v87q-3 18-20 9" fill="none"/><path d="M346 176h25l9 19h-47l1-19h12v-35" fill="#b6caa9"/><path d="M335 142h24v34h-24Z" fill="#b6caa9"/>''',
    'adverb-adjective': '''<path d="M276 37v29m-66-3 15 19m118-19-15 19m-138 38h24m131 0h24" stroke="#d2a65d"/><path d="M251 159q3-23-10-39-20-42 22-55 44-14 58 23 10 25-10 50-8 8-7 21Z" fill="#f2d993"/><path d="M251 159h53v24h-53Z" fill="#8caf99"/><path d="M260 191h35m-18-32v-32l-17-14m17 14 18-14" fill="none"/><path d="M256 99v3m37-3v3m-30 13q13 11 22 0" fill="none"/><circle cx="371" cy="168" r="14" fill="#eac7ac"/><path d="m161 159 5-12 5 12 12 5-12 5-5 12-5-12-12-5Z" fill="#c5d5bd"/>''',
    'verb-preposition': '''<path d="M145 194q-3-46 63-57t58-55" fill="none" stroke="#d9c5a8" stroke-width="22"/><path d="M320 74v119"/><path d="M286 50h83l23 18-23 18h-83Z" fill="#a9cbb9"/><path d="M275 100h82v34h-82l-23-17Z" fill="#ecc591"/><path d="M305 68h53m-65 49h45" fill="none"/><path d="m191 168 24-8m9-10 24-8" stroke="#6d8b72"/><path d="M366 189q-18-34 6-43 27 18-6 43m0 0q-1-40 27-27 5 21-27 27" fill="#c2d3a8"/>''',
    'adjective-preposition': '''<circle cx="247" cy="75" r="25" fill="#edc4a0"/><path d="M216 173v-57q32-24 62 0v57Z" fill="#b9cdb5"/><path d="m223 120-31 18-17-22m98 6 26 15 26-37" fill="none" stroke-width="11"/><path d="M237 73v2m18-2v2m-17 11q9 6 17-1" fill="none"/><path d="m346 49 11 22 25 4-18 18 4 25-22-12-22 12 4-25-18-18 25-4Z" fill="#e6bd70"/><path d="m218 190 0-17m57 17v-17m115-47 10 4m-99-91 5 9" fill="none"/>''',
    'noun-preposition': '''<path d="M252 191V45h104v146" fill="#bbd3c2"/><path d="m265 59 77 11v121h-77Z" fill="#e4c19a"/><circle cx="328" cy="128" r="4" fill="#456557"/><circle cx="186" cy="111" r="24" fill="#f0d58d"/><circle cx="186" cy="111" r="8" fill="#fff9ed"/><path d="m205 127 42 42m-8-8 12-12m-25 0 11-11" fill="none" stroke="#c69a54" stroke-width="10"/><path d="M239 192h128"/><path d="m376 84 9-7m-13 28h15" stroke="#d0a971"/>''',
    'verb-adverb': '''<circle cx="214" cy="161" r="35" fill="#f7f7ed"/><circle cx="350" cy="161" r="35" fill="#f7f7ed"/><path d="m215 160 37-61 37 61h-74l51-40 84 41-29-78m-85 13h31m48-13h28" fill="none" stroke="#67927c" stroke-width="5"/><circle cx="291" cy="49" r="18" fill="#edc4a0"/><path d="m280 68-23 40 40 19-14 32m-14-76 33 14h24" fill="none" stroke="#c79b6d" stroke-width="12"/><path d="m158 94h49m-60 25h43m-47 26h26" fill="none" stroke="#c7d7c1"/><path d="M290 46v2m8-2v2"/>''',
    'noun-noun': '''<path d="M184 85h192v111H184Z" fill="#e5cfaa"/><path d="M175 69h210v34H175Z" fill="#a3c7b0"/><path d="M175 103q17 21 35 0 17 21 35 0 17 21 35 0 17 21 35 0 17 21 35 0 17 21 35 0" fill="#a3c7b0"/><path d="M211 133h58v63h-58Z" fill="#fff9ed"/><path d="M292 129h63v43h-63Z" fill="#dce7db"/><path d="M255 165h1" stroke-width="5"/><path d="M252 27h45v19q0 15-23 15t-22-15Z" fill="#dfb18c"/><path d="M298 30h8q11 13-10 17m-30-27q-6-7 0-13m16 13q-6-7 0-13" fill="none"/>''',
    'word-family': '''<path d="M280 178V84m0 51-54-40m54 19 55-44m-55 88 65-31" fill="none" stroke="#73976a" stroke-width="6"/><path d="M226 95q-48 0-45-42 52-2 45 42Z" fill="#bdd4aa"/><path d="M335 70q-2-40 42-39 3 43-42 39Z" fill="#b4d0b8"/><path d="M345 127q1-38 44-37 0 42-44 37Z" fill="#d6c58b"/><path d="M279 86q-34-32-5-63 35 31 5 63Z" fill="#c6d9a9"/><path d="M244 168h73l-11 34h-52Z" fill="#dba682"/><path d="M269 180v2m22-2v2m-16 9q6 4 12 0" fill="none"/>''',
}

OUT.mkdir(parents=True, exist_ok=True)
for name, drawing in ART.items():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 240" width="560" height="240">
<rect width="560" height="240" rx="24" fill="#f2f3e9"/><ellipse cx="280" cy="120" rx="173" ry="102" fill="#fffaf0"/>
<ellipse cx="280" cy="205" rx="146" ry="7" fill="#dfe6d7"/>
<g stroke="#456557" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{drawing}</g>
<g fill="#d6b574"><circle cx="116" cy="62" r="4"/><circle cx="430" cy="166" r="5"/></g></svg>'''
    (OUT/(name+'.svg')).write_text(svg+'\n',encoding='utf8')
print(f'{len(ART)} original pattern illustrations')
