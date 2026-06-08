from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.helpers import BannerHelper
from apps.banner.models import Banner, BannerAccess
from apps.language import models as language_models


class BannerHelperBranchTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.factory = RequestFactory()

        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Branch Banner",
            image="banner.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

    def tearDown(self):
        cache.clear()

    def test_get_banners_with_falsy_language(self):
        # get_language returning None should skip the lower() branch (19->23)
        with patch("apps.banner.helpers.get_language", return_value=None):
            banners = BannerHelper.get_banners(BannerZone.HOME)
            self.assertIsNotNone(banners)

    def test_get_banners_with_explicit_site_id(self):
        # passing site_id keeps the value and skips the SITE_ID default (23->27)
        banners = BannerHelper.get_banners(
            BannerZone.HOME, language="en", site_id=self.site.id
        )
        self.assertIn(self.banner, banners)

    @override_settings(BANNER_ACCESS_INTERVAL=3600)
    def test_track_banner_access_with_valid_country_code(self):
        # a valid two letter country code is kept (148->152)
        request = self.factory.get("/")
        request.META = {
            "REMOTE_ADDR": "192.168.1.1",
            "HTTP_CF_IPCOUNTRY": "br",
        }

        class _User:
            is_authenticated = False

            def has_customer(self):
                return False

        request.user = _User()

        result = BannerHelper.track_banner_access(
            request, self.banner, BannerAccessType.VIEW
        )

        self.assertTrue(result)
        access = BannerAccess.objects.get(banner=self.banner)
        self.assertEqual(access.country_code, "BR")

    @override_settings(BANNER_ACCESS_INTERVAL=3600)
    def test_track_banner_access_invalid_ip_value_error(self):
        # client ip that passes ipware but fails ipaddress validation (119-121)
        request = self.factory.get("/")
        request.META = {"REMOTE_ADDR": "192.168.1.1"}
        request.user = None

        with patch(
            "apps.banner.helpers.get_client_ip", return_value=("not-an-ip", True)
        ):
            result = BannerHelper.track_banner_access(
                request, self.banner, BannerAccessType.VIEW
            )

        self.assertFalse(result)
        self.assertEqual(BannerAccess.objects.filter(banner=self.banner).count(), 0)
