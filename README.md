# LexiRead Reading Studio v2

A reading-first English/Vietnamese learning app: a fixed, original lesson library plus private imported readings, with saved-reading search/status/favorites, contextual vocabulary filters, grounded Q&A and spaced personal review.

Start with [README_VI.md](README_VI.md) and [v2 usage/upgrade guide](docs/READING_STUDIO_V2.md).

12 original lessons; A2/B1/B2 labels are author estimates, not calibrated CEFR levels. 72 contextual vocabulary suggestions, 48 comprehension questions, 24 grammar notes and 24 preset explanations. Existing 116 personal seed cards remain optional.

Django/PostgreSQL source + standalone `preview.html`. No secret keys included. Offline HTML cannot call AI; manual prompt/JSON import is supported. Review includes a daily goal, streak and learning buckets; due cards are prioritized and an **Again** card is requeued once later in the same flashcard session.

The pure Python suite ran 76 tests: 75 passed and one optional reportlab test was skipped. 49 Chromium DOM checks passed without the optional legacy-v1 fixture; that fixture raises the suite to 50 checks when supplied. Django `check` passed and `makemigrations --check --dry-run` reported no changes in a temporary validation environment. The 35 Django/PostgreSQL integration tests were prepared but not run because no PostgreSQL listener was available; Docker/full-database flows, real browser storage persistence and live AI calls were not tested. See [test report](docs/TEST_REPORT.md).
