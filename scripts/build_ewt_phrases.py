"""Extract repeated, evidenced word pairs; these are corpus examples, not vetted collocations.

Derived EWT data and retained sentences: CC BY-SA 4.0, see data/lexical/ewt/LICENSE.txt.
Run offline normally, or --download to retrieve exactly the pinned source files again.
"""
import argparse
import gzip
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data/lexical/ewt'
LEXEME = re.compile(r"[a-z][a-z'-]{1,35}\Z")
CONTACT = re.compile(r'https?://|www\.|@|\d{4,}|\S+\.(?:com|org|net)\b', re.I)
UNSUITABLE = re.compile(r'\b(?:fuck\w*|shit\w*|bitch\w*|porn\w*|rape\w*|nigg\w*|sex\w*|kill\w*|terror\w*|bomb\w*|suicid\w*|murder\w*)\b', re.I)
FUNCTION_ADVERBS = {'not','so','very','too','just','also','then','there','here','now','still','even','only','again','really','more','most','less','least','as','however','when','where','why','how','ever','never','always','often','sometimes','usually','almost','quite','rather','much','else','once','perhaps','maybe','probably','yet','already','soon','away','back','out','up','down','off','in','on','over'}


def source_files(download=False):
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf8'))
    for item in manifest['files']:
        compressed = item['name'].endswith('.conllu')
        path = ROOT / (item['name'] + ('.gz' if compressed else ''))
        if download:
            request = urllib.request.Request(item['url'], headers={'User-Agent':'Lexivela-data-import/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read(20_000_001)
            if len(raw) > 20_000_000 or hashlib.sha256(raw).hexdigest() != item['sha256']:
                raise ValueError('Source changed: '+item['name'])
            path.write_bytes(gzip.compress(raw, mtime=0) if compressed else raw)
        raw = gzip.decompress(path.read_bytes()) if compressed else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Source checksum mismatch: '+item['name'])
        if compressed:
            yield item['name'], raw.decode('utf8')


def sentences(text):
    for block in text.strip().split('\n\n'):
        tokens, sentence, sid = {}, '', ''
        for line in block.splitlines():
            if line.startswith('# text = '): sentence = line[9:]
            elif line.startswith('# sent_id = '): sid = line[12:]
            elif not line.startswith('#'):
                row = line.split('\t')
                if len(row) == 10 and row[0].isdigit(): tokens[int(row[0])] = row
        if sentence and sid and 5 <= len(tokens) <= 32 and 25 <= len(sentence) <= 240 and not CONTACT.search(sentence) and not UNSUITABLE.search(sentence):
            yield sid, sentence, tokens


def build(download=False):
    pairs = {}
    for filename, text in source_files(download):
        for sid, sentence, tokens in sentences(text):
            for index, token in tokens.items():
                head = tokens.get(int(token[6]))
                if not head: continue
                dep, parent, relation = token[3], head[3], token[7]
                if relation == 'obj' and (parent, dep) == ('VERB','NOUN'): kind = 'verb-noun'
                elif relation == 'amod' and (parent, dep) == ('NOUN','ADJ'): kind = 'adjective-noun'
                elif relation == 'compound' and (parent, dep) == ('NOUN','NOUN'): kind = 'noun-noun'
                elif relation == 'advmod' and dep == 'ADV' and parent in ('ADJ','VERB') and token[2].lower() not in FUNCTION_ADVERBS:
                    kind = 'adverb-adjective' if parent == 'ADJ' else 'verb-adverb'
                else: continue
                lemma, other = head[2].lower(), token[2].lower()
                if not LEXEME.fullmatch(lemma) or not LEXEME.fullmatch(other) or lemma == other: continue
                start, end = sorted((index,int(head[0])))
                if end-start > 5: continue
                # Require ordinary forward order and no intervening clause punctuation.
                if kind in ('adjective-noun','noun-noun','adverb-adjective') and index > int(head[0]): continue
                if kind == 'verb-noun' and index < int(head[0]): continue
                if any(tokens[i][3]=='PUNCT' for i in range(start,end+1) if i in tokens): continue
                key = (kind,lemma,other)
                record = pairs.setdefault(key, {'sentences':{}, 'evidence':[]})
                if sid in record['sentences']: continue
                record['sentences'][sid] = True
                # Keep exact sentence and surface span, never invent a sentence from lemmas.
                if len(record['evidence']) < 2:
                    record['evidence'].append({'sentence_id':sid,'file':filename,'text':sentence,
                        'phrase':' '.join(tokens[i][1] for i in range(start,end+1) if i in tokens)})
    rows = []
    for (relation,headword,related), data in sorted(pairs.items()):
        count = len(data['sentences'])
        if count < 2: continue
        detail = {'pattern':data['evidence'][0]['phrase'],'count':count,'evidence':data['evidence'],
                  'examples':[x['text'] for x in data['evidence']], 'license':'CC BY-SA 4.0'}
        identity = ['ewt-2.18',relation,headword,related]
        rows.append({'key':hashlib.sha256(json.dumps(identity).encode()).hexdigest(),
            'kind':'corpus','source':'ewt-2.18','headword':headword,'related':related,
            'relation':relation,'rank':count,'detail':detail})
    packed = gzip.compress(('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in rows)+'\n').encode(),mtime=0)
    (ROOT/'phrases.jsonl.gz').write_bytes(packed)
    info = {'rows':len(rows),'examples':sum(len(r['detail']['examples']) for r in rows),
            'relations':dict(Counter(r['relation'] for r in rows)),
            'sha256':hashlib.sha256(packed).hexdigest(),'license':'CC BY-SA 4.0'}
    (ROOT/'phrases-manifest.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf8')
    print(info)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true')
    build(parser.parse_args().download)
