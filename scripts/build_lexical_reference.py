"""Reproducible, offline conversion of licensed lexical relations (no inferred families)."""
import gzip
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/lexical'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
POS = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}


def checked(path, expected):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, f'Checksum mismatch: {path.name}'
    return raw


def wordnet():
    path = ROOT / 'data/dictionaries/english-wordnet-2025-json.zip'
    manifest = json.loads((path.parent / 'manifest.json').read_text(encoding='utf8'))
    entries, synsets = {}, {}
    with zipfile.ZipFile(io.BytesIO(checked(path, manifest['sha256']))) as z:
        for name in z.namelist():
            if name.endswith('.json'):
                data = json.loads(z.read(name))
                (entries if name.startswith('entries-') else synsets).update(data)
    senses = {}
    for word, variants in entries.items():
        if not re.fullmatch(r"[a-z][a-z '-]{1,79}", word):
            continue
        for pos, entry in variants.items():
            for sense in entry.get('sense', []):
                senses[sense['id']] = (word, POS.get(pos[0], pos), sense)
    # Each edge is an actual source relation, not a transitive cluster or a shared suffix.
    pairs = {}
    for sid, (word, pos, sense) in senses.items():
        for relation in ('derivation', 'pertainym'):
            for target in sense.get(relation, []):
                if target not in senses:
                    continue
                related, target_pos, target_sense = senses[target]
                if related == word:
                    continue
                key = (word, related, pos, target_pos, relation)
                reverse = (related, word, target_pos, pos, relation)
                if reverse in pairs:
                    continue
                if key not in pairs:
                    pairs[key] = dict(kind='family', source='oewn-2025', headword=word, related=related,
                        relation=relation, rank=0, detail={'head_pos': pos, 'related_pos': target_pos, 'senses': []})
                evidence = dict(head_id=sid, related_id=target,
                    head_gloss='; '.join(synsets.get(sense['synset'], {}).get('definition', [])),
                    related_gloss='; '.join(synsets.get(target_sense['synset'], {}).get('definition', [])))
                evidence_list = pairs[key]['detail']['senses']
                if evidence not in evidence_list and len(evidence_list) < 3:
                    evidence_list.append(evidence)
    return list(pairs.values())


def spreadsheet_rows(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        strings = [''.join(el.itertext()) for el in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row', NS):
            result = {}
            for cell in row.findall('m:c', NS):
                value = cell.find('m:v', NS)
                text = '' if value is None else value.text or ''
                if cell.get('t') == 's' and text:
                    text = strings[int(text)]
                text = re.sub(r'_x000D_', '', text).strip()
                result[re.sub(r'\d+', '', cell.get('r'))] = text
            yield result


def collocaid():
    raw = checked(OUT / 'collocaid-sample-v2.zip', '9c9689ab83653f76765979107423e193ebb281739ec47a1f7e1cf211bd42d880')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = next(n for n in z.namelist() if 'DatabaseSample' in n)
        rows = list(spreadsheet_rows(z.read(name)))[1:]
    result = []
    for row in rows:
        if not row.get('B') or not row.get('F'):
            continue
        result.append(dict(kind='collocation', source='collocaid-v2', headword=row['B'].lower(),
            related=row['F'].lower(), relation=row['E'], rank=float(row.get('J') or 0), detail=dict(
                source_id=row['A'], head_pos={'n':'noun','j':'adjective','v':'verb'}.get(row.get('D'), ''),
                sense=row.get('C', ''), following=row.get('G', ''), pattern=row.get('H', ''),
                count=int(row.get('I') or 0), examples=[row[c] for c in ('K','L','M') if row.get(c)])))
    return result


def build():
    rows = collocaid() + wordnet()
    for row in rows:
        identity = [row['source'], row['headword'], row['related'], row['relation'], row['detail']]
        row['key'] = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    rows = list({r['key']: r for r in rows}.values())
    rows.sort(key=lambda r: r['key'])
    raw = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rows)+'\n').encode()
    packed = gzip.compress(raw, mtime=0)
    (OUT / 'reference.jsonl.gz').write_bytes(packed)
    ewt = json.loads((OUT / 'ewt/phrases-manifest.json').read_text(encoding='utf8'))
    manifest = dict(version=1, sha256=hashlib.sha256(packed).hexdigest(), counts={**dict(Counter(r['kind'] for r in rows)), 'corpus':ewt['rows']},
        files=[dict(path='reference.jsonl.gz',sha256=hashlib.sha256(packed).hexdigest()),
               dict(path='ewt/phrases.jsonl.gz',sha256=ewt['sha256'])],
        sources=[dict(id='collocaid-v2', title='ColloCaid Sample Data (version 2)',
            url='https://doi.org/10.6084/m9.figshare.13028207.v2', license='CC BY 4.0',
            attribution='Ana Frankenberg-Garcia, Geraint Rees, Robert Lew, Jonathan Roberts, Peter Butcher',
            archive_sha256='9c9689ab83653f76765979107423e193ebb281739ec47a1f7e1cf211bd42d880',
            downloaded_at='2026-10-28', download_url='https://ndownloader.figshare.com/files/26706641',
            scope='Public sample only. 691 populated rows, 689 unique records; source description reports 692. Two exact duplicates removed. No access to the full database.'),
        dict(id='oewn-2025', title='Open English WordNet 2025', url='https://en-word.net/',
            license='CC BY 4.0 + Princeton WordNet license', attribution='Open English WordNet Team; Princeton University WordNet',
            scope='Direct derivation/pertainym edges only; sense evidence retained. Not CEFR-rated teaching families.'),
        dict(id='ewt-2.18',title='UD English Web Treebank 2.18',url='https://universaldependencies.org/treebanks/en_ewt/index.html',
            license='CC BY-SA 4.0',attribution='UD English EWT contributors; full credits and license in data/lexical/ewt/README.md and LICENSE.txt',
            revision='b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c',
            scope='Automatically extracted dependency pairs appearing in at least two eligible sentences; retained examples and sentence IDs. Not curated collocations or CEFR ratings. Derived corpus file is CC BY-SA 4.0, separate from other sources.')])
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(manifest['counts'], 'bytes', len(packed))


if __name__ == '__main__':
    build()
