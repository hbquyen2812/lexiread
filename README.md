# LexiRead Reading Studio v2

[Optional English audio](docs/READ_ALOUD.md): listen to library/IELTS/private readings, TOEIC documents, dictionary words/examples, personal vocabulary, topic cards and grammar examples. Passage controls include pause/resume, speed, English voice selection and highlighting. Word controls prefer existing dictionary recordings and fall back to installed device voices, without AI calls or new backend audio storage.

Latest addition: [topic vocabulary and a database-backed dictionary](docs/LOCAL_VOCABULARY.md). Explore 15 topics / 30 collections, learn with flip cards, practise and save individual words for review. The bundled OEWN release loads 127,311 normalized headwords, including 27,581 with IPA; the supplementary pack includes 197 licensed recordings. Definitions and recording bytes are served from the database without AI or runtime dictionary-provider calls. Oxford/Cambridge remain reference links.

[Public activity statistics and learning methods](docs/COMMUNITY_AND_METHODS_REVIEW.md): the homepage shows real 30-day learning aggregates, excludes internal test accounts and keeps detailed study advice inside the guide.

Previous local review: [foundation learning, personal decks and verified QA](docs/FOUNDATION_LEARNING_REVIEW.md). The interface includes a custom lightweight illustration, prominent personal vocabulary import, an account-based learning path, 33 official IELTS/TOEIC resource links and a catalogue of 40 learning-source links. External materials remain on their publishers' websites; these are not counts of full tests copied into the app.

Reading topic labels stay in English across interface languages, using `data/topic_labels.json`. Search and filters use the displayed English names while retaining stored editorial keys.

A reading-first English/Vietnamese learning app: original lesson and TOEIC-style practice libraries plus private imported readings, with saved-reading search/status/favorites, multi-reading vocabulary occurrences, grounded Q&A and spaced personal review.

Start with [README_VI.md](README_VI.md), the [v2 usage/upgrade guide](docs/READING_STUDIO_V2.md), and the [VPS/HTTPS deployment guide](docs/DEPLOYMENT.md).

37 bundled readings (24 general, 13 original IELTS skill exercises), plus 14 TOEIC sets with 192 questions. Foundation learning adds 36 grammar lessons with 216 original questions, including 16 guided A1–A2 lessons and 30 vocabulary collections containing 360 entries and 360 meaning-in-context questions. The grammar reference adds 132 irregular verbs, 12 tense summaries and six comparisons, embedded in seven tense lessons. Search, self-review and reference content run without AI calls. Course levels guide content selection rather than predict scores. Existing personal seed cards remain optional. The main interface has Vietnamese/English/French/Simplified Chinese selection; foundation teaching content and some labels remain Vietnamese.

Staff can import documents/JSON, preview, save drafts, edit, publish and export through Django admin without changing code. Shared content, including TOEIC, lives in PostgreSQL. The supplied dataset adapter supports 42 reading drafts + 18 TOEIC drafts, preserving 336 questions and 504 vocabulary entries; nothing is automatically published. See [content workflow](docs/LESSON_AUTHORING.md).

Django/PostgreSQL source + standalone `preview.html`. No secret keys included. The server edition has a public feature/lesson catalog, while learning actions require email login and stay isolated per account. Offline HTML cannot call AI; manual prompt/JSON import is supported. Review includes a daily goal, streak, learning buckets and a weak-word group. The server edition includes first-party traffic analytics for administrators without storing IP addresses or loading third-party trackers.

Current verification and limitations: [foundation learning review](docs/FOUNDATION_LEARNING_REVIEW.md). Earlier reports describe their respective revisions. These local changes have not been deployed to Render.

V3 content is bundled offline: 486 reading units, 3,240 reading questions and 3,572 vocabulary contexts, with additive database seeding. See [the v3 import notes](docs/CONTENT_V3.md).
