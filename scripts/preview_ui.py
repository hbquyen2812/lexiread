"""Local visual QA server: real templates + authored content; no production database.

The login preview is intentionally read-only. /preview.html uses the existing
offline adapter to exercise learner flows with browser-local test data.
"""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from django.conf import settings
ROOT=Path(__file__).resolve().parents[1]
settings.configure(DEBUG=True,SECRET_KEY='preview-only-not-a-production-secret-key-123456789',STATIC_URL='/static/',
    ROOT_URLCONF=__name__,INSTALLED_APPS=['django.contrib.staticfiles'],TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[ROOT/'templates'],'APP_DIRS':True}])
import django
django.setup()
from django.template.loader import render_to_string
from django.urls import path
from learning.services.presentation import cover_metadata
from learning.services.public_resources import public_resources
from learning.services.strategy_guides import strategy_guides
from learning.services.toeic import toeic_sets
urlpatterns=[path('login/',lambda request:None,name='login'),path('signup/',lambda request:None,name='signup'),path('password-reset/',lambda request:None,name='password_reset')]

def context():
    lessons=[]
    for path in (ROOT/'data/lessons').glob('*.json'):
        lesson=json.loads(path.read_text(encoding='utf-8'))
        lesson.update(track=lesson.get('track','general'),word_count=len(lesson['text'].split()),question_count=len(lesson['questions']),vocabulary_count=len(lesson['analysis']['vocabulary']))
        lesson.update(cover_metadata(lesson['topic'],lesson['title']))
        lessons.append(lesson)
    lessons.sort(key=lambda x:(x['order'],x['title']))
    return dict(lessons=lessons,practices=toeic_sets(),general_count=sum(x['track']=='general' for x in lessons),ielts_count=sum(x['track']=='ielts' for x in lessons),next='/#catalog',form={},official_resources=public_resources(),strategy_guides=strategy_guides())

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if path in {'/','/login/','/guides/'}:
            html=render_to_string({'/':'landing.html','/login/':'registration/login.html','/guides/':'guides.html'}[path],context()).encode()
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(html)
        elif path=='/preview.html':super().do_GET()
        elif path.startswith('/static/') and (ROOT/path.lstrip('/')).resolve().is_relative_to((ROOT/'static').resolve()):super().do_GET()
        else:self.send_error(404)

if __name__=='__main__':
    print('Visual preview: http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
