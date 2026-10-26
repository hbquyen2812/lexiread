# LexiRead Reading Studio v2

Latest addition: [selection dictionary and pronunciation](docs/DICTIONARY_LOOKUP.md). Select a word in a reading to see available Vietnamese glosses, English definitions, IPA and licensed recordings, then save with its context. Oxford/Cambridge are reference links; the integrated public source is Free Dictionary API/Wiktionary with original Commons audio. No AI call or API key is required.

[Public activity statistics and learning methods](docs/COMMUNITY_AND_METHODS_REVIEW.md): the homepage shows real 30-day learning aggregates, excludes internal test accounts and keeps detailed study advice inside the guide.

Previous local review: [foundation learning, personal decks and verified QA](docs/FOUNDATION_LEARNING_REVIEW.md). The interface includes a custom lightweight illustration, prominent personal vocabulary import, an account-based learning path, 33 official IELTS/TOEIC resource links and a catalogue of 40 learning-source links. External materials remain on their publishers' websites; these are not counts of full tests copied into the app.

Reading topic labels stay in English across interface languages, using `data/topic_labels.json`. Search and filters use the displayed English names while retaining stored editorial keys.

A reading-first English/Vietnamese learning app: original lesson and TOEIC-style practice libraries plus private imported readings, with saved-reading search/status/favorites, multi-reading vocabulary occurrences, grounded Q&A and spaced personal review.

Start with [README_VI.md](README_VI.md), the [v2 usage/upgrade guide](docs/READING_STUDIO_V2.md), and the [VPS/HTTPS deployment guide](docs/DEPLOYMENT.md).

37 bundled readings (24 general, 13 original IELTS skill exercises), plus 14 TOEIC sets with 192 questions. Foundation learning adds 30 grammar lessons with 180 original questions and 30 vocabulary collections containing 360 entries and 360 meaning-in-context questions. Course levels guide content selection rather than predict scores. Existing personal seed cards remain optional. The main interface has Vietnamese/English/French/Simplified Chinese selection; foundation teaching content and some labels remain Vietnamese.

Staff can import documents/JSON, preview, save drafts, edit, publish and export through Django admin without changing code. Shared content, including TOEIC, lives in PostgreSQL. The supplied dataset adapter supports 42 reading drafts + 18 TOEIC drafts, preserving 336 questions and 504 vocabulary entries; nothing is automatically published. See [content workflow](docs/LESSON_AUTHORING.md).

Django/PostgreSQL source + standalone `preview.html`. No secret keys included. The server edition has a public feature/lesson catalog, while learning actions require email login and stay isolated per account. Offline HTML cannot call AI; manual prompt/JSON import is supported. Review includes a daily goal, streak, learning buckets and a weak-word group. The server edition includes first-party traffic analytics for administrators without storing IP addresses or loading third-party trackers.

Current verification and limitations: [foundation learning review](docs/FOUNDATION_LEARNING_REVIEW.md). Earlier reports describe their respective revisions. These local changes have not been deployed to Render.
