from pathlib import Path
import json,sys,base64
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from learning.services.analysis import ENTRY_SCHEMA,ANALYSIS_SCHEMA,SYSTEM
from learning.services.catalog import validate_lesson
from learning.services.qa import QA_SCHEMA
from learning.services.toeic import toeic_sets
from learning.services.presentation import cover_metadata, ART_TOPICS
from learning.services.public_resources import public_resources
seed={'words':json.loads((root/'data/seed_vocab.json').read_text(encoding='utf-8')),'text':(root/'data/set_in_metal.txt').read_text(encoding='utf-8'),'analysis':json.loads((root/'data/demo_analysis.json').read_text(encoding='utf-8')),'entry_schema':ENTRY_SCHEMA,'analysis_schema':ANALYSIS_SCHEMA,'system':SYSTEM}
seed['lessons']=sorted([validate_lesson(json.loads(p.read_text(encoding='utf-8'))) for p in (root/'data/lessons').glob('*.json')],key=lambda x:x['order'])
for lesson in seed['lessons']: lesson.update(cover_metadata(lesson['topic'],lesson['title']))
seed['toeic_sets']=toeic_sets()
seed['qa_schema']=QA_SCHEMA
html=(root/'templates/app.html').read_text(encoding='utf-8').replace('{% load static %}','').replace('{% csrf_token %}','')
html=html.replace("{% include 'language_switcher.html' %}",(root/'templates/language_switcher.html').read_text(encoding='utf-8'))
html=html.replace('{{ official_resources|json_script:"official-resources-data" }}','<script id="official-resources-data" type="application/json">'+json.dumps(public_resources(),ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')+'</script>')
html=html.replace('<script src="{% static \'resources.js\' %}" defer></script>','<script>'+(root/'static/resources.js').read_text(encoding='utf-8')+'</script>')
html=html.replace('<link rel="stylesheet" href="{% static \'resources.css\' %}">','<style>'+(root/'static/resources.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<link rel="icon" href="{% static \'favicon.svg\' %}" type="image/svg+xml">','<link rel="icon" href="data:image/svg+xml;base64,'+base64.b64encode((root/'static/favicon.svg').read_bytes()).decode()+'" type="image/svg+xml">')
html=html.replace('<link rel="stylesheet" href="{% static \'responsive.css\' %}">','<style>'+(root/'static/responsive.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<link rel="stylesheet" href="{% static \'motivation.css\' %}">','<style>'+(root/'static/motivation.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<link rel="stylesheet" href="{% static \'brand.css\' %}">','<style>'+(root/'static/brand.css').read_text(encoding='utf-8')+'</style>')
library=(root/'static/library.js').read_text(encoding='utf-8')
artwork={key:'data:image/svg+xml;base64,'+base64.b64encode((root/f'static/illustrations/{key}.svg').read_bytes()).decode() for key in ART_TOPICS}
library=library.replace("const artwork=Object.fromEntries(['reading','nature','school','work','travel','city','food','technology'].map(key=>[key,'/static/illustrations/'+key+'.svg']));",'const artwork='+json.dumps(artwork)+';')
html=html.replace('<script src="{% static \'library.js\' %}" defer></script>','<script>'+library+'</script>')
html=html.replace('<link rel="stylesheet" href="{% static \'experience.css\' %}">','<style>'+(root/'static/experience.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script src="{% static \'i18n.js\' %}" defer></script>','<script>'+(root/'static/i18n.js').read_text(encoding='utf-8')+'</script>')
html=html.replace('<link rel="stylesheet" href="{% static \'app.css\' %}">','<style>'+(root/'static/app.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script src="{% static \'app.js\' %}" defer></script>', '<script>const PREVIEW_SEED='+json.dumps(seed,ensure_ascii=False).replace('<','\\u003c')+';</script>\n<script>'+(root/'scripts/preview_adapter.js').read_text(encoding='utf-8')+'</script>\n<script>'+(root/'static/app.js').read_text(encoding='utf-8')+'</script>')
html=html.replace("<script src=\"{% static 'reading_platform.js' %}\" defer></script>", '<script>'+(root/'static/reading_platform.js').read_text(encoding='utf-8')+'</script>')
signature='data:image/webp;base64,'+base64.b64encode((root/'static/illustrations/lexi-reading-garden.webp').read_bytes()).decode()
html=html.replace('/static/illustrations/lexi-reading-garden.webp',signature)
html=html.replace('<div class="workspace">','<div class="workspace"><div class="preview-banner">BẢN HTML DÙNG THỬ · Lưu trong trình duyệt này, không phải PostgreSQL · Không gọi API · Có thể xuất backup JSON sang bản Django.</div>')
html=html.replace('Kho riêng · PostgreSQL','Bản HTML · localStorage')
html=html.replace('<a href="/account/" id="storage-label">Tài khoản của tôi</a>','<span id="storage-label">Bản HTML dùng thử</span>')
html=html.replace('<form method="post" action="/logout/" class="logout"><button class="link-btn" type="submit">Đăng xuất</button></form>','')
(root/'preview.html').write_text(html,encoding='utf-8')
print('Preview bytes:',len(html.encode()))
