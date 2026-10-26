# Public study-source catalog

Reviewed on **2026-10-26**. `data/study_sources.json` contains **40 official-source links**: 16 grammar resources, 14 vocabulary resources, 3 dictionaries, 4 IELTS resources and 3 TOEIC resources. The catalog covers A1, A2, B1, B2, C1 and C2. All Vietnamese descriptions are written for LexiRead.

This is a directory of learning resources, not a collection of imported lessons. The website should open each resource on its publisher's site. Public access does not grant permission to reproduce passages, exercises, answer keys, dictionary entries, word lists, audio or artwork. None of those bodies are stored in this catalog or its crawl report.

## Files and integration

| File | Purpose |
| --- | --- |
| `data/study_sources.json` | Curated metadata for display, search and filtering |
| `scripts/crawl_study_sources.py` | Offline validator and bounded link/metadata checker |
| `data/public_sources/foundation_crawl.json` | Latest recorded network-check results; no response bodies |
| `docs/STUDY_SOURCES.md` | Provenance, level-tag interpretation and update procedure |

The top-level object has `version: 1`, a review date in `checked_at`, and `items`. Each item has exactly `id`, `title`, `provider`, `url`, `levels`, `kind` and `description_vi`. IDs are stable lowercase slugs. `kind` is one of `grammar`, `vocabulary`, `dictionary`, `ielts`, `toeic`. `levels` is an ordered, nonempty subset of A1–C2. URLs and IDs are unique.

Filter by `kind` and membership in `levels`; search `title`, `provider` and `description_vi`. Treat titles as plain text. For links opened in another tab, use `rel="noopener noreferrer"`. The crawl report can be joined by item `id`, but it is a maintenance report, not a learner proficiency score or a guarantee that an interactive exercise works. `checked_at` in the catalog is the editorial review date; an automated run records its own timestamps without silently updating that date.

## Selection and level tags

British Council's [A1–A2 grammar](https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2), [B1–B2 grammar](https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2), [C1 grammar](https://learnenglish.britishcouncil.org/free-resources/grammar/c1), [A1–A2 vocabulary](https://learnenglish.britishcouncil.org/free-resources/vocabulary/a1-a2) and [B1–B2 vocabulary](https://learnenglish.britishcouncil.org/free-resources/vocabulary/b1-b2) provide the published level bands. The catalog includes both these topic indexes and selected direct lessons, so a learner can either browse or start immediately.

Four Cambridge activities explicitly carry **C1–C2** on their official pages: [Precise Words](https://www.cambridgeenglish.org/learning-english/activities-for-learners/c2v001-precise-words), [Statements and Opinions](https://www.cambridgeenglish.org/learning-english/activities-for-learners/c1v002-statements-and-opinions), [Definitions of Formal Words](https://www.cambridgeenglish.org/learning-english/activities-for-learners/c2v072-definitions-of-formal-words) and [Idiomatic Language](https://www.cambridgeenglish.org/learning-english/activities-for-learners/c1v001-idiomatic-language). These supply publisher-labeled advanced practice, rather than treating any difficult-looking text as C2.

Oxford's [CEFR explanation](https://www.oxfordlearnersdictionaries.com/about/wordlists/cefr) places Oxford 3000 at A1–B2 and the additional 2,000 words in Oxford 5000 at B2–C1. The [Oxford Phrase List](https://www.oxfordlearnersdictionaries.com/wordlists/oxford-phrase-list) labels individual phrases. No Oxford list has been relabeled C2, and no list entries have been imported.

For **dictionaries, English Grammar Today, VOA, BBC and exam resources**, `levels` are LexiRead's suggested audience filters, **not publisher-certified CEFR ratings or exam-score conversions**. VOA calls [Let's Learn English — Level 1](https://learningenglish.voanews.com/p/5644.html) a beginner course; the A1–A2 filter is an editorial guide. [Everyday Grammar](https://learningenglish.voanews.com/p/9392.html) is a topic-based reference series. Dictionaries support lookup at different abilities; their inclusion under a level does not mean every definition will be easy for that learner.

IELTS links lead to the official [Academic samples](https://ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test), [General Training samples](https://ielts.org/take-a-test/preparation-resources/sample-test-questions/general-training-test), and British Council Reading practice. TOEIC links lead to [ETS preparation materials](https://www.ets.org/toeic/test-takers/prepare.html), the [Listening and Reading sample PDF](https://www.ets.org/pdfs/toeic/toeic-listening-reading-sample-test.pdf), and the separate [TOEIC Bridge sample PDF](https://www.ets.org/pdfs/toeic/toeic-bridge-sample-test-listening-reading.pdf). Bridge has its own format. The two ETS PDF paths were updated to the current `/pdfs/toeic/` destinations after observing official HTTP 301 redirects from the older `/content/dam/ets-org/pdfs/toeic/` paths and verifying the destinations with web access.

The Oxford dictionary's public A–Z lookup is distinct from its paid extras. The ETS preparation index contains free samples and paid products. Descriptions disclose these distinctions; inclusion in this directory does not promise every linked feature is free.

## What the crawler does

Run from the repository root; Python's standard library is sufficient:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/crawl_study_sources.py --validate
.\.venv\Scripts\python.exe -X utf8 scripts/crawl_study_sources.py --self-test
.\.venv\Scripts\python.exe -X utf8 scripts/crawl_study_sources.py --crawl
```

Without `--crawl`, there is no network access. `--limit N` accepts 1–60 and checks only the first N catalog entries. A partial run replaces the report and explicitly records `not_checked`; use the full command for a complete report. The script has no arbitrary-URL or output-path argument and does not follow links found in page bodies.

The network policy is deliberately bounded:

- Exact allowlisted publisher hosts and learning-resource path prefixes; HTTPS only. Credentials, nonstandard ports, query strings, fragments, traversal, control characters and excessive URL encoding are rejected.
- A named metadata bot, with no browser impersonation, cookie session, authentication or proxy workaround.
- `robots.txt` checked once per host per run. HTTP 404/410 means no published file; failures, HTTP 401/403, binary/interstitial responses and oversized robot files cause the resource to be skipped. Published rules are checked again for each redirect target.
- At least 1.5 seconds between requests to a host, extended by parsed crawl-delay/request-rate rules. Hosts requiring an interval over 10 seconds are skipped in this short-run checker.
- At most 60 catalog items and four redirects per request. Redirects remain within the HTTPS host/path allowlist. A network failure or HTTP 403 is not retried or bypassed.
- Ten-second socket timeout, a 20-second body-read deadline, and an eight-minute limit on starting further requests.
- A 256 KiB HTML/robots cap and a 1 KiB PDF-header probe. An extra byte is read to identify truncation. HTML is used transiently to extract the page title; PDF checks require the PDF MIME type and `%PDF-` signature. No HTML, PDF, robots body, exercise text or extracted lesson content is written to disk.
- Report writes are atomic. The report records the catalog SHA-256, timestamps, policy, response metadata, redirect attempts, robot-check results and per-item status.

`ok` means HTTP success and a matching HTML title or PDF signature. It does **not** mean JavaScript exercises, embedded media, account flows, audio playback or answer submission were tested. A truncated HTML probe can still confirm a complete title near the beginning of a page; it cannot verify the rest of the document. `blocked_robots_unavailable` means no resource request was made because robots could not be checked. It does not establish that the learner-facing URL is dead. `policy_blocked` records a rejected redirect or another local safety limit. Other possible statuses are `blocked_robots`, `http_error`, `network_error` and `unverified_content`.

## Recorded verification

The final run completed at **2026-10-26 08:40:06 UTC** (15:40:06 in Vietnam): **40 checked, 31 `ok`, 9 `blocked_robots_unavailable`, 0 unchecked**. All 31 successful checks returned HTTP 200; the 28 HTML page titles matched the intended resources and three PDF probes had the correct MIME and signature. The report's catalog SHA-256 and all 40 source IDs were checked against the final JSON catalog.

| Local crawler limitation | Affected catalog items | Recorded evidence |
| --- | --- | --- |
| `dictionary.cambridge.org` robots unavailable | 3: Grammar Today, English dictionary, English–Vietnamese dictionary | Robots HTTP 403; target resources were not requested |
| `downloads.bbc.co.uk` robots unavailable | 2: Simple Inversion, Lexical Sets | Robots network `URLError`; the underlying cause was not classified |
| `learningenglish.voanews.com` robots unavailable | 2: Everyday Grammar, Let's Learn English 1 | Robots network `URLError`; the underlying cause was not classified |
| `takeielts.britishcouncil.org` robots unavailable | 2: Academic and General Training Reading | Robots network `TimeoutError` |

Consult the report's `summary` and `robots` arrays for the machine-readable details. All 40 catalog resources were reviewed through official publisher pages, their official indexes or web search metadata. Network checks and web-tool evidence are reported separately.

The web tool opened the official BBC [Simple Inversion PDF](https://downloads.bbc.co.uk/learningenglish/eiam/unit-1/191025_simple_inversion.pdf) and [Lexical Sets PDF](https://downloads.bbc.co.uk/learningenglish/lowerintermediate/unit7/141110_6minvocab_lexical_sets.pdf) as PDFs of one and five pages respectively. BBC's main site was blocked by the web tool's robots policy; it was not crawled through another route. The catalog uses separately published official download links found in search, not a mirror of the blocked main site.

The web tool also identified both VOA series on their official pages and opened the British Council IELTS practice pages. Those findings do not override a failure to retrieve their robots files in the local crawler. Cambridge Dictionary's three direct opens returned HTTP 403; official indexed metadata established the resource identity, including the [English–Vietnamese dictionary](https://dictionary.cambridge.org/dictionary/english-vietnamese/). No dictionary entry bodies were imported or fetched through a workaround.

Nine offline self-tests cover catalog/category/CEFR coverage, duplicate and invalid-level rejection, unsafe URL rejection, robot denial, robot HTTP 403, binary robots responses, off-allowlist redirects, robot checks on redirect targets and false PDF MIME claims. They passed when the catalog and crawler were prepared.

## Updating

1. Review the official publisher resource and write a short original Vietnamese description. Preserve existing IDs when correcting a URL.
2. Use the publisher's CEFR labels where available; otherwise keep the audience-tag interpretation above. Do not infer a resource's license from its public visibility.
3. Add a narrowly scoped host/path only after checking an official source or redirect. Never broaden to wildcard hosts to make a failed check pass.
4. Run offline validation and self-tests, then perform a single complete `--crawl` when network access is available.
5. Review failures and changed titles. Record unresolved limits honestly; do not replace a blocked result with `ok` merely because a search engine knows the URL.

No production database, account, deployment, previous catalog or existing crawler is modified by these four files.
