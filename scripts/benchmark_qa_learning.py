"""Bounded reads against temporary loopback QA Gunicorn, with a disposable test session."""
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if os.environ.get('DJANGO_SETTINGS_MODULE') != 'config.qa_settings':
    raise SystemExit('Run only inside the isolated QA container.')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
from django.conf import settings
from django.contrib.sessions.models import Session

BASE = 'http://127.0.0.1:8770'
PATHS = ['/api/catalog/?track=general&limit=12', '/api/learn/vocabulary/pack-v3-day-003/',
         '/api/learn/overview/?kind=vocabulary', '/api/learn/plan/', '/api/dictionary/search/?q=book']

def reader(index, cookies):
    timings=[];errors=0
    with httpx.Client(base_url=BASE,cookies=cookies,timeout=20,trust_env=False) as client:
        for i in range(10):
            start=time.perf_counter()
            try:
                response=client.get(PATHS[(i+index)%len(PATHS)])
                errors += response.status_code != 200
            except httpx.HTTPError:
                errors += 1
            timings.append((time.perf_counter()-start)*1000)
    return timings, errors

def main():
    # Django's test login makes a session for this named QA-only account. No password
    # is read, stored in the script, printed or sent to an external service.
    bootstrap=Client()
    bootstrap.force_login(get_user_model().objects.get(username='qa-reader'))
    key=bootstrap.cookies[settings.SESSION_COOKIE_NAME].value
    cookies={settings.SESSION_COOKIE_NAME:key}
    try:
        with httpx.Client(base_url=BASE,cookies=cookies,timeout=20,trust_env=False) as client:
            for path in PATHS:
                client.get(path).raise_for_status()
        stages=[]
        for clients in [1,4,8,16]:
            start=time.perf_counter()
            with ThreadPoolExecutor(max_workers=clients) as pool:
                results=list(pool.map(lambda index:reader(index,cookies),range(clients)))
            elapsed=time.perf_counter()-start
            times=sorted(t for values,_ in results for t in values)
            stages.append({'concurrent_clients':clients,'requests':len(times),'errors':sum(e for _,e in results),
                'median_ms':round(statistics.median(times),1),'p95_ms':round(times[math.ceil(.95*len(times))-1],1),
                'requests_per_second':round(len(times)/elapsed,1)})
        print(json.dumps({'server':'QA Gunicorn, 1 worker x 4 threads, warmed public metadata',
            'limits':'Loopback reads only; shared QA account with little personal history. No think time. Not a production/user capacity guarantee.',
            'stages':stages},indent=2))
    finally:
        Session.objects.filter(session_key=key).delete()

if __name__ == '__main__':
    main()
