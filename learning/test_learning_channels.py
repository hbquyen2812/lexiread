import json
import re
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase

class LearningChannelPageTests(TestCase):
    def test_public_guide_page_has_channels_without_network_and_noscript_links(self):
        with patch('httpx.get',side_effect=AssertionError('No remote request during page load')):
            response=self.client.get('/guides/')
        self.assertContains(response,'learning_channels.js')
        self.assertContains(response,'#guides/youtube')
        self.assertContains(response,'<noscript>')
        match=re.search(r'<script id="learning-channels-data" type="application/json">(.*?)</script>',response.content.decode(),re.S)
        self.assertEqual(len(json.loads(match.group(1))),8)
        self.assertNotContains(response,'<iframe')

    def test_signed_in_page_escapes_channel_data_and_keeps_existing_guides(self):
        self.client.force_login(get_user_model().objects.create_user(username='channel-reader'))
        with patch('learning.services.learning_channels.learning_channels',return_value=[{'name':'</script><img src=x onerror=alert(1)>'}]):
            response=self.client.get('/')
        self.assertNotContains(response,'<img src=x')
        self.assertContains(response,'\\u003C/script\\u003E')
        self.assertContains(response,'strategy-guides-data')
        self.assertContains(response,'learning_channels.css')
