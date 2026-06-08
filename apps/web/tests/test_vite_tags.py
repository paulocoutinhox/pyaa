from unittest.mock import patch

from django.test import TestCase

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
