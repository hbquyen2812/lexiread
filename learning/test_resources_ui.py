"""The public resource catalog is safe local metadata on both entry pages."""
import copy
import json
from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from learning.models import CuratedLesson, Reading, ToeicPractice
from learning.services.public_resources import official_resource_url, public_resources


class ResourceDataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []
        self.script_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('id') == 'official-resources-data':
            assert attrs.get('type') == 'application/json'
            self.inside = True
            self.script_count += 1

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.inside = False


class PublicResourcesPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='resource-reader')

    def resource_data(self, response):
        self.assertEqual(response.status_code, 200)
        parser = ResourceDataParser()
        parser.feed(response.content.decode())
        self.assertEqual(parser.script_count, 1)
        return json.loads(''.join(parser.parts))

    def test_public_and_signed_in_pages_contain_the_reviewed_official_links(self):
        expected = public_resources()
        for signed_in in (False, True):
            with self.subTest(signed_in=signed_in):
                if signed_in:
                    self.client.force_login(self.user)
                response = self.client.get('/')
                self.assertTemplateUsed(response, 'app.html' if signed_in else 'landing.html')
                rows = self.resource_data(response)
                self.assertEqual(rows, expected)
                self.assertEqual({row['exam'] for row in rows}, {'ielts', 'toeic'})
                self.assertTrue(all(official_resource_url(row['url']) for row in rows))
                self.assertTrue(all(row['content_mode'] == 'external_link' for row in rows))
                self.assertContains(response, '/static/resources.js')

    def test_titles_cannot_break_out_of_embedded_json_on_either_page(self):
        rows = copy.deepcopy(public_resources()[:1])
        attack = '</script><script>window.resourceAttack=1</script><img src=x onerror=alert(1)>'
        rows[0]['title'] = attack
        with patch('learning.services.public_resources.public_resources', return_value=rows):
            for signed_in in (False, True):
                with self.subTest(signed_in=signed_in):
                    if signed_in:
                        self.client.force_login(self.user)
                    response = self.client.get('/')
                    self.assertNotContains(response, attack)
                    self.assertNotContains(response, '<script>window.resourceAttack=1</script>')
                    self.assertEqual(self.resource_data(response)[0]['title'], attack)

    def test_page_requests_neither_fetch_publishers_nor_import_learning_content(self):
        models = (CuratedLesson, Reading, ToeicPractice)
        before = [model.objects.count() for model in models]
        with patch('socket.create_connection', side_effect=AssertionError('Unexpected network fetch')):
            self.resource_data(self.client.get('/'))
            self.client.force_login(self.user)
            self.resource_data(self.client.get('/'))
        self.assertEqual([model.objects.count() for model in models], before)
