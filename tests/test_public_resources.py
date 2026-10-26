"""Metadata catalog and bounded crawler regressions; no network calls in tests."""
import copy
import json
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError, URLError
from urllib.request import Request

from learning.services.public_resources import (
    CATALOG_PATH, official_resource_url, public_resources, validate_catalog,
)
from scripts.crawl_public_resources import Fetcher, ResourceLinks, SafeRedirects, allowed_url


class PublicResourcesTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding='utf-8'))

    def test_reviewed_inventory_and_filter(self):
        rows = validate_catalog(self.catalog)
        self.assertEqual(len(rows), 33)
        self.assertEqual(len(public_resources('ielts')), 28)
        self.assertEqual(len(public_resources('toeic')), 5)
        self.assertEqual(sum(bool(x['answer_url']) for x in rows), 28)
        self.assertTrue(all(x['content_mode'] == 'external_link' for x in rows))
        with self.assertRaises(ValueError):
            public_resources('unknown')

    def test_client_mutation_cannot_change_cached_catalog(self):
        cards = public_resources()
        cards[0]['title'] = 'changed'
        cards[0]['skills'].clear()
        self.assertNotEqual(public_resources()[0]['title'], 'changed')
        self.assertEqual(public_resources()[0]['skills'], ['Reading'])

    def test_expansion_uses_current_worksheets_and_one_iibc_collection(self):
        rows = public_resources()
        worksheets = [r for r in rows if r['id'].endswith('-worksheet')]
        self.assertEqual(len(worksheets), 7)
        self.assertTrue(all('/2026-06/' in r['url'] for r in worksheets))
        iibc = [r for r in rows if 'iibc-global.org' in r['url']]
        self.assertEqual(len(iibc), 1)
        self.assertEqual(iibc[0]['format'], 'collection')
        self.assertTrue(official_resource_url(iibc[0]['url']))
        self.assertTrue(allowed_url(iibc[0]['url']))
        self.assertFalse(allowed_url('https://www.iibc-global.org.example.com/'))

    def test_rejects_unsafe_and_nonofficial_links(self):
        urls = ['javascript:alert(1)', 'http://ielts.org/test',
                'https://ielts.org.example.com/a', 'https://ielts.org@localhost/a',
                'https://127.0.0.1/test', 'https://ielts.org:444/test',
                'https://ielts.org:bad/test', 'https://ielts.org/\nattack']
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(official_resource_url(url))
                self.assertFalse(allowed_url(url))
                self.catalog['resources'][0]['url'] = url
                with self.assertRaises(ValueError):
                    validate_catalog(self.catalog)

    def test_catalog_rejects_duplicates_missing_provenance_and_copied_content(self):
        for key, value in [('id', self.catalog['resources'][1]['id']),
                           ('url', self.catalog['resources'][1]['url']),
                           ('source_url', ''), ('rights', ''), ('last_checked', 'yesterday'),
                           ('content_mode', 'republished'), ('text', 'copied passage')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.catalog)
                data['resources'][0][key] = value
                with self.assertRaises(ValueError):
                    validate_catalog(data)

    def test_parser_resolves_deduplicates_and_discards_prose(self):
        parser = ResourceLinks('https://ielts.org/samples/')
        parser.feed('<h2>Reading sample</h2><p>Do not retain this exam passage.</p>'
                    '<a href="/a.pdf"><b>Reading</b> answer key</a>'
                    '<a href="/a.pdf">Duplicate</a>'
                    '<a href="javascript:alert(1)">Reading sample</a>'
                    '<a href="https://example.com/test.pdf">Reading sample</a>'
                    '<h3>Sentence completion</h3>'
                    '<a href="https://ielts.inspera.com/player/?assessmentRunId=1">Sentence completion</a>')
        self.assertEqual(len(parser.links), 2)
        self.assertEqual(parser.links[0]['url'], 'https://ielts.org/a.pdf')
        self.assertEqual(parser.links[0]['title'], 'Reading answer key')
        self.assertNotIn('passage', json.dumps(parser.links))

    def test_redirect_cannot_escape_allowlist(self):
        with self.assertRaises(ValueError):
            SafeRedirects().redirect_request(Request('https://ielts.org/a'), None,
                                             302, '', {}, 'https://localhost/private')

    def test_parser_discovers_iibc_reading_samples_without_listening_or_other_paths(self):
        parser = ResourceLinks('https://www.iibc-global.org/toeic/test/lr/about/format.html')
        parser.feed('<a href="format/sample05.html">Part5</a>'
                    '<a href="format/sample06.html">Part6</a>'
                    '<a href="format/sample07_04.html">Part7-4</a>'
                    '<a href="format/sample01.html">Part1</a>'
                    '<a href="https://example.com/sample05.html">Reading sample</a>')
        self.assertEqual([x['title'] for x in parser.links], ['Part5', 'Part6', 'Part7-4'])

    def test_robots_denial_blocks_fetch_and_is_cached(self):
        fetcher = Fetcher()
        fetcher.fetch = Mock(return_value=(b'User-agent: *\nDisallow: /', '', '', 200))
        self.assertFalse(fetcher.permitted('https://ielts.org/a'))
        self.assertFalse(fetcher.permitted('https://ielts.org/b'))
        self.assertEqual(fetcher.fetch.call_count, 1)

    def test_robots_unavailable_fails_closed_but_404_allows(self):
        for error, expected in [(URLError('offline'), False),
                                (HTTPError('', 403, '', {}, None), False),
                                (HTTPError('', 404, '', {}, None), True)]:
            fetcher = Fetcher()
            fetcher.fetch = Mock(side_effect=error)
            self.assertEqual(fetcher.permitted('https://ielts.org/a'), expected)

    def test_pdf_probe_requires_mime_and_signature(self):
        fetcher = Fetcher()
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.url, response.status = 'https://ielts.org/a.pdf', 200
        response.headers = {'Content-Type': 'text/html'}
        response.read.return_value = b'<html>Challenge</html>'
        fetcher.opener = Mock()
        fetcher.opener.open.return_value = response
        self.assertEqual(fetcher.probe(response.url)['status'], 'unexpected_content')


if __name__ == '__main__':
    unittest.main()
