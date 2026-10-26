# Foundation learning and personal decks — 26 October 2026

## Delivered in the local web app

- Home: a prominent personal-deck import action in the hero and a dedicated feature card. The vocabulary library also prioritizes importing a complete set over entering individual words.
- Level selection: a separate “Tất cả trình độ” control; CEFR tiles show the level only. Removed repeated estimate labels and duplicate level controls. The old browser-local home plan is replaced by the account-based learning path, so two different goals are no longer shown.
- `/#learn/plan`: level, goal and daily study time; instructions for using LexiRead at each level; recommendations explained in a collapsed detail panel.
- `/#learn/grammar`: 30 original grammar lessons, five per level A1–C2, with 180 original questions, examples and Vietnamese explanations.
- `/#learn/vocabulary`: 30 collections, 360 original word entries with meanings, usage patterns and translated examples. Each collection also has 12 automatically assembled meaning-in-context questions: 360 questions in total.
- `/#learn/dictionary`: accent-insensitive local lookup across these entries, plus explicit outbound searches in Cambridge, Oxford and Merriam-Webster. It is a learning-word index, not a complete copied dictionary.
- `/#learn/sources`: 40 official learning-source links. The metadata crawl verified 31; nine were stopped because robots could not be checked. No publisher passages, answer banks, audio or paid content were copied.
- Collection actions save selected words together, preserve existing review schedules, then open review filtered to that collection. The learning and quiz views switch without requiring a long scroll through the word cards.

Content provenance and review: [grammar](GRAMMAR_CONTENT_REVIEW.md), [vocabulary](VOCABULARY_COLLECTIONS_REVIEW.md), [sources and crawler](STUDY_SOURCES.md). Course levels are editorial groupings, with a single expandable explanation in the UI. IELTS/TOEIC sources remain distinguished from LexiRead-authored practice.

## Recommendation rules

The server uses the learner's selected level, goal, time budget and owned progress. There are no AI/model calls or live third-party requests in this flow.

1. Reserve five minutes for vocabulary already due.
2. Prioritize weaker/due grammar, followed by new grammar at the selected level. Only prerequisites within that level gate new content; a C1 learner does not have to redo all A1 lessons.
3. Use recent reading/TOEIC results to revisit weaker exercises and choose work appropriate to the goal.
4. Add a vocabulary collection when time remains. Suggested task times stay inside the selected budget.

Grammar/collection review uses up to three recent scores, weighted 50/30/20 and normalized when fewer attempts exist. Review dates are one, three or seven days later according to the weighted result. A higher-level suggestion requires at least three completed grammar topics at 80% or above; the learner chooses whether to change level. This is not a calibrated placement test or band prediction.

Only the result fields needed by the planner are read from attempt history, avoiding loading full reading/quiz snapshots for recommendations.

## Persistence and safeguards

- Migration `0010_foundationattempt_learningprofile` adds per-user preferences and quiz attempts.
- Server-side grading validates all answers and rejects stale content versions. UUID retry tokens are unique per owner; repeated requests return the existing result.
- GET quiz payloads omit keyed answers and explanations; feedback is returned after submission.
- Vocabulary saving uses the existing fingerprint-based merge and transactions, preserving review progress and enforcing tag limits.
- Backup v5 includes preferences and foundation attempts. Restore regrades stored questions and merges without replacing existing preferences or attempts. Versions 1–4 remain supported by the web server.
- The standalone HTML preview still supports its existing reading/deck flows. Foundation pages explicitly direct users to the server edition. It rejects v5 restore instead of silently dropping new progress.
- The local test account requested in chat was created in disposable QA only. Its password is not written to source files or documentation.

## Verification

- 117/117 Django tests passed against isolated PostgreSQL, including 11 foundation integration tests. The final planner query optimization was additionally checked with the 11 focused tests.
- 110 pure Python tests ran: 109 passed, one optional PDF/reportlab test skipped.
- Nine crawler policy tests passed: allowlist, redirects, robots denial, MIME and PDF signature handling.
- Frontend logic suites passed for shared library/i18n, learning hub/practice tools, personal decks, YouTube channels and the new academy. Added checks cover escaping, safe outbound URLs and the compact level picker.
- Live HTTP smoke passed for authentication, 79 readings, 32 TOEIC sets, foundation catalogues, dictionary search, time budgets, private answers, backup and assets.
- Production static packaging: 169 files copied, 493 post-processed.
- Browser: grammar submission 5/6, feedback and wrong-only filtering; collection save of 12 words; vocabulary quiz 12/12; review opened with the collection selected; B1/TOEIC/30-minute preference saved and a weak TOEIC result was selected for review; dictionary lookup; C2 source filters; public and authenticated reading filters.
- No horizontal overflow in the checked foundation routes at 320, 768 and 1440 px; plan and public home additionally checked at 390 and 1024 px. Home import card checked at 390 px. No browser errors/warnings observed.

Screenshots: [home import feature](qa/import-feature-home-desktop.jpg), [mobile import feature](qa/import-feature-home-mobile.jpg), [learning path](qa/foundation-plan-desktop.jpg), [mobile path](qa/foundation-plan-mobile.jpg).

The QA app runs at `http://127.0.0.1:8766/`. These changes are local, not pushed or deployed to the public site. The temporary QA PostgreSQL data is lost if its database container is removed.
