import re
from django.db.models import Q
from django.http import JsonResponse, Http404
from .models import VocabularyCollection, LexicalReference, Vocabulary
from .views import api
from .services.core import InputError, fingerprint
from .services.foundation_content import fold, get_unit
from .services.storage import serial_vocab
from .services.learning_path import progress_for
from .services.lexical_patterns import manifest, lessons


@api('GET')
def catalogue(request):
    rows = VocabularyCollection.objects.filter(content__track='lexical_patterns').values(
        'slug','title','level','content__pattern_kind','content__relation','content__words')
    progress = progress_for(request.user)
    items = []
    for row in rows:
        words = row['content__words'] or []
        # Only this small course catalogue, never reference data or question answers.
        items.append(dict(id=row['slug'], title=row['title'], level=row['level'],
            kind=row['content__pattern_kind'], relation=row['content__relation'], count=len(words),
            preview=[w['word'] for w in words[:3]], terms=' '.join(w['word'] for w in words),
            progress=progress.get('vocabulary/'+row['slug'])))
    # Show one introductory lesson per pattern before the second/third rounds.
    order = {u['id']:(int(u['id'].rsplit('-',1)[1]) if u['pattern_kind']=='collocations' else 1, i)
             for i,u in enumerate(lessons())}
    items.sort(key=lambda row:order.get(row['id'],(99,9999)))
    response = JsonResponse({'items':items, 'sources':manifest()['sources']})
    response['Cache-Control'] = 'private, no-store'
    return response


@api('GET')
def reference(request):
    kind = request.GET.get('kind','collocation')
    query = fold(request.GET.get('q','').strip())
    if kind not in ('collocation','family','corpus'):
        raise InputError('Chọn collocations, word families hoặc cụm trong câu.')
    if not re.fullmatch(r"[a-z][a-z '\-]{1,79}", query):
        raise InputError('Nhập từ tiếng Anh từ 2 đến 80 ký tự.')
    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        raise InputError('Số trang chưa hợp lệ.')
    if not 1 <= page <= 100:
        raise InputError('Số trang chưa hợp lệ.')
    rows = LexicalReference.objects.filter(kind=kind).filter(Q(headword=query)|Q(related=query)).order_by('-rank','headword','related','key')
    offset = (page-1)*12
    results = list(rows.values('headword','related','relation','source','detail')[offset:offset+13])
    return JsonResponse(dict(items=results[:12], page=page, has_next=len(results)>12, query=query))


@api('GET')
def cards(request, unit_id):
    unit = get_unit('vocabulary', unit_id)
    if not unit or unit.get('track') != 'lexical_patterns':
        raise Http404('Bài học không tồn tại.')
    keys = [fingerprint(w['word'], w['meaning_vi']) for w in unit['words']]
    owned = {v.fingerprint: v for v in Vocabulary.objects.filter(owner=request.user, fingerprint__in=keys)}
    response = JsonResponse({'id':unit_id, 'title':unit['title'], 'items':[serial_vocab(owned[k]) for k in keys if k in owned]})
    response['Cache-Control'] = 'private, no-store'
    return response
