"""Reviewed outbound video recommendations, with editorial level estimates."""
from copy import deepcopy
from datetime import date
from functools import lru_cache
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PATH=Path(__file__).resolve().parents[2]/'data/learning_channels.json'
LEVELS={'A1','A2','B1','B2','C1','C2'}
SKILLS={'listening','speaking','pronunciation','vocabulary','work','ielts','ideas'}
HOSTS={'www.youtube.com','learningenglish.voanews.com','www.easyenglish.video','rachelsenglish.com',
       'www.oxfordonlineenglish.com','www.ieltsadvantage.com','ed.ted.com','www.ted.com'}

def safe_url(value,youtube=False):
    if not isinstance(value,str) or len(value)>2000 or any(ord(c)<33 for c in value):return False
    try:
        u=urlsplit(value)
        return u.scheme=='https' and u.hostname in ({'www.youtube.com'} if youtube else HOSTS) and u.port in (None,443) and not u.username and not u.password
    except ValueError:return False

def validate_channels(raw):
    if not isinstance(raw,dict) or type(raw.get('schema_version')) is not int or raw['schema_version']!=1:raise ValueError('Invalid channel catalog version')
    rows=raw.get('channels');seen=set()
    if not isinstance(rows,list) or not 1<=len(rows)<=50:raise ValueError('Expected reviewed channel list')
    for row in rows:
        if not isinstance(row,dict):raise ValueError('Invalid channel')
        key=row.get('id','')
        if not isinstance(key,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',key) or key in seen:raise ValueError('Invalid channel id')
        seen.add(key)
        for field in ('name','mark','accent_vi','description_vi','start_vi','task_vi','support_vi'):
            if not isinstance(row.get(field),str) or not row[field].strip() or len(row[field])>600:raise ValueError('Invalid channel text')
        for field,allowed in [('levels',LEVELS),('skills',SKILLS)]:
            values=row.get(field)
            if not isinstance(values,list) or not values or any(not isinstance(x,str) or x not in allowed for x in values) or len(set(values))!=len(values):raise ValueError('Invalid channel categories')
        if row.get('tone') not in {'sky','peach','sage','lavender'}:raise ValueError('Invalid visual tone')
        for field in ('channel_url','start_url','source_url'):
            if not safe_url(row.get(field),field=='channel_url'):raise ValueError('Unsafe channel link')
        try:date.fromisoformat(row.get('checked_at',''))
        except (ValueError,TypeError):raise ValueError('Invalid review date') from None
    return deepcopy(rows)

@lru_cache(maxsize=1)
def _channels():return validate_channels(json.loads(PATH.read_text(encoding='utf-8')))

def learning_channels():return deepcopy(_channels())
