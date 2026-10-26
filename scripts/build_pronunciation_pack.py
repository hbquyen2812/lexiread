"""Maintainer-only bulk preparation. The learner website never runs this network job."""
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
from pathlib import Path
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from learning.services.dictionary import fetch_remote, safe_url, USER_AGENT


def main():
    units = json.loads((ROOT/'data/vocabulary_collections.json').read_text(encoding='utf-8'))['collections']
    words = {w['word'].lower() for u in units for w in u['words']}
    for path in (ROOT/'data/lessons').glob('*.json'):
        lesson = json.loads(path.read_text(encoding='utf-8'))
        words.update(w['word'].lower() for w in lesson.get('analysis', {}).get('vocabulary', []))
    words.update(('routine', 'appointment', 'serendipity'))
    words = sorted(words)
    work = ROOT/'data/private/dictionary_build'
    work.mkdir(parents=True, exist_ok=True)

    def fetch(word):
        path = work/(hashlib.sha256(word.encode()).hexdigest()+'.json')
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
        result = {'word': word, 'entries': [], 'audio': {}}
        try:
            data = fetch_remote(word)
            if data['status'] == 'unavailable':
                return result
            result['entries'] = data['entries']
            for entry in result['entries']:
                for phonetic in entry['phonetics']:
                    url = safe_url(phonetic['audio'], {'upload.wikimedia.org'}, '/wikipedia/commons/')
                    phonetic['audio'] = ''
                    if not url:
                        continue
                    with httpx.Client(timeout=8, follow_redirects=False, trust_env=False) as client:
                        with client.stream('GET', url, headers={'User-Agent': USER_AGENT}) as response:
                            mime = response.headers.get('content-type','').split(';')[0]
                            if response.status_code != 200 or mime not in ('audio/ogg','application/ogg','audio/mpeg','audio/wav'):
                                continue
                            content = bytearray()
                            for chunk in response.iter_bytes():
                                content.extend(chunk)
                                if len(content)>500_000:
                                    raise ValueError('Audio too large')
                    digest = hashlib.sha256(content).hexdigest()
                    result['audio'][digest] = {'data':base64.b64encode(content).decode(), 'mime':mime,
                        'source':phonetic['source'], 'license':phonetic['license']}
                    phonetic['audio'] = '/api/dictionary/audio/'+digest+'/'
        except (httpx.HTTPError, ValueError):
            return result
        path.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
        return result

    output = {'version':1, 'source':'Free Dictionary API / Wiktionary / Wikimedia Commons', 'words':{}, 'audio':{}}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fetch,w):w for w in words}
        for i,future in enumerate(as_completed(futures),1):
            result = future.result()
            for entry in result['entries']:
                for p in entry.get('phonetics', []):
                    if p.get('audio') and not p['audio'].startswith('/api/dictionary/audio/'):
                        p['audio'] = ''
            if result['entries']:
                output['words'][result['word']] = result['entries']
                output['audio'].update(result['audio'])
            if i%20==0:
                print(f'Prepared {i}/{len(words)}; {len(output["audio"])} recordings',flush=True)
    destination = ROOT/'data/dictionaries/pronunciation-pack.json.gz'
    with gzip.GzipFile(filename=str(destination), mode='wb', mtime=0) as f:
        f.write(json.dumps(output,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    print(f'Saved {len(output["words"])} words and {len(output["audio"])} recordings ({destination.stat().st_size} bytes)',flush=True)


if __name__ == '__main__':
    main()
