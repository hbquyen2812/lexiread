# LexiRead Reading Studio v2

A reading-first English/Vietnamese learning app: original lesson and TOEIC-style practice libraries plus private imported readings, with saved-reading search/status/favorites, multi-reading vocabulary occurrences, grounded Q&A and spaced personal review.

Start with [README_VI.md](README_VI.md), the [v2 usage/upgrade guide](docs/READING_STUDIO_V2.md), and the [VPS/HTTPS deployment guide](docs/DEPLOYMENT.md).

12 original lessons plus two TOEIC Reading paths (Parts 5–6 and Part 7) containing 24 original questions and 16 focus-vocabulary entries. A2/B1/B2 and target-score labels are author estimates, not calibrated levels or official score predictions. Existing 116 personal seed cards remain optional.

Django/PostgreSQL source + standalone `preview.html`. No secret keys included. The server edition has a public feature/lesson catalog, while learning actions require email login and stay isolated per account. Offline HTML cannot call AI; manual prompt/JSON import is supported. Review includes a daily goal, streak, learning buckets and a weak-word group. The server edition includes first-party traffic analytics for administrators without storing IP addresses or loading third-party trackers.

The pure Python suite ran 81 tests: 80 passed and one optional reportlab test was skipped. 56 Chromium DOM checks passed. Docker Compose and both health checks passed; migrations through `0006_daily_visit`, Django `check`, and all 43 Django/PostgreSQL integration tests passed. The public landing page, email form and responsive layout also passed a Chromium smoke test. The production Compose/Caddy configuration passes Django deployment checks with a sample domain; a real public deployment, production restore drill and live AI calls were not tested. See [test report](docs/TEST_REPORT.md).
