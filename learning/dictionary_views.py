from django.http import JsonResponse
import uuid

from .models import Reading, Vocabulary
from .services.dictionary import lookup_word, remote_lookup, dictionary_links
from .services.foundation_content import units, word_entry
from .views import api


@api('GET')
def lookup(request):
    word = lookup_word(request.GET.get('word', ''))
    local = []
    seen = set()

    def add(entry, label):
        if not isinstance(entry, dict) or str(entry.get('word', '')).casefold() != word:
            return
        meaning = entry.get('meaning_vi', '')
        if not meaning or meaning in seen or len(local) >= 6:
            return
        seen.add(meaning)
        fields = ('word', 'meaning_vi', 'pos', 'example', 'example_vi', 'usage_pattern', 'note')
        local.append({**{k: entry.get(k, '') for k in fields}, 'label': label})

    if request.GET.get('reading_id'):
        reading = Reading.objects.get(owner=request.user, pk=uuid.UUID(request.GET['reading_id']))
        for entry in (reading.analysis or {}).get('vocabulary', []):
            add(entry, 'Trong bài đang đọc')
    for entry in Vocabulary.objects.filter(owner=request.user, word__iexact=word).values()[:6]:
        add(entry, 'Kho từ của bạn')
    for unit in units('vocabulary'):
        for entry in unit['words']:
            if entry['word'].casefold() == word:
                add(word_entry(entry, unit), 'Kho học LexiRead')
    response = JsonResponse({'word': word, 'local_entries': local, 'dictionary': remote_lookup(word, request.user.pk),
                             'links': dictionary_links(word)})
    response['Cache-Control'] = 'private, no-store'
    return response
