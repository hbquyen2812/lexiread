"""Bounded, cached word lookups; no passage or account data leaves the server."""
import hashlib
import json
import re
import time
from urllib.parse import parse_qs, quote, unquote, urlsplit

import httpx
from django.core.cache import cache

from .core import InputError

ENDPOINT = 'https://api.dictionaryapi.dev/api/v2/entries/en/'
COMMONS_API = 'https://commons.wikimedia.org/w/api.php'
USER_AGENT = 'LexiRead/1.0 (https://github.com/hbquyen2812/lexiread)'


def lookup_word(value):
    if not isinstance(value, str):
        raise InputError('Chọn một từ hoặc cụm từ tiếng Anh ngắn để tra.')
    value = ' '.join(value.replace('’', "'").strip(' \t\r\n\".,;:!?“”()[]{}').split()).lower()
    if len(value) > 160 or len(value.split()) > 12 or not re.fullmatch(r"[^\W_][\w '\-().,]*", value, re.UNICODE) or '_' in value:
        raise InputError('Chọn một từ hoặc cụm từ tiếng Anh ngắn để tra.')
    return value


def text(value, limit=1200):
    return value[:limit].strip() if isinstance(value, str) else ''


def safe_url(value, hosts, prefix='/'):
    if not isinstance(value, str):
        return ''
    try:
        url = urlsplit(value)
        if (url.scheme == 'https' and url.hostname in hosts and not url.username and not url.password
                and url.port in (None, 443) and url.path.startswith(prefix)):
            return value
    except ValueError:
        pass
    return ''


def license_info(raw):
    raw = raw if isinstance(raw, dict) else {}
    url = safe_url(raw.get('url'), {'creativecommons.org'}, '/licenses/')
    return {'name': text(raw.get('name'), 100), 'url': url} if url else None


def dictionary_links(word):
    encoded = quote(word, safe='')
    return [
        {'title': 'Cambridge Dictionary', 'url': 'https://dictionary.cambridge.org/search/english/direct/?q=' + encoded},
        {'title': 'Oxford Learner’s Dictionaries', 'url': 'https://www.oxfordlearnersdictionaries.com/search/english/?q=' + encoded},
    ]


def sanitize_entries(payload):
    entries = []
    for raw in (payload[:3] if isinstance(payload, list) else []):
        if not isinstance(raw, dict):
            continue
        license = license_info(raw.get('license'))
        sources = [url for value in raw.get('sourceUrls', [])[:4]
                   if (url := safe_url(value, {'en.wiktionary.org'}, '/wiki/'))] if isinstance(raw.get('sourceUrls'), list) else []
        if not license or not sources:
            continue
        phonetics = []
        for p in (raw.get('phonetics', [])[:8] if isinstance(raw.get('phonetics'), list) else []):
            if not isinstance(p, dict):
                continue
            ipa = text(p.get('text'), 160)
            if '-' in ipa or '…' in ipa:  # Some source records contain a partial transcription.
                ipa = ''
            audio_license = license_info(p.get('license'))
            source = safe_url(p.get('sourceUrl'), {'commons.wikimedia.org'})
            audio = safe_url(p.get('audio'), {'api.dictionaryapi.dev'}, '/media/pronunciations/en/')
            if not audio_license or not source or not audio.endswith('.mp3'):
                audio = ''
            accent = next((a.upper() for a in ('uk', 'us', 'au') if audio.endswith('-' + a + '.mp3')), '')
            if ipa or audio:
                item = {'ipa': ipa, 'audio': audio, 'accent': accent, 'source': source if audio else '',
                        'license': audio_license if audio else None}
                if not any(x['ipa'] == ipa and x['audio'] == audio for x in phonetics):
                    phonetics.append(item)
        if not phonetics:
            ipa = text(raw.get('phonetic'), 160)
            if ipa and '-' not in ipa and '…' not in ipa:
                phonetics.append({'ipa': ipa, 'audio': '', 'accent': '', 'source': '', 'license': None})
        # Prefer a transcription paired with a recording; remove duplicate text-only versions.
        recorded = {p['ipa'] for p in phonetics if p['audio']}
        phonetics = [p for p in phonetics if p['audio'] or p['ipa'] not in recorded][:4]
        meanings = []
        for m in (raw.get('meanings', [])[:6] if isinstance(raw.get('meanings'), list) else []):
            if not isinstance(m, dict):
                continue
            definitions = []
            for d in (m.get('definitions', [])[:12] if isinstance(m.get('definitions'), list) else []):
                if isinstance(d, dict) and text(d.get('definition')):
                    definitions.append({'definition': text(d['definition']), 'example': text(d.get('example'))})
            if definitions:
                meanings.append({'pos': text(m.get('partOfSpeech'), 40), 'definitions': definitions})
        if meanings:
            entries.append({'word': text(raw.get('word'), 80), 'phonetics': phonetics, 'meanings': meanings,
                            'license': license, 'sources': sources})
    return entries


def resolve_recordings(entries):
    """Resolve at most two licensed recordings to their original Commons files."""
    groups = {'pageids': {}, 'titles': {}}
    recordings = [p for entry in entries for p in entry['phonetics'] if p['audio']][:2]
    for recording in recordings:
        source = urlsplit(recording['source'])
        pageid = parse_qs(source.query).get('curid', [''])[0]
        if pageid.isdigit() and len(pageid) <= 12:
            groups['pageids'].setdefault(pageid, []).append(recording)
        elif source.path.startswith('/wiki/File:'):
            title = unquote(source.path[len('/wiki/'):]).replace('_', ' ')
            if len(title) <= 250 and '|' not in title:
                groups['titles'].setdefault(title, []).append(recording)
    for field, refs in groups.items():
        if not refs:
            continue
        try:
            with httpx.Client(timeout=httpx.Timeout(4, connect=3), follow_redirects=False, trust_env=False) as client:
                with client.stream('GET', COMMONS_API, params={'action': 'query', 'format': 'json',
                        'prop': 'imageinfo', 'iiprop': 'url|mime', field: '|'.join(refs)},
                        headers={'Accept': 'application/json', 'User-Agent': USER_AGENT}) as response:
                    if response.status_code != 200 or 'application/json' not in response.headers.get('content-type', ''):
                        continue
                    content = bytearray()
                    started = time.monotonic()
                    for chunk in response.iter_bytes():
                        content.extend(chunk)
                        if len(content) > 128_000 or time.monotonic() - started > 5:
                            raise ValueError('Recording metadata too large or slow')
            pages = json.loads(content).get('query', {}).get('pages', {})
            for page in (pages.values() if isinstance(pages, dict) else []):
                if not isinstance(page, dict) or page.get('ns') != 6:
                    continue
                key = str(page.get('pageid')) if field == 'pageids' else page.get('title')
                info = page.get('imageinfo')
                if key not in refs or not isinstance(info, list) or not info or not isinstance(info[0], dict):
                    continue
                url = safe_url(info[0].get('url'), {'upload.wikimedia.org'}, '/wikipedia/commons/')
                if not url or info[0].get('mime') not in ('audio/ogg', 'audio/mpeg', 'audio/wav', 'application/ogg'):
                    continue
                parsed = urlsplit(url)
                if not parsed.path.lower().endswith(('.ogg', '.mp3', '.wav')):
                    continue
                for recording in refs[key]:
                    recording['audio'] = parsed._replace(query='', fragment='').geturl()
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            continue  # Definitions and the original provider URL remain usable.
    return entries


def fetch_remote(word):
    started = time.monotonic()
    with httpx.Client(timeout=httpx.Timeout(4, connect=3), follow_redirects=False, trust_env=False) as client:
        with client.stream('GET', ENDPOINT + quote(word, safe='') + '/', headers={'Accept': 'application/json'}) as response:
            # A CDN error page is not evidence that the word is absent.
            if 'application/json' not in response.headers.get('content-type', ''):
                return {'status': 'unavailable', 'entries': []}
            if response.status_code == 404:
                return {'status': 'not_found', 'entries': []}
            if response.status_code != 200:
                return {'status': 'unavailable', 'entries': []}
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)
                if len(content) > 512_000 or time.monotonic() - started > 8:
                    return {'status': 'unavailable', 'entries': []}
    entries = resolve_recordings(sanitize_entries(json.loads(content)))
    return {'status': 'ok' if entries else 'not_found', 'entries': entries}


def remote_lookup(word, user_id):
    key = 'dictionary-v1:' + hashlib.sha256(word.encode()).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        return cached
    # Limit cache misses per account. Cached vocabulary remains available.
    budget = 'dictionary-budget:' + str(user_id)
    cache.add(budget, 0, 60)
    try:
        used = cache.incr(budget)
    except ValueError:
        cache.set(budget, 1, 60); used = 1
    if used > 30:
        return {'status': 'rate_limited', 'entries': []}
    try:
        result = fetch_remote(word)
    except (httpx.HTTPError, ValueError, TypeError):
        result = {'status': 'unavailable', 'entries': []}
    cache.set(key, result, 86400 if result['status'] == 'ok' else 3600 if result['status'] == 'not_found' else 15)
    return result
