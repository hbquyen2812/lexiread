"""HTTP contract smoke against the fixed local QA port; not a browser/layout test."""
import json
from pathlib import Path
import re

import httpx


def resource_data(response):
    assert response.status_code == 200
    match = re.search(r'<script id="official-resources-data" type="application/json">(.*?)</script>',
                      response.text, re.S)
    assert match, 'Official resource JSON missing from page'
    return json.loads(match.group(1))


def main():
    expected_resources = json.loads((Path(__file__).resolve().parents[1] /
        'data/public_sources/catalog.json').read_text(encoding='utf-8'))['resources']
    with httpx.Client(base_url='http://127.0.0.1:8766',timeout=20,trust_env=False) as client:
        assert client.get('/health/').json()=={'status':'ok'}
        assert resource_data(client.get('/')) == expected_resources
        assert client.get('/api/bootstrap/').status_code==401
        assert client.get('/login/').status_code==200
        response=client.post('/login/',data={'username':'qa-reader','password':'LexiRead-QA-2026!',
                                           'csrfmiddlewaretoken':client.cookies['csrftoken']})
        assert response.status_code==302
        assert resource_data(client.get('/')) == expected_resources
        assert client.get('/account/').status_code==200
        assert client.get('/account/password/').status_code==200
        assert client.get('/password-reset/').status_code==200
        general=client.get('/api/catalog/?track=general').json()
        ielts=client.get('/api/catalog/?track=ielts').json()
        toeic=client.get('/api/toeic/').json()
        assert (general['total'],ielts['total'],len(toeic['items']))==(54,15,20)
        csrf={'X-CSRFToken':client.cookies['csrftoken']}
        sample=next(row for row in ielts['items'] if row['slug'].startswith('pack-v1-'))
        lesson=client.post(f"/api/catalog/{sample['slug']}/open/",headers=csrf,json={}).json()
        assert lesson['lesson']['translation_status']=='not_provided'
        assert lesson['analysis']['translations']==[]
        assert 'editorial' not in lesson['lesson']
        assert all('answer' not in row for row in lesson['lesson']['questions'])
        word=lesson['analysis']['vocabulary'][0]
        assert word['usage_pattern'] and word['example'] and word['paraphrases']
        saved=client.post('/api/vocabulary/',headers=csrf,json={'items':[word],'reading_id':lesson['id']})
        assert saved.status_code in (200,201)
        words=client.get('/api/vocabulary/').json()['items']
        assert any(w['word']==word['word'] and w['usage_pattern']==word['usage_pattern'] for w in words)
        assert client.get('/api/backup/').status_code==200
        assert client.get('/static/app.js').status_code==200
        for asset in ('resources.js', 'resources.css', 'brand.css', 'favicon.svg'):
            assert client.get('/static/' + asset).status_code == 200, asset
        artwork = client.get('/static/illustrations/lexi-reading-garden.webp')
        assert artwork.status_code == 200 and artwork.content[:4] == b'RIFF'
        assert client.post('/logout/',headers=csrf).status_code==302
        assert client.get('/api/bootstrap/').status_code==401
    print('PASS QA HTTP: login/logout, profile/password pages, 54 general + 15 IELTS + 20 TOEIC, English-only label, private answers, word patterns, backup, official resource JSON and brand assets.')


if __name__=='__main__': main()
