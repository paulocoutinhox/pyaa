import json

from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner, BannerAccess
from apps.language import models as language_models


@override_settings(BANNER_ACCESS_INTERVAL=3600)
class BannerTrackViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()
        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Banner",
            image="banner.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

    def _post(self, url_name, payload):
        return self.client.post(
            reverse(url_name),
            data=json.dumps(payload),
            content_type="application/json",
            REMOTE_ADDR="192.168.1.1",
        )

    def test_track_view_access_success(self):
        response = self._post(
            "banner_track_view_access", {"token": str(self.banner.token)}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(
            BannerAccess.objects.filter(
                banner=self.banner, access_type=BannerAccessType.VIEW
            ).count(),
            1,
        )

    def test_track_click_access_success(self):
        response = self._post(
            "banner_track_click_access", {"token": str(self.banner.token)}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(
            BannerAccess.objects.filter(
                banner=self.banner, access_type=BannerAccessType.CLICK
            ).count(),
            1,
        )

    def test_track_view_access_missing_token(self):
        response = self._post("banner_track_view_access", {})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Token is required")

    def test_track_click_access_missing_token(self):
        response = self._post("banner_track_click_access", {})

        self.assertEqual(response.status_code, 400)

    def test_track_view_access_banner_not_found(self):
        response = self._post(
            "banner_track_view_access",
            {"token": "00000000-0000-0000-0000-000000000000"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Banner not found")

    def test_track_click_access_banner_not_found(self):
        response = self._post(
            "banner_track_click_access",
            {"token": "00000000-0000-0000-0000-000000000000"},
        )

        self.assertEqual(response.status_code, 404)

    def test_track_view_access_requires_post(self):
        response = self.client.get(reverse("banner_track_view_access"))
        self.assertEqual(response.status_code, 405)
