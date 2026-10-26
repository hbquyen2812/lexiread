# Vocabulary collections review

Reviewed: 2026-10-26

## Deliverable

`data/vocabulary_collections.json` contains 30 original themed collections, five at each suggested study level A1, A2, B1, B2, C1 and C2. Each collection contains 12 entries: 360 entries in total, with 360 distinct headwords and 360 distinct example sentences.

Each entry includes a selected Vietnamese meaning, a part of speech for that sense, an original English sentence, a natural Vietnamese translation, and a usable grammatical pattern or collocation. No IPA or pronunciation claim is supplied.

The level is an editorial recommendation for studying the collection in context. It is **not an official CEFR classification of each word**, a comprehensive level syllabus, or an official IELTS/TOEIC vocabulary list. A familiar word can appear at a higher level when its selected sense or context is more demanding. The tags describe useful contexts, not endorsement by an examination provider.

Suggested learner-facing note: “A1–C2 là mức học gợi ý cho từng bộ, dựa trên nghĩa và cách dùng trong bài.”

## Coverage

| Suggested level | Five themes | Entries |
| --- | --- | ---: |
| A1 | Daily routines; home; food and shopping; places and transport; people and classroom | 60 |
| A2 | Travel plans; health habits; workday; money and shopping; learning plans | 60 |
| B1 | Teamwork; greener living; sharing opinions; reading news; relationships | 60 |
| B2 | Business projects; academic analysis; media literacy; society and change; linking ideas | 60 |
| C1 | Research quality; organizations; evaluating arguments; environmental policy; academic writing | 60 |
| C2 | Argument and logic; meaning and style; institutions; complex systems; careful judgment | 60 |

## Research boundaries and provenance

The collection structure and contextual progression were informed by [Oxford's word-list guidance](https://www.oxfordlearnersdictionaries.co.uk/about/wordlists/oxford3000-5000), [British Council vocabulary guidance](https://learnenglish.britishcouncil.org/free-resources/vocabulary), its [A1–A2 topic lessons](https://learnenglish.britishcouncil.org/free-resources/vocabulary/a1-a2), and [Oxford's learner-dictionary guidance](https://learningenglishwithoxford.oup.com/2021/02/17/how-to-online-learner-dictionaries/amp/). Oxford's 3000/5000 lists are not evidence that our C2 grouping is officially classified.

Bounded primary-source checks focused on meanings that are particularly easy to blur:

- [Responsibility](https://dictionary.cambridge.org/dictionary/english/responsibility?topic=duty-obligation-and-responsibility): responsibility for an activity.
- [Confounding variable](https://dictionary.cambridge.org/dictionary/english/confounding-variable?topic=scientific-techniques) and [empirical](https://dictionary.cambridge.org/dictionary/english/empirical): causal interpretation versus observed evidence.
- [Qualify](https://dictionary.cambridge.org/dictionary/english/qualify): limiting a claim, rather than gaining a qualification.
- [Oversight](https://dictionary.cambridge.org/dictionary/english/oversight): supervision, with a note separating the alternative “mistake” sense.
- [Tenable](https://dictionary.cambridge.org/us/dictionary/english/tenable?topic=suitable-and-acceptable) and [specious](https://dictionary.cambridge.org/dictionary/english/specious): defensible reasoning versus apparent but false plausibility.
- [Connotation](https://dictionary.cambridge.org/dictionary/english/connotation) and [Cambridge's discussion of understatement](https://dictionaryblog.cambridge.org/2014/07/30/its-not-bad-emphasizing-with-negatives-in-english/?amp=1): direct meaning versus rhetorical effect.
- [Subsidiarity](https://dictionary.cambridge.org/dictionary/english/subsidiarity) and [remit](https://dictionary.cambridge.org/dictionary/english/remit?topic=duty-obligation-and-responsibility): decision-making level versus an assigned scope of responsibility.
- [Contingent on](https://dictionary.cambridge.org/dictionary/english/contingent-on-upon?q=contingent-on-upon-something) and [path dependence](https://dictionary.cambridge.org/example/english/path-dependence): conditional outcomes versus the influence of earlier choices.
- [Disinterested](https://dictionary.cambridge.org/us/dictionary/english/disinterested): lack of a personal stake, explicitly distinguished from “uninterested”.

Research used official search results and available indexed dictionary text. Some direct dictionary opens returned 403; this review does not claim all pages were directly accessible or that all 360 entries received an individual dictionary lookup. Collection-level `source_urls` record references used for topic design or selected sense checks, not a source attribution for every sentence.

The word selection, Vietnamese explanations, sentence examples and translations were authored for this project. Dictionary definitions, corpus sentences and lesson exercises were not copied into the dataset. Common headwords and short grammatical patterns are used as teaching material.

## Editorial checks

All 360 entries were read during composition and reviewed for alignment between the selected sense, part of speech, example and translation. The final pass improved “paradigm”, “contingency”, “recourse” and “disinterested” to avoid awkward phrasing or a mismatch between the meaning and example.

Examples use the exact target form, including multiword phrases. Entries distinguish borrowing from lending, revenue from profit, correlation from causation, and an impartial perspective from a personal lack of interest. Uncountable items such as luggage, homework, progress and evidence have concise usage reminders. Advanced examples remain practice contexts; they are not claims about named organizations or current events.

## Validation

An inline Python check passed after final edits:

- Exact top-level and collection/word schemas; version 1.
- 30 unique collection IDs; five collections per level; 12 entries per collection.
- 360 globally unique headwords and 360 unique example sentences.
- Exact target headword or phrase present in every example, ignoring case.
- Allowed parts of speech and tags only; non-empty trimmed strings.
- HTTPS source URLs; no replacement characters, HTML or invented IPA fields.
- JSON parses as UTF-8; level prefixes match collection IDs.

No application files, databases or production configuration were changed by this content task. The integration owner should display the study-level note and perform the website's usual rendering/import checks. Content is frozen for integration.
