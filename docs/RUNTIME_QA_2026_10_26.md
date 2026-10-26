# Runtime QA — 26/10/2026

Checked against the disposable `lexiread-qa` Docker Compose project. No production
database, real email provider, AI API, or local `.env` was used. The QA web port is
bound to `127.0.0.1:8766`; PostgreSQL has no exposed host port and uses temporary
container storage.

## Results

| Check | Result |
| --- | --- |
| Django suite, Python 3.12 / PostgreSQL 16 | **89/89 PASS** |
| Django suite, local Python 3.14 / SQLite memory | **88 PASS**, 1 PostgreSQL locking test SKIP |
| Pure Python unit suite | **89 PASS**, 1 optional reportlab fixture SKIP |
| Node frontend logic | PASS: catalog/track/pagination, scoring and private metadata, four locale dictionaries, compact cards and escaped content |
| Django system check, PostgreSQL QA | PASS |
| Migration drift | No changes detected |
| Migration against existing QA data | `0009_learningday` applied successfully |
| Real local HTTP smoke | PASS: health, auth, account/password pages, catalog, opening IELTS, vocabulary save, backup and logout |
| Production security check in a disposable container | No errors; one expected `security.W004` warning because HSTS is opt-in |
| Production `collectstatic` in a disposable container | PASS, including manifest hashing/compression of new brand and resource assets |

After the final catalog verification labels, accessibility adjustments and mobile
route-scroll fix, the QA image was rebuilt and the web container restarted. The
three resource integration tests, expanded HTTP smoke (including exact catalog
JSON and new image/CSS/JS assets) and production `collectstatic` all passed again.
The complete 89-test Django run above preceded these final presentation updates.

QA content remains **69 readings (54 general + 15 IELTS) and 20 TOEIC sets**.
Repeated seeding and QA preparation preserved existing content and created no
duplicates. The 60-item editorial pack is included only in this disposable QA
database; the default application seed is still 27 readings and 2 TOEIC sets.

## Regression coverage added

`learning/test_platform.py` previously expected a page visit to count as a study
day. That stale assertion now checks zero study days and two page views, matching
the existing real-study behavior.

Eight tests in `learning/test_motivation.py` check completion versus browsing and
favorites; repeat completion; account isolation; idempotent review and survival
after vocabulary deletion; legacy review timestamps across the Vietnam/UTC date
boundary; backup merge without duplicated study days; invalid/future backup dates
with atomic rejection; and streak grace, longest run and the rolling 30-day window.

Three tests in `learning/test_resources_ui.py` verify that anonymous and signed-in
entry pages include the same reviewed official URLs; malicious resource text cannot
break out of the JSON script element; and page requests do not contact publishers
or import exam content into the learning database.

## Repeat commands

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node scripts/test_frontend_logic.cjs
.\.venv\Scripts\python.exe manage.py test learning --settings=config.test_settings --noinput
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa build web
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py test learning --settings=config.qa_settings --noinput
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py check --settings=config.qa_settings
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web manage.py makemigrations --check --dry-run --settings=config.qa_settings
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa run --rm web scripts/prepare_qa.py --publish-pack
docker compose --env-file .env.example -f compose.qa.yml -p lexiread-qa up -d web
.\.venv\Scripts\python.exe scripts/smoke_qa_http.py
```

Rebuild and restart QA after subsequent source changes before using the local URL
to review those changes. QA `runserver`, DEBUG mode, console email and fake accounts
are deliberately local-only and are not production deployment settings.

## Verification limits

The old `scripts/test_platform_preview.py` command was attempted but could not
launch because its default `/usr/bin/chromium` path is Linux-specific. This is not
a successful browser/layout check. Browser verification of the new design is
reported separately by the interface work. Real password recovery delivery,
production migrations, real-domain HTTPS and the deployed site are not verified
by this local suite. HSTS remains an explicit deployment configuration choice as
described in the deployment guide.
