"""Small, bundled grammar reference; independent of AI and external APIs."""
import copy
import json
from functools import lru_cache
from .foundation_content import ROOT, source_url


@lru_cache(maxsize=1)
def _reference():
    data = json.loads((ROOT / 'grammar_reference.json').read_text(encoding='utf-8'))
    if data.get('version') != 1:
        raise ValueError('Unsupported grammar reference version')
    for collection, key in [('verbs', 'base'), ('tenses', 'id'), ('comparisons', 'id')]:
        rows = data[collection]
        if not rows or len({r[key] for r in rows}) != len(rows):
            raise ValueError(f'Empty or duplicate grammar reference: {collection}')
    for row in data['verbs']:
        if not row['meaning_vi'] or any(not row[k] or not all(isinstance(s, str) and s for s in row[k]) for k in ('past', 'participle')):
            raise ValueError('Missing verb forms')
    for row in data['tenses']:
        if not all(row.get(k) for k in ('title','uses','example','translation_vi','note')) or set(row['forms']) != {'affirmative','negative','question'}:
            raise ValueError('Incomplete tense guide')
    for row in data['comparisons']:
        if not row['tip'] or len(row['sides']) != 2 or not all(all(side.get(k) for k in ('title','use','example','translation_vi')) for side in row['sides']):
            raise ValueError('Incomplete tense comparison')
    for guide in data['lesson_guides'].values():
        for key in ('tenses', 'comparisons'):
            if not set(guide[key]) <= {r['id'] for r in data[key]}:
                raise ValueError('Unknown grammar reference')
    if not all(source_url(url) for url in data['source_urls']):
        raise ValueError('Invalid reference source')
    return data


def reference():
    return copy.deepcopy(_reference())


def lesson_guide(unit_id):
    data = reference()
    mapping = data['lesson_guides'].get(unit_id)
    if not mapping:
        return None
    return {key: [r for r in data[key] if r['id'] in mapping[key]] for key in ('tenses', 'comparisons')}
