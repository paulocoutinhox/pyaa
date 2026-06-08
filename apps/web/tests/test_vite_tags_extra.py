import json
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.web.templatetags import pyaa_vite

MANIFEST = {
    "frontend.js": {
        "file": "assets/frontend.abc123.js",
        "name": "frontend",
        "isEntry": True,
        "css": ["assets/frontend.def456.css"],
    }
}


class GetManifestTest(TestCase):
    def setUp(self):
        # reset module-level cache before each test
        pyaa_vite._manifest_cache = None
        self.addCleanup(setattr, pyaa_vite, "_manifest_cache", None)

    @override_settings(DEBUG=False)
    def test_reads_manifest_and_caches_when_not_debug(self):
        with patch(
            "apps.web.templatetags.pyaa_vite.Path.read_text",
            return_value=json.dumps(MANIFEST),
        ) as mock_read:
            first = pyaa_vite.get_manifest()
            second = pyaa_vite.get_manifest()

        self.assertEqual(first, MANIFEST)
        self.assertEqual(second, MANIFEST)
        # cached on the second call, so the file is only read once
        mock_read.assert_called_once()

    @override_settings(DEBUG=True)
    def test_rereads_manifest_each_call_when_debug(self):
        with patch(
            "apps.web.templatetags.pyaa_vite.Path.read_text",
            return_value=json.dumps(MANIFEST),
        ) as mock_read:
            pyaa_vite.get_manifest()
            pyaa_vite.get_manifest()

        # debug mode resets the cache, forcing a read on every call
        self.assertEqual(mock_read.call_count, 2)
