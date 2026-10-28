"""Exercise the production static pipeline without .env or a database connection."""
import io
import json
import posixpath
import re
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings
from whitenoise.middleware import WhiteNoiseMiddleware


class ProductionStaticBuildTests(SimpleTestCase):
    def test_manifest_build_and_serving_include_vendor_source_map(self):
        with TemporaryDirectory(prefix='lexivela-static-test-') as output, override_settings(
            DEBUG=False,
            STATIC_ROOT=output,
            STORAGES={
                'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
                'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
            },
            WHITENOISE_USE_FINDERS=False,
            WHITENOISE_AUTOREFRESH=False,
        ):
            # Scans every shipped CSS/JS dependency, just as the deployment does.
            call_command('collectstatic', interactive=False, verbosity=0, stdout=io.StringIO())
            root = Path(output)
            paths = json.loads((root / 'staticfiles.json').read_text(encoding='utf8'))['paths']
            js = root / paths['vendor/purify.min.js']
            reference = re.search(r'//# sourceMappingURL=(\S+)', js.read_text(encoding='utf8'))
            self.assertIsNotNone(reference)
            self.assertEqual(posixpath.join('vendor', reference.group(1)), paths['vendor/purify.min.js.map'])
            source_map = json.loads((root / paths['vendor/purify.min.js.map']).read_text(encoding='utf8'))
            self.assertEqual(source_map['version'], 3)
            self.assertEqual(source_map['file'], 'purify.min.js')

            # Serve the collected hashed files through the actual production middleware.
            serve = WhiteNoiseMiddleware(lambda request: HttpResponse(status=404))
            for asset in ('vendor/purify.min.js', 'vendor/purify.min.js.map', 'app.css',
                          'fonts/noto-serif-500.woff2', 'illustrations/patterns/noun-noun.svg'):
                with self.subTest(asset=asset):
                    response = serve(RequestFactory().get('/static/' + paths[asset]))
                    try:
                        self.assertEqual(response.status_code, 200)
                        self.assertIn('immutable', response['Cache-Control'])
                        self.assertEqual(b''.join(response.streaming_content), (root / paths[asset]).read_bytes())
                    finally:
                        response.close()
