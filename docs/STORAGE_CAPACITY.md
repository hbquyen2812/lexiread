# Storage and capacity — 2026-10-27

PostgreSQL is appropriate for this reading and vocabulary application. There is no
measured reason to replace it. This report describes the repository and local QA,
not an inspection of the production provider, subscription or backups.

## What is stored where

| Data | Current storage |
| --- | --- |
| Accounts, private vocabulary, review schedule, submissions and progress | PostgreSQL, scoped to the account |
| Shared reading units, TOEIC, vocabulary collections and dictionary | PostgreSQL; versioned source packs can seed missing content |
| Grammar and guide source content | Versioned local JSON content shipped with the application |
| Illustrations, fonts, CSS and scripts | Static files shipped with the image; WhiteNoise in production |
| UI language and local guide read markers | Browser storage; not all preferences sync across devices |
| Offline preview | Separate browser-local experience, not the server database |

QA PostgreSQL uses the named volume `lexiread-qa_qa_pgdata`. Restarting or rebuilding
the web container preserves it. At measurement time the QA database was **139 MB**
with **100 maximum database connections**. Neither number establishes a user limit.
Do not run `docker compose down -v` on a database whose contents must be retained.

The account JSON export preserves personal learning data, but it does not back up
all accounts, the full dictionary or system tables. Use PostgreSQL/provider backups
for the entire service, keep a copy outside the application server and periodically
restore into a separate database. The existing operational procedure is in
[DEPLOYMENT.md](DEPLOYMENT.md). Production backup and recovery were not exercised
in this change.

For future uploaded images or audio, use persistent object storage and keep the
object key in PostgreSQL. The 16 new SVG objects are shipped as static assets;
they require no image API or runtime AI calls. Concrete words get an appropriate
object when available; abstract or unmatched words get a neutral study-card motif.

## Changes made

- Fetch one vocabulary collection by its key rather than loading all 516 collections.
- Project only catalogue metadata and JSON array lengths, without reading every
  word and answer. Cache this public metadata for 60 seconds per process. Private
  progress is read separately and is never part of that cache. Transactions bypass
  the cache; editorial list changes may take up to 60 seconds to appear.
- Reuse lightweight summaries when generating the rule-based study plan.
- Load three home-page starters (A1, A2, B1) instead of 300 general reading rows.
  The general reading response is about 94% smaller (190,609 to 10,691 bytes).
- Lock the existing vocabulary sense while merging concurrent saves, preserving
  both imports' tags and the review schedule.
- Accept `pre-A1` collection filters and backup history without expanding the
  learner profile levels. Fix a lock-order timing edge case that rejected requests
  even when the relevant authentication limiter had no cooldown.

## Measurements

QA used the current PostgreSQL content and a small QA account. Endpoint timings
below are warm medians from three requests after an initial request through the
Django test client. They exclude network latency and are indicative, not an SLA.

| Endpoint | Before | After |
| --- | ---: | ---: |
| Vocabulary overview | 83.8 ms | 6.0 ms |
| One vocabulary collection | 53.2 ms | 4.6 ms |
| Study plan | 85.2 ms | 36.1 ms |

The new overview's cold request took **127.1 ms**. The main overview gain comes
from caching; the cold SQL projection alone is not claimed to be faster. Its
174,201-byte metadata response still contains all collections. The old full
300-reading endpoint was not improved (152.6 to 178.9 ms in these samples); the
home page now avoids it. The new three-level starter response took 8.2 ms.

A separate bounded loopback test used Gunicorn with **1 worker and 4 threads**,
matching `render.yaml`. Five authenticated read endpoints were warmed and mixed:
catalogue, collection detail, collection overview, study plan and dictionary search.
Each client made 10 requests without think time, sharing one QA account/session.

| Concurrent clients | Requests | Errors | Median | p95 | Requests/sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 10 | 0 | 18.9 ms | 55.9 ms | 38.3 |
| 4 | 40 | 0 | 41.3 ms | 105.2 ms | 75.6 |
| 8 | 80 | 0 | 93.7 ms | 170.9 ms | 77.4 |
| 16 | 160 | 0 | 213.7 ms | 285.3 ms | 73.6 |

This is **290 read requests with no observed failures**, not proof that production
supports a particular maximum number of people. It excludes browser assets,
internet latency, cold starts, AI, bulk imports, mixed writes, long histories and
sustained load. The temporary loopback server was stopped after measurement.
Use `scripts/profile_qa_learning.py` and `scripts/benchmark_qa_learning.py` only
with `config.qa_settings`. The benchmark uses a disposable session and no password;
it requires a temporary QA Gunicorn on loopback port 8770.

## Capacity and deployment decisions

Registered accounts, active learners and simultaneous requests are different
quantities. Four worker threads do not mean four users, and 100 database connections
do not mean 100 users. A person reading for several minutes makes few requests;
an import or submission can place more load than many idle readers.

The repository configures a **Free Render web service**, one worker/four threads,
and PostgreSQL connections reused for up to 60 seconds. `DATABASE_URL` is supplied
outside the repository, so its provider and tier have not been verified. Render's
current documentation says Free web services sleep after 15 idle minutes; **if**
the database is also Free Render Postgres, it expires 30 days after creation.
These are conditional deployment constraints, not a claim about the user's actual
database. See [Render Free documentation](https://render.com/docs/free), checked
2026-10-27. Do not store user uploads on that web service's ephemeral filesystem.

Before claiming a production user limit:

1. Confirm the actual web/DB plan, persistence, available memory and connection cap.
2. Test restoring a full backup to a separate database.
3. Measure a staging deployment with representative account histories and a mix
   of reading, dictionary search, submissions, reviews and imports over a sustained
   period. Track p95, errors, CPU, RAM and database connections, including cold cache.
4. Optimize the observed bottleneck, then repeat that workload. Prioritize an
   always-on web service and durable managed PostgreSQL for continuous availability.
   Budget database connections across workers/threads and admin jobs; use provider
   pooling when needed, rather than increasing workers without measurement.

No paid plan, production setting or database was changed. Django's connection
management is documented at [Django databases](https://docs.djangoproject.com/en/5.2/ref/databases/).

## Verification and UI evidence

- 156 Django/PostgreSQL tests passed, including concurrent saves, limiter budget,
  summary/detail parity, `pre-A1` filters and backup round-trip.
- 17 Node suites passed, including real DOMPurify and hostile import/render input.
- HTTP QA smoke passed; migration check reported no missing migrations.
- Host unit suite: 113 tests, 112 passed and one optional ReportLab test skipped.
- Browser checks: compact settings and restore disclosure, translated controls,
  illustrated guidance/collections/guides, no horizontal overflow in checked desktop
  and 320/390-pixel settings layouts, 390-pixel collection cards, the standalone
  public guide page, and no observed console errors in those flows.
- Screenshots: `qa/settings-desktop-20261027.png`, `qa/settings-mobile-20261027.png`,
  `qa/plan-desktop-20261027.png`, `qa/vocabulary-covers-20261027.png`,
  `qa/guides-desktop-20261027.png`, `qa/collection-mobile-20261027.png`.

The learner-facing activity calculation disclosure was removed. Accurate counts,
the 30-day period and the QA/demo label remain. Settings now emphasize account and
backup actions; restore and privacy details are collapsed. Teaching text, English
examples, private words and progress remain intact.
