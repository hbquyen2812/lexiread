"""Local dictionary queries and reproducible import of the licensed OEWN release."""
import hashlib
import base64
import copy
import gzip
import json
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

from django.db import transaction
from learning.models import (DictionaryEntry, DictionaryForm, DictionaryRelease, VocabularyCollection,
                             DictionaryAudio, DictionarySupplement)
from .foundation_content import _units

DATA = Path(__file__).resolve().parents[2] / 'data' / 'dictionaries'
SOURCE_URL = 'https://en-word.net/'
LICENSE = {'name': 'CC BY 4.0 · OEWN & Princeton WordNet', 'url': 'https://creativecommons.org/licenses/by/4.0/'}
POS = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}


def key(word):
    return ' '.join(unicodedata.normalize('NFKC', word).replace('’', "'").split()).casefold()


def seed_collections():
    created = 0
    for order, unit in enumerate(_units('vocabulary')):
        _, made = VocabularyCollection.objects.get_or_create(slug=unit['id'], defaults={
            'title': unit['title'], 'topic': unit['topic'], 'level': unit['level'], 'order': order, 'content': unit})
        created += made
    return created


def convert_archive(path):
    """Keep all senses, examples, pronunciations and explicit inflected forms; no model calls."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if sum(i.file_size for i in archive.infolist()) > 250_000_000:
            raise ValueError('Dictionary archive exceeds the import limit.')
        synsets = {}
        for name in names:
            if name.startswith(('noun.', 'verb.', 'adj.', 'adv.')) and name.endswith('.json'):
                synsets.update(json.loads(archive.read(name)))
        for name in names:
            if not name.startswith('entries-') or not name.endswith('.json'):
                continue
            for word, variants in json.loads(archive.read(name)).items():
                if not word or len(key(word)) > 160:
                    continue
                entries, forms = [], set()
                for pos, variant in variants.items():
                    meanings = []
                    for sense in variant.get('sense', []):
                        synset = synsets.get(sense['synset'], {})
                        examples = synset.get('example', [])
                        example_text = [x if isinstance(x, str) else x.get('text', '') for x in examples]
                        for definition in synset.get('definition', []):
                            meanings.append({'definition': definition, 'example': ' · '.join(example_text),
                                             'synset': sense['synset'], 'synonyms': synset.get('members', [])})
                    phonetics = [{'ipa': '/' + p['value'].strip('/') + '/', 'audio': '', 'accent': '',
                                  'source': '', 'license': None}
                                 for p in variant.get('pronunciation', []) if p.get('value')]
                    if meanings:
                        entries.append({'word': word, 'phonetics': phonetics, 'meanings': [
                            {'pos': POS.get(pos.split('-')[0], pos), 'definitions': meanings}],
                            'license': LICENSE, 'sources': [SOURCE_URL], 'source_label': 'Open English WordNet 2025'})
                    forms.update(key(f) for f in variant.get('form', []) if isinstance(f, str) and len(key(f)) <= 160)
                if entries:
                    yield key(word), word, entries, forms


def import_release(path=None):
    path = Path(path) if path else DATA / 'english-wordnet-2025-json.zip'
    manifest = json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))
    raw_checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    if raw_checksum != manifest['sha256']:
        raise ValueError('Dictionary checksum does not match the pinned release.')
    checksum = hashlib.sha256((raw_checksum + ':conversion-2').encode()).hexdigest()
    existing = DictionaryRelease.objects.filter(pk='oewn-2025', checksum=checksum).first()
    if existing and existing.entry_count and DictionaryEntry.objects.filter(release=existing).count() == existing.entry_count:
        return existing, False
    # Collapse case variants without dropping their senses.
    rows, aliases = {}, defaultdict(set)
    for normalized, display, entries, forms in convert_archive(path):
        if normalized in rows:
            if display == normalized:
                rows[normalized].content = entries + rows[normalized].content
                rows[normalized].display_word = display
                rows[normalized].definition = entries[0]['meanings'][0]['definitions'][0]['definition']
            else:
                rows[normalized].content.extend(entries)
        else:
            rows[normalized] = DictionaryEntry(word=normalized, display_word=display, content=entries,
                definition=entries[0]['meanings'][0]['definitions'][0]['definition'], release_id='oewn-2025')
        aliases[normalized].update(forms)
    with transaction.atomic():
        release, _ = DictionaryRelease.objects.update_or_create(pk='oewn-2025', defaults={
            'checksum': checksum, 'entry_count': len(rows),
            'ipa_count': sum(any(e['phonetics'] for e in row.content) for row in rows.values())})
        DictionaryEntry.objects.bulk_create(list(rows.values()), batch_size=400, update_conflicts=True,
            update_fields=['display_word', 'definition', 'content', 'release'], unique_fields=['word'])
        DictionaryForm.objects.filter(entry__release=release).delete()
        DictionaryForm.objects.bulk_create([DictionaryForm(form=f, entry_id=word)
            for word, forms in aliases.items() for f in forms if f != word], batch_size=1000, ignore_conflicts=True)
    return release, True


def lookup_local(word):
    normalized = key(word)
    row = DictionaryEntry.objects.filter(pk=normalized).first()
    supplement = DictionarySupplement.objects.filter(pk=normalized).first()
    if row or supplement:
        entries = copy.deepcopy(row.content if row else supplement.content)
        if supplement:
            # API transcriptions may describe a different dialect from the linked recording.
            # Keep OEWN IPA separately; don't claim an API transcription matches an audio file.
            sounds = [{**p, 'ipa': ''} for e in supplement.content for p in e.get('phonetics', []) if p.get('audio')]
            if not row:
                for entry in entries:
                    entry['phonetics'] = []
            if sounds:
                entries[0]['phonetics'] = entries[0].get('phonetics', []) + sounds
        return {'status': 'ok', 'entries': entries, 'storage': 'database'}
    matches = list(DictionaryEntry.objects.filter(forms__form=normalized).distinct()[:4])
    if matches:
        return {'status': 'ok', 'entries': [e for row in matches for e in row.content],
                'storage': 'database', 'base_words': [row.display_word for row in matches]}
    ready = DictionaryRelease.objects.filter(entry_count__gt=0).exists()
    return {'status': 'not_found' if ready else 'not_ready', 'entries': [], 'storage': 'database'}


def import_recordings():
    path = DATA/'pronunciation-pack.json.gz'
    if not path.exists():
        return 0
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    if DictionaryRelease.objects.filter(pk='pronunciation-v1',checksum=checksum).exists():
        return 0
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        pack = json.load(f)
    if pack.get('version') != 1:
        raise ValueError('Unsupported pronunciation pack')
    sounds = []
    for entries in pack['words'].values():
        for entry in entries:
            for phonetic in entry.get('phonetics', []):
                audio = phonetic.get('audio', '')
                if audio and (not audio.startswith('/api/dictionary/audio/') or
                              not audio.endswith('/') or audio.split('/')[-2] not in pack['audio']):
                    raise ValueError('Recording must refer to a file included in the local pack')
    for digest, row in pack['audio'].items():
        binary = base64.b64decode(row['data'], validate=True)
        if len(binary)>500_000 or hashlib.sha256(binary).hexdigest()!=digest:
            raise ValueError('Recording checksum or size invalid')
        if row['mime'] not in ('audio/ogg','application/ogg','audio/mpeg','audio/wav'):
            raise ValueError('Invalid recording MIME')
        sounds.append(DictionaryAudio(digest=digest, data=binary, mime=row['mime'],
            attribution={'source':row['source'], 'license':row['license']}))
    with transaction.atomic():
        DictionaryAudio.objects.bulk_create(sounds,batch_size=100,ignore_conflicts=True)
        DictionarySupplement.objects.bulk_create([DictionarySupplement(word=key(w),content=c)
            for w,c in pack['words'].items()],batch_size=200,update_conflicts=True,
            update_fields=['content'],unique_fields=['word'])
        DictionaryRelease.objects.update_or_create(pk='pronunciation-v1', defaults={
            'checksum':checksum,'entry_count':len(pack['words']),'ipa_count':len(sounds)})
    return len(sounds)


def search_local(q, page=1):
    normalized = key(q)
    # Exact and indexed prefix matches, then explicit inflections. No full JSON scans.
    rows = DictionaryEntry.objects.filter(word__startswith=normalized).only('word', 'display_word', 'definition')
    total = rows.count()
    items = list(rows[(page-1)*20:page*20])
    if not total and page == 1:
        items = list(DictionaryEntry.objects.filter(forms__form=normalized).distinct().only('word','display_word','definition')[:20])
        total = len(items)
    return {'items': [{'word': r.display_word, 'definition': r.definition} for r in items],
            'total': total, 'page': page, 'has_next': page*20 < total}
