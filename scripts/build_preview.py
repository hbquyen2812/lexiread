from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from learning.services.analysis import ENTRY_SCHEMA,ANALYSIS_SCHEMA,SYSTEM
from learning.services.catalog import validate_lesson
from learning.services.qa import QA_SCHEMA
seed={'words':json.loads((root/'data/seed_vocab.json').read_text(encoding='utf-8')),'text':(root/'data/set_in_metal.txt').read_text(encoding='utf-8'),'analysis':json.loads((root/'data/demo_analysis.json').read_text(encoding='utf-8')),'entry_schema':ENTRY_SCHEMA,'analysis_schema':ANALYSIS_SCHEMA,'system':SYSTEM}
seed['lessons']=sorted([validate_lesson(json.loads(p.read_text(encoding='utf-8'))) for p in (root/'data/lessons').glob('*.json')],key=lambda x:x['order'])
seed['qa_schema']=QA_SCHEMA
html=(root/'templates/app.html').read_text(encoding='utf-8').replace('{% load static %}','').replace('{% csrf_token %}','')
html=html.replace('<link rel="stylesheet" href="{% static \'app.css\' %}">','<style>'+(root/'static/app.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script src="{% static \'app.js\' %}" defer></script>', '<script>const PREVIEW_SEED='+json.dumps(seed,ensure_ascii=False).replace('<','\\u003c')+';</script>\n<script>'+(root/'scripts/preview_adapter.js').read_text(encoding='utf-8')+'</script>\n<script>'+(root/'static/app.js').read_text(encoding='utf-8')+'</script>')
html=html.replace("<script src=\"{% static 'reading_platform.js' %}\" defer></script>", '<script>'+(root/'static/reading_platform.js').read_text(encoding='utf-8')+'</script>')
html=html.replace('<div class="workspace">','<div class="workspace"><div class="preview-banner">BẢN HTML DÙNG THỬ · Lưu trong trình duyệt này, không phải PostgreSQL · Không gọi API · Có thể xuất backup JSON sang bản Django.</div>')
html=html.replace('Kho riêng · PostgreSQL','Bản HTML · localStorage')
html=html.replace('<form method="post" action="/logout/" class="logout"><button class="link-btn" type="submit">Đăng xuất</button></form>','')
(root/'preview.html').write_text(html,encoding='utf-8')
print('Preview bytes:',len(html.encode()))
