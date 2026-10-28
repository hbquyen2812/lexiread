# Lexivela interface update

The user-facing name is **Lexivela**. The existing repository URL, database,
local-storage keys, JavaScript interfaces, and `lexiread-vocabulary` import format
remain compatible. Existing accounts, saved words and imported decks require no
migration. If a deployment overrides `DEFAULT_FROM_EMAIL`, its sender display
name can be updated separately to Lexivela.

## Learning visuals

Eight original SVG scenes combine the project's existing object illustrations.
They are used in strategy guides, study methods, channel cards, grammar lessons,
vocabulary collections, the study plan and the import workflow. Assets are local,
have intrinsic dimensions, use lazy loading and decorative empty alt text; the
adjacent text contains the actual learning instruction. Regenerate with
`python scripts/build_learning_art.py`. No image-generation service is called by
the application.

Channel learning instructions and supporting information remain available in
collapsed details. Guide instructions and examples are retained. This update
does not add TOEIC listening or change IELTS scoring.

## Navigation

The desktop Menu button hides or opens the left sidebar. The choice is stored on
the device. A closed sidebar is inert and hidden from assistive technology. On
small screens the existing Study menu opens independently of the desktop choice;
navigation and Escape close it. Escape from a focused desktop navigation link
closes the sidebar and returns focus to its Menu button. Reduced-motion settings
disable the slide animation.

## Inline pronunciation

Word audio controls in the vocabulary list, collection cards, dictionary search,
reading suggestions and review cards gain inline IPA from the installed OEWN
dictionary. The existing dictionary modal already shows IPA and is not duplicated.

`POST /api/dictionary/pronunciations/` accepts up to 100 words of 160 characters,
requires authentication and normal CSRF protection, and queries exact normalized
headwords in a single database query. It does not call AI or an external dictionary.
Multiple available transcriptions are preserved (up to four); no accent is
invented. IPA for a lemma is not substituted for the pronunciation of an inflected
word. When IPA is missing, the user can open the dictionary with “Tra phiên âm”.

The browser deduplicates requests and keeps a bounded cache only for the current
page session. IPA is rendered as plain text, including when source data contains
HTML-like characters. File imports and old saved vocabulary continue to work
without an IPA field. The standalone preview does not embed the full dictionary;
its manual lookup fallback remains available.

## Verification, 2026-10-28

- Backend: full Django suite on isolated PostgreSQL test database, including
  one-query batching, headword accuracy, request limits, authentication and CSRF.
- Frontend: all Node suites, including real-DOM tests for sidebar persistence,
  breakpoint changes, focus handling, batched IPA, stale renders and safe text.
- HTTP: authenticated library, grammar, vocabulary, dictionary, backup and plan
  smoke checks against the existing QA database.
- Browser: desktop and narrow mobile layouts, menu persistence and navigation,
  inline IPA, illustrations, English UI and preserved English teaching content.
