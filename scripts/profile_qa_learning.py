"""Read-only endpoint timings in the isolated QA database, excluding network latency."""
import json
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if os.environ.get('DJANGO_SETTINGS_MODULE') != 'config.qa_settings':
    raise SystemExit('Run only with DJANGO_SETTINGS_MODULE=config.qa_settings.')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

user = get_user_model().objects.get(username='qa-reader')
client = Client(HTTP_HOST='127.0.0.1')
client.force_login(user)
paths = ['/api/learn/overview/?kind=vocabulary', '/api/learn/vocabulary/pack-v3-day-003/',
         '/api/learn/plan/', '/api/catalog/?track=general', '/api/catalog/?track=general&featured=1&limit=3']
results = []
for path in paths:
    timings = []
    for _ in range(4):
        start = time.perf_counter()
        with CaptureQueriesContext(connection) as queries:
            response = client.get(path)
        elapsed = (time.perf_counter()-start)*1000
        if response.status_code != 200:
            raise SystemExit(f'{path}: HTTP {response.status_code}')
        timings.append(elapsed)
    results.append({'path':path,'cold_ms':round(timings[0],1),'warm_median_ms':round(statistics.median(timings[1:]),1),
                    'query_count':len(queries),'response_bytes':len(response.content)})
print(json.dumps({'measurement':'Django test client, QA database, one reader; not a production capacity test', 'results':results}, indent=2))
