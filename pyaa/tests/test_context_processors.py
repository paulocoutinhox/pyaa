from unittest.mock import patch

from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase, override_settings

from pyaa.context_processors import cookie_consent_processor, site_processor


class SiteProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_current_site(self):
        request = self.factory.get("/")
        result = site_processor(request)

        self.assertEqual(result["site"], Site.objects.get_current())

    def test_returns_none_when_lookup_fails(self):
        request = self.factory.get("/")

        with patch(
            "pyaa.context_processors.Site.objects.get_current",
            side_effect=Site.DoesNotExist,
        ):
            result = site_processor(request)

        self.assertIsNone(result["site"])


class CookieConsentProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(GOOGLE_ANALYTICS_ID="GA-TEST-123", COOKIE_CONSENT_VERSION="9")
    def test_returns_settings_values(self):
        request = self.factory.get("/")
        result = cookie_consent_processor(request)

        self.assertEqual(result["google_analytics_id"], "GA-TEST-123")
        self.assertEqual(result["cookie_consent_version"], "9")
