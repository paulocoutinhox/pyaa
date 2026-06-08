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
    },
    "admin.js": {
        "file": "assets/admin.789xyz.js",
        "name": "admin",
        "isEntry": True,
        "css": [],
    },
}


class ViteTagsTest(TestCase):
    def setUp(self):
        patcher = patch.object(pyaa_vite, "get_manifest", return_value=MANIFEST)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_vite_js_returns_hashed_path(self):
        result = pyaa_vite.vite_js("frontend.js")
        self.assertIn("assets/frontend.abc123.js", result)

    def test_vite_js_resolves_entry_by_name(self):
        result = pyaa_vite.vite_js("frontend")
        self.assertIn("assets/frontend.abc123.js", result)

    def test_vite_css_returns_hashed_path(self):
        result = pyaa_vite.vite_css("frontend.js")
        self.assertIn("assets/frontend.def456.css", result)

    def test_vite_css_without_css_returns_empty(self):
        self.assertEqual(pyaa_vite.vite_css("admin.js"), "")

    def test_vite_all_css_renders_link_tags(self):
        result = pyaa_vite.vite_all_css()
        self.assertIn('<link rel="stylesheet"', result)
        self.assertIn("assets/frontend.def456.css", result)

    def test_vite_all_js_renders_script_tags(self):
        result = pyaa_vite.vite_all_js()
        self.assertIn("<script", result)
        self.assertIn("assets/frontend.abc123.js", result)
        self.assertIn("assets/admin.789xyz.js", result)

    def test_get_entry_raises_for_unknown_entry(self):
        with self.assertRaises(ValueError):
            pyaa_vite._get_entry(MANIFEST, "missing")


GET_MANIFEST_TEST_MANIFEST = {
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
            "apps.web.templatetags.pyaa_vite.Path.exists", return_value=True
        ), patch(
            "apps.web.templatetags.pyaa_vite.Path.read_text",
            return_value=json.dumps(GET_MANIFEST_TEST_MANIFEST),
        ) as mock_read:
            first = pyaa_vite.get_manifest()
            second = pyaa_vite.get_manifest()

        self.assertEqual(first, GET_MANIFEST_TEST_MANIFEST)
        self.assertEqual(second, GET_MANIFEST_TEST_MANIFEST)
        # cached on the second call, so the file is only read once
        mock_read.assert_called_once()

    @override_settings(DEBUG=True)
    def test_rereads_manifest_each_call_when_debug(self):
        with patch(
            "apps.web.templatetags.pyaa_vite.Path.exists", return_value=True
        ), patch(
            "apps.web.templatetags.pyaa_vite.Path.read_text",
            return_value=json.dumps(GET_MANIFEST_TEST_MANIFEST),
        ) as mock_read:
            pyaa_vite.get_manifest()
            pyaa_vite.get_manifest()

        # debug mode resets the cache, forcing a read on every call
        self.assertEqual(mock_read.call_count, 2)

    @override_settings(DEBUG=False)
    def test_returns_empty_manifest_when_file_missing(self):
        # a missing build manifest must not crash template rendering
        with patch(
            "apps.web.templatetags.pyaa_vite.Path.exists", return_value=False
        ), patch("apps.web.templatetags.pyaa_vite.Path.read_text") as mock_read:
            manifest = pyaa_vite.get_manifest()

        self.assertEqual(manifest, {})
        mock_read.assert_not_called()
