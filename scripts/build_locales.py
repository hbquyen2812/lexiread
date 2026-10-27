"""Build static translations from repository-authored copy (never learner data).

Maintenance command only, with explicit --translate opt-in for network requests.
Cached translations and editorial corrections produce a standalone local catalog.
English examples, grammatical terms and template values must survive unchanged.
"""
import argparse
import ast
import concurrent.futures
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'data/private/localization-build'
VI = re.compile(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', re.I)
# Unaccented Vietnamese words are prose, not English vocabulary to protect.
VI_ASCII = set('ai an anh ba ban bao bay bia bui ca cam can cao cha chai chan cho chua chui co con cung da danh di do du em ga gai gan ghi gia gian giao hai hay hi ho hoa hoi hom hon in ke kem kho khi khoa kia kim la lai lam lan lang lo loai ly ma mai mang me minh mua nay nam nghe ngon ngay nha nhan nhanh nhau nhu noi non nuoc o ong qua quan quen quy ra rang sau sang sao sinh so son sung ta tai tam tan tay ten tham than thanh thay theo thi tho thu thua tien tin tinh toan tra trai trang tre trong truoc trua tui va vai van vi voi vui xa xe xem xanh xong yen'.split())
TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
VI_ASCII.update('suy chi sai chung dung quay quanh trung reo phong mong chia xin ngang coi tranh gom che xu treo xung linh ao ven chen duy hy lau cong tung tha phim khung ty'.split())
VI_ASCII.difference_update({'can','an','do','so','in','me','than','hi'})

def prepare(row):
    values = []
    def mark(value):
        values.append(value)
        return '__TERM'+str(len(values)-1)+'__'
    source = re.sub(r'\{\d+\}', lambda m: mark(m[0]), row['text'])
    source = re.sub(r'[“"]([^”"\n]+)[”"]', lambda m: m[0] if VI.search(m[1]) or '__TERM' in m[1] else mark(m[0]), source)
    if any('grammar' in f or 'strategy_guides' in f for f in row['files']):
        def term(match):
            word=match[0];after=source[match.end():];before=source[:match.start()]
            # These Vietnamese homographs are prose; elsewhere they are English grammar terms.
            exceptions={'an':r'\s+(toàn|ninh|tâm|ủi)\b','can':r'\s+(thiệp|ngăn)\b','so':r'\s+(sánh|với)\b','do':r'\s+(đó|dự|dụ|LexiRead)\b','in':r'\s+(đậm|nghiêng|hoa|màu|chữ|ra)\b'}
            if word.lower() in exceptions and re.match(exceptions[word.lower()],after,re.I):return word
            if word.lower()=='do' and re.search(r'\blý\s+$',before,re.I):return word
            return mark(word) if word.replace('’',"'").isascii() and word.lower() not in VI_ASCII and word!='TERM' else word
        source = TOKEN.sub(term, source)
    return source, values

def restore(text, values):
    text = re.sub(r'__\s*(?:TERM|TERME|学期|學期)\s*(\d+)\s*__',r'__TERM\1__',text,flags=re.I)
    for i, value in enumerate(values):
        marker = '__TERM'+str(i)+'__'
        if text.count(marker) != 1:
            raise ValueError('Translated text changed a protected English term or variable')
        text = text.replace(marker, value)
    if re.search(r'__TERM\d+__', text):
        raise ValueError('Unresolved marker')
    return text

def translate_batch(items, lang):
    source = '\n'.join('[[%d]] %s' % (i, item[1]) for i,item in enumerate(items))
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({'client':'gtx','sl':'vi','tl':lang,'dt':'t','q':source})
    with urllib.request.urlopen(url, timeout=40) as response:
        data = json.load(response)
    output = ''.join(s[0] for s in data[0] if s[0])
    parts = re.split(r'\[\[\s*(\d+)\s*\]\]\s*', output)
    translated = {int(parts[i]):parts[i+1].strip() for i in range(1,len(parts)-1,2)}
    if set(translated) != set(range(len(items))):
        raise ValueError('Translation changed batch boundaries')
    return {item[0]:restore(translated[i],item[2]) for i,item in enumerate(items)}

def canonical(source):
    keys=[]
    def key(match):
        if match[0] not in keys:keys.append(match[0])
        return '{'+str(keys.index(match[0]))+'}'
    return re.sub(r'\{\d+\}',key,source),keys

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--translate',action='store_true')
    parser.add_argument('--check',action='store_true',help='Validate the bundled catalog without writing it')
    args=parser.parse_args()
    sources=json.loads((BUILD/'sources.json').read_text(encoding='utf-8'))
    indexed={r['text']:r for r in sources}
    for name in ['learning/services/learning_path.py','learning/accounts/forms.py','learning/forms.py','learning/services/foundation_content.py']:
        for node in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8'))):
            value=None
            if isinstance(node,ast.Constant) and isinstance(node.value,str):value=node.value
            elif isinstance(node,ast.JoinedStr):
                parts=[];index=0
                for part in node.values:
                    if isinstance(part,ast.Constant):parts.append(part.value)
                    else:parts.append('{'+str(index)+'}');index+=1
                value=''.join(parts)
            if value and VI.search(value) and len(value)<2200:
                value=re.sub(r'\s+',' ',value).strip()
                indexed.setdefault(value,{'text':value,'files':[name]})
    sources=list(indexed.values())
    edits=json.loads((ROOT/'data/interface_translations.json').read_text(encoding='utf-8'))
    templates={canonical(source)[0]:(canonical(source)[1],translations) for source,translations in edits.items() if re.search(r'\{\d+\}',source)}
    for row in sources:
        source=row['text'];pattern,keys=canonical(source)
        if source not in edits and pattern in templates:
            old,translations=templates[pattern];mapping=dict(zip(old,keys))
            edits[source]=[re.sub(r'\{\d+\}',lambda m:mapping[m[0]],text) for text in translations]
    caches={}
    bundled=ROOT/'static/i18n_catalog.js'
    existing=json.loads(bundled.read_text(encoding='utf-8').split('window.LEXI_INTERFACE_LOCALES=',1)[1].strip().removesuffix(';')) if bundled.exists() else []
    def language(lang):
        path=BUILD/('translated-'+lang+'.json')
        cache=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        column={'en':1,'fr':2,'zh-CN':3}[lang]
        for row in existing:cache.setdefault(row[0],row[column])
        pending=[]
        for row in sources:
            if row['text'] not in cache and row['text'] not in edits:
                text,values=prepare(row);pending.append((row['text'],text,values))
        if pending and not args.translate:
            raise ValueError(f'{lang}: {len(pending)} strings require translation; opt in with --translate')
        groups=[];batch=[];size=0
        for row in pending:
            if batch and size+len(row[1])>1900:groups.append(batch);batch=[];size=0
            batch.append(row);size+=len(row[1])+15
        if batch:groups.append(batch)
        failures=[]
        for n,batch in enumerate(groups):
            try:cache.update(translate_batch(batch,lang))
            except ValueError:
                for row in batch:
                    try:cache.update(translate_batch([row],lang))
                    except ValueError:failures.append(row[0])
            # Fail closed on HTTP errors or throttling; no bypass/retry loop.
            path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            if n%15==0:print(lang,n+1,'/',len(groups),flush=True)
            time.sleep(.15)
        print(lang,'missing',len(failures),flush=True)
        return lang,cache
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(language,lang):lang for lang in ['en','fr','zh-CN']}
        for job in concurrent.futures.as_completed(jobs):
            try:
                lang,cache=job.result();caches[lang]=cache
            except Exception as error:
                print(jobs[job],type(error).__name__,str(error),flush=True)
                raise
    rows=[];missing=[]
    for source in sources:
        text=source['text']
        translated=edits.get(text) or [caches[lang].get(text) for lang in ['en','fr','zh-CN']]
        if not all(translated):missing.append(text);continue
        rows.append([text,*translated])
    (BUILD/'missing.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
    if missing:raise ValueError(f'{len(missing)} strings need editorial corrections; see missing.json')
    for text,translations in edits.items():
        if text not in {r[0] for r in rows}:rows.append([text,*translations])
    for row in rows:
        assert len(row)==4 and all(isinstance(v,str) and v for v in row)
        assert all(sorted(re.findall(r'\{\d+\}',v))==sorted(re.findall(r'\{\d+\}',row[0])) for v in row[1:]),row[0]
    output='/* Bundled translations; English learning content is excluded by i18n.js. */\nwindow.LEXI_INTERFACE_LOCALES='+json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';\n'
    if args.check:
        if bundled.read_text(encoding='utf-8')!=output:raise ValueError('Catalog is stale. Run build_locales.py and review its diff.')
    else:bundled.write_text(output,encoding='utf-8')
    print('Exported',len(rows),'local translations')

if __name__=='__main__':main()
