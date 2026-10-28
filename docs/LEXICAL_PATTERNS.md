# Collocations & Word families

Open `/#learn/patterns`. This course is focused on reading and vocabulary, with no runtime AI calls.

- 24 collocation lessons: 144 phrases across eight patterns (verb–noun, adjective–noun, adverb–adjective, verb–preposition, adjective–preposition, noun–preposition, verb–adverb and noun–noun). The first page introduces one lesson per pattern; later pages go further.
- 13 word-family lessons: 24 families, 96 forms. Families are grouped by lesson level, with four or eight entries per lesson.
- 240 contextual multiple-choice questions. Vietnamese meaning cues disambiguate the intended sense; form questions explain the grammatical slot. These are original learning exercises, not official examination questions or official CEFR word ratings.
- Nine original local SVG illustrations distinguish the pattern groups. Word cards use familiar object illustrations where appropriate and compact word-part diagrams for abstract forms; word-family diagrams connect each form to its part of speech. Images are decorative and do not claim to define every sense.
- Each lesson has examples, expandable translations/usage, pronunciation and dictionary IPA where available. The local dictionary does not contain IPA for every multiword phrase; missing IPA is not fabricated.
- “Lưu bộ & ôn thẻ” saves complete phrases/forms and starts the lesson's flashcards without configuration. The flashcard page reloads saved cards by their exact word/meaning fingerprints and owner, not by a potentially ambiguous tag.
- Existing review schedules and previous attempts survive saving or importing again. Progress uses the existing `FoundationAttempt` service and can inform the deterministic learning plan.

## Reference sources and scope

`data/lexical/manifest.json` records archive checksum, attribution, source links and actual imported counts. The large reference table is searched separately from the short teaching lessons, with 12 results per page and indexed exact headword/collocate lookups. No entire reference dump is sent to the browser.

1. **ColloCaid Sample Data v2** — Ana Frankenberg-Garcia, Geraint Rees, Robert Lew, Jonathan Roberts and Peter Butcher. [Dataset and licence](https://doi.org/10.6084/m9.figshare.13028207.v2), CC BY 4.0. Downloaded from Figshare on 28 October 2026; the original ZIP and API metadata are retained. The supplied spreadsheet contains **691 populated rows**, with **two exact duplicates**, producing **689 unique records**. Its description says 692. This is only the published sample, covering 14 distinct headword spellings (16 headword/POS combinations); the full database is not included. Original relation labels, sense indicators, common patterns, corpus counts and example fragments are retained. Excel carriage-return escapes are normalised. Corpus frequencies are not learner levels.
2. **Open English WordNet 2025** — Open English WordNet Team, based on Princeton University WordNet. [Source](https://en-word.net/), CC BY 4.0 plus the underlying Princeton licence. The already installed, checksum-verified archive provides **22,143 direct lexical relation pairs** (`derivation` and `pertainym`). Sense IDs, part of speech and up to three distinct source sense pairs are preserved. Reverse duplicate edges are removed; only lower-case alphabetic entries with spaces, apostrophes or hyphens are included. These relations are **not** transitive word-family clusters, synonym lists or a complete English word-family inventory. The UI labels them related forms and displays their meanings.

3. **UD English EWT 2.18** — [Source and contributors](https://universaldependencies.org/treebanks/en_ewt/index.html), CC BY-SA 4.0, pinned revision `b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c`. The three source splits were downloaded on 28 October 2026; compressed originals, README, complete licence and raw-file SHA-256 hashes are in `data/lexical/ewt/`. Dependency extraction yields **1,887 repeated word pairs with 3,774 original example sentences**. Only five specified dependency/POS combinations are used; proper-name operands, long spans, clause punctuation, function adverbs, contacts/URLs, long numeric strings and unsuitable sentence topics are filtered. Every pair occurs in at least two distinct eligible sentences, with at most two exact source examples retained. Source sentence IDs, split file names and observed surface spans remain available. These are automatically extracted **phrases in context**, not reviewed collocations, certified learner levels or automatically generated exercises. Source sentences can retain informal spelling. The separate derived `ewt/phrases.jsonl.gz` is distributed under **CC BY-SA 4.0**, with source attribution in the interface; this licence does not relicense the separately authored lessons or other reference packs.

WordNet licence copies are in `data/dictionaries/OEWN-LICENSE.md` and `OEWN-WNDB_License.txt`. The original ColloCaid documentation remains inside the downloaded ZIP. Source examples are attributed separately from Lexivela's original bilingual lessons.

The OpenSubtitles collocation dataset was investigated but its data download repeatedly reset the connection. It is **not imported or counted**. No Cambridge/Oxford dictionary body, proprietary corpus or paid exercise bank was copied.

## Rebuild and import

From the repository root, using the project's Python environment:

```sh
python scripts/build_lexical_lessons.py
python scripts/build_ewt_phrases.py
python scripts/build_lexical_reference.py
python scripts/build_pattern_art.py
python manage.py seed_lexical_patterns --check
python manage.py migrate
python manage.py seed_lexical_patterns
```

The build scripts are deterministic and work offline from the bundled source rows/archives. The reference importer validates the archive hash and row counts before writing. Importing is additive and idempotent: existing lesson edits, accounts, personal vocabulary and progress are left intact. Deployment `entrypoint.sh` runs the migration and seed automatically. The QA compose override uses a separate entrypoint, so run migrate and seed explicitly there.

`reference.jsonl.gz` is 3.04 MB and yields **22,832** indexed reference records; the separate EWT file adds **1,887**, for **24,719** total. EWT download can be repeated with `python scripts/build_ewt_phrases.py --download`; the pinned SHA-256 checks reject changed source files. The lesson JSON is separate from the reference data. The catalogue returns course metadata; the normal vocabulary API returns answer-free questions until submission. Personal card responses are `private, no-store`. GET requests never create cards.

The standalone HTML preview continues to explain that foundation courses require the signed-in web app; it does not download the database or silently call an external service.

## Verification

- Reproducible lesson build, source checksums, counts, direct-relation evidence and duplicate handling.
- Authentication, CSRF, answer-free question responses, owned flashcards, bounded pagination, unknown searches, idempotent saves/imports and isolated progress.
- Real DOM + DOMPurify tests for filters, pagination, hostile source text, out-of-order search responses, quiz/retry, direct flashcards and navigation during a pending save.
- Browser checks cover desktop/mobile layouts, local IPA, completing a word-family quiz, reference lookup, saving and reviewing cards, and interface language switching without translating the English being taught.

Verified on 28 October 2026: 171 Django tests on PostgreSQL and all 20 Node test scripts pass. See `docs/qa/lexical-patterns-*-20261028.png` for desktop/mobile proof. The HTTP smoke handles pagination and preserves edited existing vocabulary rather than assuming every saved card is newly created.
