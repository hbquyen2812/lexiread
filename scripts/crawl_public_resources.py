"""Bounded discovery of official practice-resource links, never exam-text import.

Run explicitly by an editor. It writes a review report, not the live catalog.
Only the configured HTTPS publishers are contacted; redirects stay allowlisted.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'LexiReadResourceCatalog/1.0 (metadata-only educational link checker)'
MAX_BYTES = 2_000_000
MAX_LINKS = 100
HOSTS = frozenset({'ielts.org', 'www.ielts.org', 'cdn.ielts.org',
    'takeielts.britishcouncil.org', 'ielts.idp.com', 'www.ets.org',
    'ielts.inspera.com', 'demo-ielts.inspera.com', 'www.iibc-global.org'})
SOURCES = (
    ('ielts-academic', 'https://ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test'),
    ('ielts-general', 'https://ielts.org/take-a-test/preparation-resources/sample-test-questions/general-training-test'),
    ('british-council-academic', 'https://takeielts.britishcouncil.org/prepare/ielts-free-practice-mock-tests/academic/reading'),
    ('british-council-general', 'https://takeielts.britishcouncil.org/prepare/ielts-free-practice-mock-tests/general-training/reading'),
    ('ets-toeic', 'https://www.ets.org/toeic/test-takers/prepare.html'),
    ('idp-reading', 'https://ielts.idp.com/prepare/all-test-types/reading'),
    ('british-council-reading-lessons', 'https://takeielts.britishcouncil.org/teach-ielts/teaching-resources/lesson-plans-reading'),
    ('iibc-toeic-samples', 'https://www.iibc-global.org/toeic/test/lr/about/format.html'),
)


def allowed_url(url):
    try:
        p = urlsplit(url)
        return (p.scheme == 'https' and p.hostname in HOSTS and p.port in (None, 443)
                and not p.username and not p.password and not any(ord(c) < 32 for c in url))
    except (ValueError, TypeError):
        return False


class SafeRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError('Redirect outside official HTTPS allowlist')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class ResourceLinks(HTMLParser):
    """Extract short link labels and their nearest heading, discarding prose."""
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url, self.links = base_url, []
        self.heading, self.heading_tag, self.heading_parts = '', '', []
        self.href, self.label = None, []

    def handle_starttag(self, tag, attrs):
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading_tag, self.heading_parts = tag, []
        if tag == 'a':
            self.href, self.label = dict(attrs).get('href'), []

    def handle_data(self, data):
        if self.heading_tag:
            self.heading_parts.append(data)
        if self.href is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == self.heading_tag:
            self.heading = ' '.join(' '.join(self.heading_parts).split())[:180]
            self.heading_tag = ''
        if tag == 'a' and self.href is not None:
            url = urljoin(self.base_url, self.href)
            title = ' '.join(' '.join(self.label).split())[:180]
            haystack = (title + ' ' + url + ' ' + self.heading).lower()
            parts = urlsplit(url)
            iibc_reading = (parts.hostname == 'www.iibc-global.org' and
                            re.fullmatch(r'/toeic/test/lr/about/format/sample(?:0[56]|07_0[1-4])\.html', parts.path))
            if (allowed_url(url) and (any(t in haystack for t in ('reading', 'sample', 'practice'))
                                      or 'inspera.com' in urlsplit(url).hostname)
                    and ('.pdf' in urlsplit(url).path.lower() or 'inspera.com' in urlsplit(url).hostname
                         or 'practice' in urlsplit(url).path.lower() or iibc_reading)):
                item = {'title': title, 'url': url, 'heading': self.heading}
                if not any(x['url'] == url for x in self.links) and len(self.links) < MAX_LINKS:
                    self.links.append(item)
            self.href, self.label = None, []


class Fetcher:
    def __init__(self, delay=1.5):
        self.delay, self.last_request = max(1.0, delay), 0.0
        self.opener = build_opener(SafeRedirects())
        self.robots = {}

    def fetch(self, url):
        if not allowed_url(url):
            raise ValueError('URL outside official HTTPS allowlist')
        time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        with self.opener.open(Request(url, headers={'User-Agent': USER_AGENT}), timeout=20) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise ValueError('Response exceeded 2 MB limit')
            return body, response.url, response.headers.get('Content-Type', ''), response.status

    def probe(self, url):
        """Inspect at most 4 KB for link health; do not retain exam content."""
        if not allowed_url(url):
            raise ValueError('URL outside official HTTPS allowlist')
        time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        with self.opener.open(Request(url, headers={'User-Agent': USER_AGENT}), timeout=20) as response:
            prefix = response.read(4096)
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if urlsplit(url).path.lower().endswith('.pdf'):
                valid = prefix.startswith(b'%PDF-') and content_type == 'application/pdf'
            else:
                valid = content_type == 'text/html' and bool(prefix.strip())
            return {'status': 'ok' if valid else 'unexpected_content', 'http_status': response.status,
                    'final_url': response.url, 'content_type': content_type, 'bytes_inspected': len(prefix)}

    def permitted(self, url):
        p = urlsplit(url)
        origin = f'{p.scheme}://{p.netloc}'
        if origin not in self.robots:
            parser = RobotFileParser(origin + '/robots.txt')
            try:
                body, _, _, _ = self.fetch(parser.url)
                parser.parse(body.decode('utf-8', errors='replace').splitlines())
                self.robots[origin] = parser
            except HTTPError as exc:
                # An absent robots file allows discovery; denial and outages fail closed.
                self.robots[origin] = True if exc.code == 404 else False
            except (URLError, TimeoutError, OSError, ValueError):
                self.robots[origin] = False
        result = self.robots[origin]
        if isinstance(result, bool):
            return result
        delay = result.crawl_delay(USER_AGENT) or result.crawl_delay('*')
        if delay:
            self.delay = max(self.delay, delay)
        return result.can_fetch(USER_AGENT, url)


def crawl(sources=SOURCES, delay=1.5):
    fetcher = Fetcher(delay)
    report = {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'mode': 'metadata_only', 'sources': []}
    for key, url in sources:
        record = {'id': key, 'url': url, 'links': []}
        try:
            if not fetcher.permitted(url):
                record['status'] = 'robots_denied_or_unavailable'
            else:
                body, final_url, content_type, status = fetcher.fetch(url)
                if 'text/html' not in content_type:
                    raise ValueError('Expected an HTML source page')
                parser = ResourceLinks(final_url)
                parser.feed(body.decode('utf-8', errors='replace'))
                record.update(status='ok', http_status=status, final_url=final_url,
                              sha256=hashlib.sha256(body).hexdigest(), bytes_read=len(body),
                              links=parser.links)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            record.update(status='error', error=type(exc).__name__)
        report['sources'].append(record)
        print(f"{key}: {record['status']} ({len(record['links'])} candidate links)", flush=True)
    return report


def check_catalog_links():
    raw = json.loads((ROOT / 'data/public_sources/catalog.json').read_text(encoding='utf-8'))
    urls = dict.fromkeys(row[field] for row in raw['resources']
                        for field in ('url', 'answer_url') if row.get(field))
    fetcher = Fetcher()
    report = {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'mode': 'http_metadata_only', 'links': []}
    for url in urls:
        record = {'url': url}
        try:
            record.update(fetcher.probe(url) if fetcher.permitted(url)
                          else {'status': 'robots_denied_or_unavailable'})
        except HTTPError as exc:
            record.update(status='http_error', http_status=exc.code)
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            record.update(status='error', error=type(exc).__name__)
        report['links'].append(record)
        print(f"{urlsplit(url).hostname}: {record['status']}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--source', choices=[x[0] for x in SOURCES], action='append')
    parser.add_argument('--check-links', action='store_true', help='Check reviewed catalog targets and answer links, without downloading files')
    args = parser.parse_args()
    sources = [x for x in SOURCES if not args.source or x[0] in args.source]
    report = check_catalog_links() if args.check_links else crawl(sources)
    output = args.output or ROOT / ('data/public_sources/link_health.json' if args.check_links
                                   else 'data/public_sources/crawl_report.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Review report: {output}')
    return 0 if all(x['status'] == 'ok' for x in report.get('links', report.get('sources', []))) else 1


if __name__ == '__main__':
    sys.exit(main())
