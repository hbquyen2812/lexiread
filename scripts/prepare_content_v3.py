"""Prepare a compact runtime release from the supplied ZIP; never execute pack tools/SQL."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from learning.services.content_release import converted_release, release_slug


def prepare(path):
    with zipfile.ZipFile(path) as archive:
        def read(name):
            info = archive.getinfo('lexiread_data_v3/' + name)
            if info.file_size > 20_000_000:
                raise ValueError('Oversized content file')
            return archive.read(info)
        source_manifest = json.loads(read('manifest.json'))
        required = ['data/lessons.json', 'data/baseline_v1.json', 'data/sources.json',
                    'data/tests.json', 'data/external_resources.json']
        raw = {}
        for name in required:
            raw[name] = read(name)
            if hashlib.sha256(raw[name]).hexdigest() != source_manifest['files'][name]['sha256']:
                raise ValueError('Archive checksum mismatch: ' + name)
    pack = json.loads(raw['data/lessons.json'])
    manifest = {'dataset_id': pack['metadata']['dataset_id'], 'version': pack['metadata']['version'],
                'source_archive_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                'source_lessons_sha256': source_manifest['files']['data/lessons.json']['sha256'],
                'counts': source_manifest['counts'], 'distinct_terms': source_manifest['distinct_terms'],
                'legacy_ids': json.loads(raw['data/baseline_v1.json'])['lesson_ids'],
                'sources': {s['id']: s['url'] for s in json.loads(raw['data/sources.json'])},
                'content_origin': 'original_ai_authored', 'independent_teacher_reviewed': False}
    rows = list(converted_release(pack, manifest))
    lessons = {s['id']: s for s in pack['lessons']}
    tests = json.loads(raw['data/tests.json'])
    for test in tests:
        total = 0
        for section in test['sections']:
            lesson = lessons[section['lesson_id']]
            if [q['question_id'] for q in section['questions']] != [q['id'] for q in lesson['questions']]:
                raise ValueError('Test question ordering mismatch: ' + test['id'])
            total += len(section['questions'])
        if total != test['question_count']:
            raise ValueError('Test question count mismatch')
    target = ROOT / 'data/content_packs/v3'
    target.mkdir(parents=True, exist_ok=True)
    bundle = gzip.compress(json.dumps(pack, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)
    manifest['bundle_sha256'] = hashlib.sha256(bundle).hexdigest()
    (target / 'lessons.json.gz').write_bytes(bundle)
    (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for name in ['tests', 'external_resources', 'sources']:
        (target / (name+'.json')).write_bytes(raw['data/'+name+'.json'])
    # Answer-free index, safe to serve directly. Full practice runs remain separate sections.
    public = []
    legacy = set(manifest['legacy_ids'])
    for test in tests:
        public.append({k: test[k] for k in ('id','test_kind','exam_type','title','time_limit_minutes','question_count')})
        public[-1]['sections'] = [{'title': lessons[s['lesson_id']]['title_en'],
            'label': s['label'], 'question_count': len(s['questions']),
            'href': ('#toeic-set/' if lessons[s['lesson_id']]['track']=='toeic' else '#lesson/')+
                    release_slug(s['lesson_id'], legacy)} for s in test['sections']]
    (ROOT/'static/practice_index.json').write_text(json.dumps(public,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    resources=[{k:r.get(k) for k in ('id','title','url','publisher','track','cefr_label')}
               for r in json.loads(raw['data/external_resources.json'])]
    (ROOT/'static/practice_resources.json').write_text(json.dumps(resources,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'validated_lessons':len(rows),'reading_questions':sum(len(r['questions']) for _,r,_ in rows),
        'vocabulary_contexts':sum(len(v['words']) for _,_,v in rows),'test_groups':len(tests),
        'bundle_bytes':len(bundle)}))


if __name__ == '__main__':
    prepare(Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'lexiread_reading_vocab_v3_20261026.zip'))
