"""Local decorative artwork only; never fetch arbitrary image URLs from lesson data."""
import re
import unicodedata
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def topic_labels():
    return json.loads((Path(__file__).resolve().parents[2] / 'data/topic_labels.json').read_text(encoding='utf-8'))


def topic_label(topic):
    value = str(topic or 'Reading')
    return topic_labels().get(value, value.replace('_', ' '))


def topic_matches(topic, query):
    # Match the label learners see while retaining the editorial key in stored data.
    def normal(value):
        return re.sub(r'[^a-z0-9]+', ' ', value.casefold()).strip()
    return normal(query) in normal(topic_label(topic)) if normal(query) else False

ART_TOPICS = {
    'nature': ('nature','environment','conservation','seed','plant','garden','water','animal','climate','weather','sustainable','outdoor','moi truong','thien nhien'),
    'food': ('food','lunch','soup','kitchen','meal','market','bread','cook','cafe','thuc pham','bua an'),
    'travel': ('travel','transport','bus','train','map','journey','holiday','trip','du lich','ban do'),
    'technology': ('technology','digital','data','science','ai study','online','media','sampling','searchable','cong nghe','khoa hoc'),
    'school': ('school','education','study','learning','notebook','toy','sport','play','hoc tap','truong hoc'),
    'city': ('community','public','urban','city','museum','history','historical','heritage','neighbour','shared','art','cong dong','thanh pho'),
    'work': ('office','business','work','job','career','staff','recruit','purchase','purchasing','delivery','service','management','conference','reservation','hospitality','product','cong viec'),
    'reading': ('reading','book','library','literacy','thu vien','doc sach'),
}


def cover_key(topic='', title=''):
    def normalized(value):
        text=unicodedata.normalize('NFD',value.lower().replace('đ','d'))
        return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in text if not unicodedata.combining(c)))
    # Topic is authoritative; title is a fallback, not an unrelated keyword override.
    for value in (topic,title):
        text=' '+normalized(value)+' '
        scores={key:sum((' '+word+' ') in text for word in words) for key,words in ART_TOPICS.items()}
        if max(scores.values()): return max(scores,key=scores.get)
    return 'reading'


def cover_metadata(topic='',title=''):
    key=cover_key(topic,title)
    return {'cover_key':key,'cover_path':f'illustrations/{key}.svg','topic_label':topic_label(topic)}
