"""Small, portable personal vocabulary packs; never restore account or study state."""
from .core import InputError, clean_text, validate_entry, fingerprint

FORMAT='lexiread-vocabulary'
MAX_ITEMS=500
MAX_BYTES=2*1024*1024
FIELDS=('word','pos','meaning_vi','usage_pattern','example','example_vi','synonyms','paraphrases','context','note')


def validate_deck(payload):
    if not isinstance(payload,dict) or payload.get('format')!=FORMAT:
        raise InputError('File chưa đúng mẫu bộ từ LexiRead. Bạn có thể tải mẫu ở bước 1.')
    if type(payload.get('version')) is not int or payload['version']!=1:
        raise InputError('Phiên bản file này chưa được hỗ trợ. Hãy dùng mẫu phiên bản 1.')
    meta=payload.get('deck')
    if not isinstance(meta,dict):raise InputError('File cần có tên bộ từ trong mục deck.')
    name=clean_text(meta.get('name',''),100,True)
    rows=payload.get('vocabulary')
    if not isinstance(rows,list) or not 1<=len(rows)<=MAX_ITEMS:
        raise InputError('Mỗi bộ cần từ 1 đến 500 từ hoặc cụm từ.')
    items=[];seen=set();duplicates=0
    for index,row in enumerate(rows,1):
        if not isinstance(row,dict):raise InputError(f'Từ số {index} chưa đúng cấu trúc. Hãy đối chiếu file mẫu.')
        try:
            fields=validate_entry({key:row[key] for key in FIELDS if key in row})
        except InputError as exc:
            raise InputError(f'Từ số {index}: {exc}') from exc
        fields.update(tags=[name],source_label=name,origin='import',verified=False)
        key=fingerprint(fields['word'],fields['meaning_vi'])
        if key in seen:duplicates+=1;continue
        seen.add(key);items.append(fields)
    return name,items,duplicates


def pack(name,entries):
    return {'format':FORMAT,'version':1,'deck':{'name':name},
            'vocabulary':[{key:entry.get(key,[] if key in ('synonyms','paraphrases') else '') for key in FIELDS} for entry in entries]}
