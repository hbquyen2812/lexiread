"""Original learning guides, loaded locally without network or account state."""
from copy import deepcopy
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
import re

from .public_resources import official_resource_url

GUIDES_PATH = Path(__file__).resolve().parents[2] / 'data/strategy_guides.json'


def _text(value, label, limit=1200):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'Invalid guide {label}')


def validate_strategy_guides(raw):
    if not isinstance(raw, dict) or raw.get('schema_version') != 1:
        raise ValueError('Unsupported strategy guide schema')
    guides = raw.get('guides')
    if not isinstance(guides, list) or not 1 <= len(guides) <= 100:
        raise ValueError('Expected 1–100 strategy guides')
    ids = set()
    for guide in guides:
        if not isinstance(guide, dict):
            raise ValueError('Guide must be an object')
        key = guide.get('id')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key) or key in ids:
            raise ValueError('Invalid or duplicate guide id')
        ids.add(key)
        if guide.get('exam') not in ('ielts', 'toeic'):
            raise ValueError('Unknown guide exam')
        _text(guide.get('title'), 'title', 180)
        _text(guide.get('summary_vi'), 'summary', 600)
        minutes = guide.get('duration_minutes')
        if type(minutes) is not int or not 1 <= minutes <= 60:
            raise ValueError('Invalid guide duration')
        kinds = guide.get('question_types')
        if not isinstance(kinds, list) or not 1 <= len(kinds) <= 12:
            raise ValueError('Invalid question types')
        for kind in kinds:
            _text(kind, 'question type', 100)
        steps = guide.get('steps')
        if not isinstance(steps, list) or not 2 <= len(steps) <= 8:
            raise ValueError('Expected 2–8 guide steps')
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError('Guide step must be an object')
            _text(step.get('title'), 'step title', 180)
            _text(step.get('body'), 'step body')
        traps = guide.get('traps')
        if not isinstance(traps, list) or not 1 <= len(traps) <= 8:
            raise ValueError('Invalid guide pitfalls')
        for trap in traps:
            _text(trap, 'pitfall', 600)
        example = guide.get('worked_example')
        if not isinstance(example, dict):
            raise ValueError('Missing worked example')
        for field, limit in [('passage', 4000), ('question', 1200), ('answer', 600), ('explanation_vi', 2500)]:
            _text(example.get(field), f'example {field}', limit)
        options = example.get('options')
        if options is not None:
            if not isinstance(options, list) or not 2 <= len(options) <= 8:
                raise ValueError('Invalid example options')
            for option in options:
                _text(option, 'example option', 600)
            if len(options) != len(set(options)) or example['answer'] not in options:
                raise ValueError('Example answer must match one unique option')
        accepted = example.get('accepted_answers')
        if accepted is not None:
            if options is not None or not isinstance(accepted, list) or not 1 <= len(accepted) <= 8:
                raise ValueError('Accepted answers are only valid for text examples')
            for answer in accepted:
                _text(answer, 'accepted example answer', 600)
            if len(accepted) != len(set(accepted)) or example['answer'] not in accepted:
                raise ValueError('Accepted answers must include the displayed answer')
        practice = guide.get('practice_query')
        if not isinstance(practice, dict) or practice.get('track') != guide['exam']:
            raise ValueError('Practice track must match the guide exam')
        if 'kind' in practice:
            _text(practice['kind'], 'practice kind', 100)
        sources = guide.get('sources')
        if not isinstance(sources, list) or not 1 <= len(sources) <= 6:
            raise ValueError('Missing guide sources')
        for source in sources:
            if not isinstance(source, dict) or not official_resource_url(source.get('url')):
                raise ValueError('Guide source must use an allowlisted official HTTPS URL')
            _text(source.get('title'), 'source title', 250)
        try:
            date.fromisoformat(guide.get('checked_at', ''))
        except (TypeError, ValueError):
            raise ValueError('Invalid guide verification date') from None
    return deepcopy(guides)


@lru_cache(maxsize=1)
def _guides():
    return validate_strategy_guides(json.loads(GUIDES_PATH.read_text(encoding='utf-8')))


def strategy_guides(exam=None):
    if exam not in (None, 'ielts', 'toeic'):
        raise ValueError('Unknown guide exam')
    return deepcopy([guide for guide in _guides() if exam is None or guide['exam'] == exam])


def strategy_guide(guide_id):
    return next((guide for guide in strategy_guides() if guide['id'] == guide_id), None)
