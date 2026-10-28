"""Licensed reference data and original lessons. All learning requests stay local."""
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from .foundation_content import validate_unit, validate_questions

ROOT = Path(__file__).resolve().parents[2] / 'data/lexical'


@lru_cache(maxsize=1)
def lessons():
    data = json.loads((ROOT / 'lessons.json').read_text(encoding='utf8'))
    if data.get('version') != 1:
        raise ValueError('Unsupported lexical lesson version')
    seen = set()
    for row in data['collections']:
        validate_unit(row, 'vocabulary')
        validate_questions(row['questions'])
        if row['id'] in seen or row.get('track') != 'lexical_patterns':
            raise ValueError('Invalid or duplicate lexical lesson')
        seen.add(row['id'])
    return data['collections']


@lru_cache(maxsize=1)
def manifest():
    return json.loads((ROOT / 'manifest.json').read_text(encoding='utf8'))


def reference_rows():
    for pack in manifest()['files']:
        path = (ROOT / pack['path']).resolve()
        if not path.is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != pack['sha256']:
            raise ValueError('Lexical reference checksum mismatch')
        with gzip.open(path, 'rt', encoding='utf8') as stream:
            for line in stream:
                row = json.loads(line)
                if row['kind'] not in ('family', 'collocation', 'corpus') or not all(
                    isinstance(row[k], str) and 0 < len(row[k]) <= limit
                    for k, limit in [('key',64), ('headword',160), ('related',160), ('relation',40), ('source',40)]
                ):
                    raise ValueError('Invalid lexical reference row')
                yield row
