"""Deterministic reading decks from existing bilingual material; no network or AI."""
import copy
import re
from collections import defaultdict

from django.core.cache import cache
from django.db.models import Q

from learning.models import DictionaryForm, Vocabulary, VocabularyCollection, VocabularyOccurrence
from .core import InputError, normalise, validate_entry
from .foundation_content import _units
from .storage import save_entry, serial_vocab

CACHE_KEY = 'lexiread:reading-deck-lexicon:v1'
WORD = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")
STOP = set('a an the this that these those i you he she it we they me him her us them my your his its our their and or but if as at by for from in into of on to with without is am are was were be been being have has had do does did can could will would shall should may might must not no yes so than then there here who whom which what when where how why very just also more most less only one two some any all each every both other such much many about because through during before after up out over under again'.split())


def tokens(text):
    return [match.group().replace('’', "'").lower() for match in WORD.finditer(text)]


def signature(text):
    return set(tokens(text)) - STOP


def lexicon():
    """Cache public vocabulary only. Never put learner text or private words in this cache."""
    saved = cache.get(CACHE_KEY)
    if saved is not None:
        return saved
    rows = VocabularyCollection.objects.values_list('content', flat=True)
    bank = defaultdict(list)
    for unit in rows.iterator(chunk_size=100) if rows.exists() else _units('vocabulary'):
        for word in unit.get('words', []):
            name, meaning = word.get('word', ''), word.get('meaning_vi', '')
            parts = tokens(name)
            if not name or not meaning or not 1 <= len(parts) <= 5:
                continue
            entry = {key: word.get(key, '') for key in ('word', 'meaning_vi', 'usage_pattern', 'context')}
            entry.update(pos=word.get('part_of_speech', ''), example=word.get('example', ''),
                         example_vi=word.get('example_translation', ''))
            key = ' '.join(parts)
            # Repeated teaching contexts can help choose the sense, but don't create duplicate cards.
            if entry not in bank[key]:
                bank[key].append(entry)
    result = dict(bank)
    cache.set(CACHE_KEY, result, 300)
    return result


def occurrences(text, wanted):
    """Match whole tokens/phrases, with explicit dictionary inflections for single words."""
    matches = list(WORD.finditer(text))
    terms = [m.group().replace('’', "'").lower() for m in matches]
    aliases = defaultdict(set)
    unknown = set(terms) - wanted - STOP
    for form, lemma in DictionaryForm.objects.filter(form__in=unknown).values_list('form', 'entry_id'):
        if lemma in wanted:
            aliases[form].add(lemma)
    found = defaultdict(list)
    for i, match in enumerate(matches):
        term = terms[i]
        for key in ({term} | aliases.get(term, set())) & wanted:
            found[key].append((match.start(), match.end()))
        for count in range(2, 6):
            if i + count > len(matches):
                break
            # A phrase must not jump over sentence boundaries or punctuation.
            if not text[matches[i + count - 2].end():matches[i + count - 1].start()].isspace():
                break
            phrase = ' '.join(terms[i:i + count])
            if phrase in wanted:
                found[phrase].append((match.start(), matches[i + count - 1].end()))
    return found


def context_at(text, start, end):
    left = max(text.rfind(mark, 0, start) for mark in ('. ', '! ', '? ', '\n'))
    left = left + (1 if text[left:left + 1] == '\n' else 2) if left >= 0 else 0
    ends = [pos + 1 for mark in ('.', '!', '?', '\n') if (pos := text.find(mark, end)) >= 0]
    right = min(ends) if ends else len(text)
    # Keep the matched word even in a very long, unpunctuated passage.
    if right - left > 1800:
        left, right = max(left, start - 500), min(right, end + 500)
    return text[left:right].strip()


def choose_sense(entries, context, word):
    senses = {}
    clues = signature(context) - signature(word)
    for entry in entries:
        meaning = normalise(entry['meaning_vi'])
        evidence = signature(' '.join(entry.get(k, '') for k in ('example', 'context', 'usage_pattern')))
        score = len(clues & (evidence - signature(word)))
        if meaning not in senses or score > senses[meaning][0]:
            senses[meaning] = (score, entry)
    ranked = sorted(senses.values(), key=lambda pair: -pair[0])
    if not ranked or (len(ranked) > 1 and ranked[0][0] == ranked[1][0]):
        return None  # Ambiguous stored senses are safer to skip than guess.
    return ranked[0][1]


def candidates(reading, limit=20):
    bank = lexicon()
    authored = {}
    for entry in (reading.analysis or {}).get('vocabulary', []):
        if isinstance(entry, dict) and entry.get('word') and entry.get('meaning_vi'):
            authored.setdefault(' '.join(tokens(entry['word'])), entry)
    wanted = set(bank) | set(authored)
    matches = occurrences(reading.text, wanted)
    ranked = []
    for key, spans in matches.items():
        if key in STOP or (len(key) < 3 and key not in authored):
            continue
        start, end = spans[0]
        context = context_at(reading.text, start, end)
        entry = authored.get(key) or choose_sense(bank.get(key, []), context, key)
        if not entry:
            continue
        fields = copy.deepcopy(entry)
        # This is the actual sentence from this reading, never a translated/generated quotation.
        fields.update(context=context, example=context, example_vi='', source_label=reading.title,
                      tags=['Bài đọc · ' + reading.title[:90]], origin='auto', verified=False)
        try:
            fields = validate_entry(fields)
        except InputError:
            continue
        score = (key in authored, len(key.split()) > 1, min(len(spans), 4), len(key))
        ranked.append((score, start, fields))
    ranked.sort(key=lambda row: (tuple(-int(v) for v in row[0]), row[1]))
    return [row[2] for row in ranked[:limit]]


def saved_cards(user, reading):
    return Vocabulary.objects.filter(owner=user).filter(
        Q(reading=reading) | Q(occurrences__owner=user, occurrences__reading=reading)
    ).distinct().order_by('due_at', 'id')


def deck_payload(user, reading, created=0):
    cards = saved_cards(user, reading)
    selected = list(cards[:100])
    contexts = {}
    for card_id, context in VocabularyOccurrence.objects.filter(
            owner=user, reading=reading, vocabulary_id__in=[card.pk for card in selected]
    ).order_by('created_at', 'pk').values_list('vocabulary_id', 'context'):
        if context and context in reading.text:
            contexts[card_id] = context
    items = []
    for card in selected:
        data = serial_vocab(card)
        context = contexts.get(card.pk, '')
        if not context and card.reading_id == reading.pk and card.context in reading.text:
            context = card.context
        # Presentation is source-specific; never overwrite the user's original card or schedule.
        data.update(reading_id=str(reading.pk), source_label=reading.title,
                    context=context, example=context, example_vi='')
        items.append(data)
    return {'reading': {'id': str(reading.pk), 'title': reading.title},
            'items': items,
            'total': cards.count(), 'created': created}


def create_deck(user, reading):
    created = 0
    for fields in candidates(reading):
        _, new = save_entry(user, fields, reading)
        created += int(new)
    result = deck_payload(user, reading, created)
    if not result['items']:
        raise InputError('Chưa tìm thấy từ có nghĩa sẵn trong bài này. Bạn có thể bôi đen từ để tra và lưu.')
    return result
