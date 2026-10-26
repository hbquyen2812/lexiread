import json
from copy import deepcopy
from pathlib import Path
import unittest
from learning.services.learning_channels import validate_channels,learning_channels,safe_url,LEVELS

class LearningChannelTests(unittest.TestCase):
    def test_reviewed_catalog_covers_every_level_and_has_unique_channels(self):
        rows=learning_channels()
        self.assertEqual(len(rows),8)
        self.assertEqual({level for row in rows for level in row['levels']},LEVELS)
        self.assertEqual(len({r['channel_url'] for r in rows}),len(rows))
        rows[0]['name']='edited'
        self.assertNotEqual(learning_channels()[0]['name'],'edited')

    def test_outbound_links_reject_non_https_credentials_and_fake_hosts(self):
        for url in ['javascript:alert(1)','http://www.youtube.com/@TED','https://www.youtube.com.evil.test/x','https://user@www.youtube.com/x','https://www.youtube.com:8443/x','https://www.youtube.com/\nx']:
            with self.subTest(url=url):self.assertFalse(safe_url(url))
        self.assertTrue(safe_url('https://www.youtube.com/@TED',True))
        self.assertFalse(safe_url('https://www.ted.com/',True))

    def test_editorial_metadata_is_validated(self):
        raw=json.loads((Path(__file__).resolve().parents[1]/'data/learning_channels.json').read_text(encoding='utf-8'))
        for field,value in [('levels',['B9']),('skills',['unknown']),('channel_url','https://evil.test/'),('checked_at','soon'),('description_vi','')]:
            bad=deepcopy(raw);bad['channels'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_channels(bad)
        bad=deepcopy(raw);bad['channels'].append(bad['channels'][0])
        with self.assertRaises(ValueError):validate_channels(bad)
