"""Reviewed, metadata-only catalog of external official practice resources.

No network or database access is performed during a learner's request.
Exam passages, questions and answer keys remain on the publisher's site.
"""
from copy import deepcopy
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

CATALOG_PATH = Path(__file__).resolve().parents[2] / 'data/public_sources/catalog.json'
OFFICIAL_HOSTS = frozenset({'ielts.org', 'www.ielts.org', 'cdn.ielts.org',
    'takeielts.britishcouncil.org', 'ielts.idp.com', 'www.ets.org',
    'ielts.inspera.com', 'demo-ielts.inspera.com', 'www.iibc-global.org'})
URL_FIELDS = ('url', 'source_url', 'answer_url')
TEXT_FIELDS = ('title', 'publisher', 'variant', 'description_vi', 'rights', 'access')


def official_resource_url(value):
    if not isinstance(value, str) or not value or len(value) > 2000:
        return False
    try:
        p = urlsplit(value)
        return (p.scheme == 'https' and p.hostname in OFFICIAL_HOSTS
                and p.port in (None, 443) and not p.username and not p.password
                and not any(ord(c) < 32 for c in value))
    except ValueError:
        return False


def validate_catalog(raw):
    if not isinstance(raw, dict) or raw.get('schema_version') != 1:
        raise ValueError('Unsupported public resource catalog version')
    rows = raw.get('resources')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200:
        raise ValueError('Expected 1–200 reviewed resources')
    ids, urls = set(), set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Resource must be an object')
        key = row.get('id', '')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key) or key in ids:
            raise ValueError('Invalid or duplicate resource id')
        ids.add(key)
        if row.get('exam') not in ('ielts', 'toeic') or row.get('format') not in ('pdf', 'interactive', 'collection'):
            raise ValueError('Invalid exam or resource format')
        for field in TEXT_FIELDS:
            if not isinstance(row.get(field), str) or not 1 <= len(row[field]) <= 600:
                raise ValueError(f'Invalid resource field: {field}')
        for field in URL_FIELDS:
            if field == 'answer_url' and not row.get(field):
                continue
            if not official_resource_url(row.get(field)):
                raise ValueError(f'Unsafe or nonofficial resource URL: {field}')
        if row['url'] in urls:
            raise ValueError('Duplicate resource URL')
        urls.add(row['url'])
        for field in ('skills', 'question_types'):
            items = row.get(field)
            if not isinstance(items, list) or not 1 <= len(items) <= 20 or any(
                    not isinstance(x, str) or not 1 <= len(x) <= 80 for x in items):
                raise ValueError(f'Invalid resource list: {field}')
        try:
            date.fromisoformat(row.get('last_checked', ''))
        except (TypeError, ValueError):
            raise ValueError('Invalid resource verification date') from None
        if row.get('content_mode') != 'external_link' or row.get('verification') not in (
                'publisher_page_checked', 'target_checked'):
            raise ValueError('Resources must remain reviewed external links')
        if any(field in row for field in ('text', 'passage', 'questions', 'answers')):
            raise ValueError('Exam content is not permitted in this metadata catalog')
    return deepcopy(rows)


@lru_cache(maxsize=1)
def _catalog():
    return validate_catalog(json.loads(CATALOG_PATH.read_text(encoding='utf-8')))


def public_resources(exam=None):
    """Return template/JSON-ready cards, optionally filtered by exam."""
    if exam not in (None, 'ielts', 'toeic'):
        raise ValueError('Unknown exam filter')
    return deepcopy([row for row in _catalog() if exam is None or row['exam'] == exam])
