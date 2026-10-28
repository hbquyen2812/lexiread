from django.http import JsonResponse, HttpResponse, Http404
import uuid

from .models import Reading, Vocabulary, DictionaryAudio, DictionaryRelease
from .services.dictionary import lookup_word, dictionary_links
from .services.offline_dictionary import lookup_local, search_local, pronunciation_batch
from .services.foundation_content import units, word_entry
from .views import api, body


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
                add(word_entry(entry, unit), 'Kho học Lexivela')
    response = JsonResponse({'word': word, 'local_entries': local, 'dictionary': lookup_local(word),
                             'links': dictionary_links(word)})
    response['Cache-Control'] = 'private, no-store'
    return response


@api('GET')
def search(request):
    q = request.GET.get('q','').strip()[:160]
    page = max(1,min(10000,int(request.GET.get('page','1'))))
    result = search_local(q,page) if q else {'items':[],'total':0,'page':1,'has_next':False}
    release = DictionaryRelease.objects.filter(pk='oewn-2025').first()
    result['available'] = release.entry_count if release else 0
    result['ipa_count'] = release.ipa_count if release else 0
    return JsonResponse(result)


@api('GET')
def audio(request, digest):
    if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise Http404
    sound = DictionaryAudio.objects.filter(pk=digest).first()
    if not sound:
        raise Http404
    response = HttpResponse(bytes(sound.data), content_type=sound.mime)
    response['Content-Length'] = len(sound.data)
    response['Cache-Control'] = 'private, max-age=86400, immutable'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@api('POST')
def pronunciations(request):
    if len(request.body) > 24000:
        return JsonResponse({'error': 'Danh sách từ quá dài.'}, status=400)
    words = body(request).get('words')
    if (not isinstance(words, list) or len(words) > 100 or
            any(not isinstance(word, str) or not word.strip() or len(word) > 160 for word in words)):
        return JsonResponse({'error': 'Danh sách từ không hợp lệ.'}, status=400)
    response = JsonResponse({'items': pronunciation_batch(words), 'source': 'Open English WordNet 2025'})
    response['Cache-Control'] = 'private, no-store'
    return response
