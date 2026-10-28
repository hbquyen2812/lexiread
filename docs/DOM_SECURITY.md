# Rendering untrusted content

The UI treats imported vocabulary, API responses and editorial metadata as text.
Escape individual values before composing a template. The six updated modules
pass the complete template through `LexiDOM.fragment` and insert the
returned nodes with `replaceChildren`, `replaceWith` or `append`.

`static/safe_dom.js` uses the locally hosted DOMPurify 3.4.17 build. It removes
executable HTML, event handlers and unsafe URL schemes. HTML forms, SVG icons,
English-language markers, data attributes and audio controls remain supported.
Missing or unsupported sanitization fails closed. Do not add an identity fallback,
reparse the fragment as HTML, or suppress the scanner findings.

The 22 Sourcery findings identify 11 locations reported by two overlapping rules.
The patch replaces all 48 dynamic HTML writes in those six modules, including
adjacent paths not reported in the original diff. Constant HTML-only assignments
remain. Other modules retain their existing escaping; this is not a claim that the
whole application has received an independent security audit.

## Maintenance and verification

Use Node 22.22.2+, 24.15.0+, or 26+ as specified in `package.json`.

```sh
npm ci --ignore-scripts
npm run vendor:dompurify
npm run test:security
python manage.py test learning.test_static_build --settings=config.test_settings
python scripts/build_preview.py
```

Update the pinned DOMPurify dependency and lockfile before regenerating the vendor
copy; also update its versioned script URL. Retain `static/vendor/DOMPurify-LICENSE`
and `static/vendor/purify.min.js.map`. The minified JS references this map;
omitting it makes production `collectstatic` fail before Gunicorn starts. The
vendor script copies all three files unchanged from the pinned npm package.
The browser loads no CDN or model service for sanitization. Tests use the real
vendored sanitizer with jsdom, verify the vendor bytes against the locked package,
exercise the 11 reported render paths with hostile input, and reject new raw HTML
writes in these modules. Audio integration tests also use this real sanitizer.

The production-static regression test runs the complete WhiteNoise manifest and
compression pipeline in a temporary directory, checks the rewritten source-map
reference and serves hashed JS, source map, CSS, font and SVG through WhiteNoise.
It uses isolated test settings without reading `.env` or connecting to a database.
The GitHub Actions `Production static assets` check runs this test on pull requests
and pushes to `main`. Keep strict manifest validation enabled.

Validated on 2026-10-27: all 17 Node suites, the HTTP QA smoke suite, and a Chromium
import preview containing image event handlers, script tags and SVG handlers.
The payload remained literal text with zero executable nodes in the preview;
it was not saved to an account. See `qa/security-import-20261027.png`.

The remote Sourcery check on commit `1ca3230` concluded `skipped`, not `success`,
because PR #4 exceeded its 150,000-character review limit.
Local coverage is not a substitute for a completed independent scan; check the
latest PR head before merging. No scanner rule has been suppressed.

References: [DOMPurify](https://github.com/cure53/DOMPurify),
[insecure-innerhtml rule](https://github.com/semgrep/semgrep-rules/blob/develop/javascript/browser/security/insecure-innerhtml.yaml),
[insecure-document-method rule](https://github.com/semgrep/semgrep-rules/blob/develop/javascript/browser/security/insecure-document-method.yaml).
