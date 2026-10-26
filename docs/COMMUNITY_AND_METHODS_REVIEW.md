# Public learning activity and study methods

## Scope

- Homepage: a compact activity summary and one short link to learning methods. Existing reading, personal deck import and learning path actions retain priority. No additional sidebar item.
- Cẩm nang → Cách học hiệu quả (`/#guides/methods`, public `/guides/#guides/methods`): three methods with collapsed instructions, original examples, references and links into the existing study tools. Level guidance for A1–A2, B1–B2 and C1–C2; an adjustable 15-minute routine is an editorial suggestion, not a research prescription.

## Statistics contract

Anonymous read-only `GET /api/community/` returns only aggregates for today and the previous 29 calendar days in the application timezone. It shares a 60-second server snapshot with the public landing page; an open page does not poll. Navigating back to the homepage fetches a fresh snapshot.

- **Tài khoản đã học:** distinct account IDs with a `LearningDay` in the window. Registration alone and page views do not count. This is an account count, not a claim of distinct human beings.
- **Bài luyện đã làm:** persisted submissions across reading, TOEIC, grammar and vocabulary exercises. Deliberate retries count as additional submissions; idempotent request retries remain one database record.
- **Lượt ôn từ:** persisted `ReviewLog` records in the window, one per card review, not distinct words or study sessions.

All three exclude inactive users, staff, superusers and accounts listed in `PUBLIC_STATS_EXCLUDED_USERNAMES` (default `qa-reader,qa-editor`). These are counts of records currently retained, so deleting data can reduce them; restored history falls into its recorded date window. No usernames, session keys, answers or personal histories are public. Admin traffic analytics remain staff-only.

QA labels say **Hoạt động bản thử nghiệm**; the disclosure distinguishes this from production users. Zero is displayed honestly. An unavailable summary is omitted on the SPA rather than replaced with fabricated zeros. The offline HTML preview has no system statistics.

## Sources checked 2026-10-26

- [Retrieval Practice: What is retrieval practice?](https://www.retrievalpractice.org/why-it-works) — recall before revealing answers.
- [Retrieval Practice: Spacing](https://www.retrievalpractice.org/spacing) — distribute review across sessions.
- [Retrieval Practice: FAQ](https://www.retrievalpractice.org/faq) — feedback and explanations after recall.
- [The Learning Scientists: Six Strategies](https://www.learningscientists.org/blog/2016/8/18-1) — background review; supports prioritising retrieval and spacing, without promising a fixed score increase.

The Vietnamese instructions, examples and website actions are original adaptations. No article text, diagrams or paid learning material copied.

## Verification

- 123 Django tests passed on the isolated PostgreSQL QA database, including six new tests for count definitions, unique learners, exclusion rules, date boundaries, zero state, public privacy, read-only methods, demo labels and snapshot caching.
- Node checks passed for method navigation, disclosure defaults, level guidance, demo/zero states, invalid count rejection, channel tabs, existing frontend and academy logic.
- Local HTTP smoke passed for public pages, method assets, aggregate response, existing login, private data, curriculum, dictionary and planner.
- Browser: homepage statistics, explanations, methods tab, level switch and grammar CTA checked. Desktop and 390 px mobile inspected; no horizontal overflow. Mobile counter alignment corrected after visual inspection.
- Screenshots in `docs/qa/community-stats-*.jpg` and `docs/qa/learning-methods-*.jpg`.

No production database changes, hosting deployment, push or AI calls were performed. No synthetic usage was added to the public counts.
