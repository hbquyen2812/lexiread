"""Versioned, offline v3 content. Imports are additive and preserve learner snapshots."""
import gzip
import hashlib
import json
from pathlib import Path

from learning.editorial.dataset import adapt_one
from learning.services.catalog import validate_lesson
from learning.services.toeic import validate_toeic_set
from learning.services.foundation_content import validate_questions

RELEASE = Path(__file__).resolve().parents[2] / 'data' / 'content_packs' / 'v3'


def load_release():
    manifest = json.loads((RELEASE / 'manifest.json').read_text(encoding='utf-8'))
    data = (RELEASE / 'lessons.json.gz').read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest['bundle_sha256']:
        raise ValueError('V3 content checksum does not match the release manifest.')
    pack = json.loads(gzip.decompress(data))
    if len(pack['lessons']) != manifest['counts']['lessons']:
        raise ValueError('V3 lesson count does not match the release manifest.')
    return pack, manifest


def release_slug(lesson_id, legacy_ids):
    return ('pack-v1-' if lesson_id in legacy_ids else 'pack-v3-') + lesson_id.replace('_', '-')


def converted_release(pack, manifest):
    legacy = set(manifest['legacy_ids'])
    seen = set()
    for index, source in enumerate(pack['lessons']):
        slug = release_slug(source['id'], legacy)
        if slug in seen:
            raise ValueError('Duplicate v3 lesson ID: ' + slug)
        seen.add(slug)
        kind = 'toeic' if source['track'] == 'toeic' else 'lesson'
        row = adapt_one(source, pack['metadata'], kind, slug=slug)
        row['published'] = True
        if kind == 'lesson':
            row['order'] = 1000 + index
            row = validate_lesson(row)
        else:
            row = validate_toeic_set(row)
        yield kind, row, vocabulary_collection(source, slug, manifest)


def vocabulary_collection(source, slug, manifest):
    # Keep all authored contextual senses and their distractors; do not invent translations.
    words = [{'word': v['term'], 'part_of_speech': v['pos'], 'meaning_vi': v['meaning_vi'],
              'example': v['example_en'], 'example_translation': '', 'usage_pattern': v['collocation'],
              'context': v['context_quote']} for v in source['vocabulary']]
    questions = []
    for q in source['vocabulary_questions']:
        options = q['options']
        questions.append({'id': q['id'], 'prompt': q['prompt_en'], 'prompt_lang': 'en',
                          'options': [o['text'] for o in options],
                          'answer': next(i for i, o in enumerate(options) if o['key'] == q['answer'][0]),
                          'explanation_vi': q['explanation_vi']})
    validate_questions(questions)
    if len(questions) != len(words) or not 4 <= len(words) <= 100:
        raise ValueError('Incomplete v3 vocabulary practice: ' + source['id'])
    return {'id': slug, 'title': source['title_en'], 'topic': source['topic'].replace('_', ' ').title(),
            'level': source['cefr_estimate'], 'description': source['title_vi'],
            'estimated_minutes': max(5, len(words)), 'words': words, 'questions': questions,
            'source_urls': [manifest['sources'][s] for s in source['source_ids']],
            'content_origin': 'original_ai_authored', 'source_lesson': slug,
            'track': source['track'], 'provenance': 'Từ vựng trong bài luyện do LexiRead biên soạn.'}
