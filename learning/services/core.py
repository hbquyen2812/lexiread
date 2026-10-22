"""Pure functions: deterministic validation / scheduling; no database or network."""
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime,timedelta,timezone
MAX_READING_CHARS = 60000
MAX_AI_CHARS = 16000
ENTRY_TEXT_FIELDS = {'word':160,'pos':40,'meaning_vi':2000,'example':2000,'example_vi':2000,
                     'context':4000,'note':4000,'source_label':200}
class InputError(ValueError): pass

def normalise(value):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(value))).strip().casefold()

def clean_text(value,limit,required=False):
    if not isinstance(value,str): raise InputError('Trường văn bản phải là chuỗi ký tự.')
    value=unicodedata.normalize('NFC',value).replace('\x00','').strip()
    if len(value)>limit: raise InputError(f'Nội dung vượt giới hạn {limit:,} ký tự.')
    if required and not value: raise InputError('Vui lòng điền đủ trường bắt buộc.')
    return value

def paragraphs(text):
    text=clean_text(text,MAX_READING_CHARS,True).replace('\r\n','\n').replace('\r','\n')
    return [s.strip() for s in re.split(r'\n\s*\n',text) if s.strip()]

def fingerprint(word,meaning):
    return hashlib.sha256((normalise(word)+'\x1f'+normalise(meaning)).encode()).hexdigest()

def occurrence_fingerprint(reading_id,source_label,context):
    raw=str(reading_id or '')+'\x1f'+normalise(source_label)+'\x1f'+normalise(context)
    return hashlib.sha256(raw.encode()).hexdigest()

def validate_entry(data):
    if not isinstance(data,dict): raise InputError('Mỗi từ vựng phải là một đối tượng JSON.')
    out={k:clean_text(data.get(k,''),limit,k in {'word','meaning_vi'}) for k,limit in ENTRY_TEXT_FIELDS.items()}
    for k in ('synonyms','paraphrases','tags'):
        values=data.get(k,[])
        if isinstance(values,str): values=[v.strip() for v in values.split('|') if v.strip()]
        if not isinstance(values,list) or len(values)>20: raise InputError(f'{k}: cần danh sách không quá 20 mục.')
        out[k]=list(dict.fromkeys(clean_text(v,300) for v in values if v))
    if len(out['word'].split())>16: raise InputError('Chọn tối đa 16 từ cho một từ/cụm từ.')
    out['verified']=data.get('verified',False) is True
    out['origin']=data.get('origin','manual') if data.get('origin') in {'ai','manual','seed','import','curated'} else 'manual'
    return out

def parse_json(text):
    text=clean_text(text,8*1024*1024,True)
    if text.startswith('```'):
        text=re.sub(r'^```(?:json)?\s*','',text,flags=re.I)
        text=re.sub(r'\s*```$','',text)
    try: return json.loads(text)
    except (ValueError,RecursionError) as exc: raise InputError('JSON không hợp lệ. Chỉ dán khối JSON, không kèm lời giải thích.') from exc

def word_in_text(word,text):
    return bool(re.search(r'(?<!\w)'+re.escape(word)+r'(?!\w)',text,re.I))

def mask_word(word,text):
    return re.sub(r'(?<!\w)'+re.escape(word)+r'(?!\w)','______',text,count=0,flags=re.I)

def schedule(state,rating,now=None):
    """A transparent simple interval scheduler, NOT FSRS or a validated memory model."""
    if rating not in {'again','hard','good','easy'}: raise InputError('Mức đánh giá không hợp lệ.')
    now=now or datetime.now(timezone.utc)
    old=max(0,float(state.get('interval_days',0)))
    ease=max(1.3,min(3,float(state.get('ease',2.5))))
    reps=max(0,int(state.get('repetitions',0)))
    lapses=max(0,int(state.get('lapses',0)))
    if rating=='again':
        interval=10/1440; ease=max(1.3,ease-0.2); reps=0; lapses+=1
    elif rating=='hard':
        interval=max(1,min(365,old*1.2)); ease=max(1.3,ease-0.15); reps+=1
    elif rating=='good':
        interval=1 if reps==0 else 3 if reps==1 else max(1,min(365,old*ease)); reps+=1
    else:
        interval=4 if reps==0 else max(4,min(365,old*ease*1.3)); ease=min(3,ease+0.1); reps+=1
    return {'interval_days':interval,'ease':ease,'repetitions':reps,'lapses':lapses,
            'due_at':now+timedelta(days=interval),'last_reviewed':now}

def calculate_review_streak(days,today):
    days=set(days)
    cursor=today if today in days else today-timedelta(days=1)
    if cursor not in days:return 0
    streak=0
    while cursor in days:
        streak+=1;cursor-=timedelta(days=1)
    return streak

def validate_progress(data):
    result={}
    for key,maxval in [('interval_days',365),('ease',3),('repetitions',100000),('lapses',100000)]:
        value=data.get(key,2.5 if key=='ease' else 0)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or not 0<=value<=maxval:
            raise InputError('Tiến độ trong backup không hợp lệ.')
        if key in ('repetitions','lapses') and not isinstance(value,int): raise InputError('Số lần ôn phải là số nguyên.')
        result[key]=value
    result['ease']=max(1.3,result['ease'])
    for key in ('due_at','last_reviewed'):
        if data.get(key):
            try:
                dt=datetime.fromisoformat(data[key].replace('Z','+00:00'))
                if dt.tzinfo is None: raise ValueError()
                result[key]=dt
            except (ValueError,TypeError,AttributeError): raise InputError('Ngày giờ trong backup phải là ISO 8601 có múi giờ.')
    return result
