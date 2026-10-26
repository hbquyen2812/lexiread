# LexiRead Reading Studio v2

Latest local review: [reading-garden design, official resources and verified QA](docs/REVIEW_2026_10_26.md). The interface includes a custom lightweight illustration and 23 reviewed official IELTS/TOEIC resource links, with search, filters, answer links and a reproducible metadata crawler. External exams remain on their publishers' websites; this is not a count of full tests copied into the app.

A reading-first English/Vietnamese learning app: original lesson and TOEIC-style practice libraries plus private imported readings, with saved-reading search/status/favorites, multi-reading vocabulary occurrences, grounded Q&A and spaced personal review.

Start with [README_VI.md](README_VI.md), the [v2 usage/upgrade guide](docs/READING_STUDIO_V2.md), and the [VPS/HTTPS deployment guide](docs/DEPLOYMENT.md).

27 bundled readings (24 general A1–C1, 3 original IELTS skill exercises), plus two TOEIC sets with 24 questions and 16 vocabulary entries. Levels are estimates, not calibrated levels or score predictions. Existing 116 personal seed cards remain optional. The main interface has Vietnamese/English/French/Simplified Chinese selection; some legacy labels remain Vietnamese.

Staff can import documents/JSON, preview, save drafts, edit, publish and export through Django admin without changing code. Shared content, including TOEIC, lives in PostgreSQL. The supplied dataset adapter supports 42 reading drafts + 18 TOEIC drafts, preserving 336 questions and 504 vocabulary entries; nothing is automatically published. See [content workflow](docs/LESSON_AUTHORING.md).

Django/PostgreSQL source + standalone `preview.html`. No secret keys included. The server edition has a public feature/lesson catalog, while learning actions require email login and stay isolated per account. Offline HTML cannot call AI; manual prompt/JSON import is supported. Review includes a daily goal, streak, learning buckets and a weak-word group. The server edition includes first-party traffic analytics for administrators without storing IP addresses or loading third-party trackers.

Current verification and limitations: [editorial update report](docs/EDITORIAL_UPDATE_QA.md). Earlier [TEST_REPORT.md](docs/TEST_REPORT.md) results describe the previous revision, not visual/PostgreSQL verification of this update. These local changes have not been deployed to Render.
