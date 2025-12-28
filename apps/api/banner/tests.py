import uuid

from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner
from apps.language.models import Language


class BannerAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = Language.objects.get(id=1)
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg",
        )
        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            zone=BannerZone.HOME,
            title="Test Banner",
            image=image,
            link="https://example.com",
            active=True,
            start_at=timezone.now(),
            end_at=timezone.now() + timezone.timedelta(days=30),
        )

    def test_list_banners(self):
        response = self.client.get(f"/api/banner/?zone={BannerZone.HOME.value}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_list_banners_with_language(self):
        response = self.client.get(
            f"/api/banner/?zone={BannerZone.HOME.value}&language=en"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_list_banners_with_site(self):
        response = self.client.get(
            f"/api/banner/?zone={BannerZone.HOME.value}&site={self.site.id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_track_banner_access_view(self):
        response = self.client.get(
            f"/api/banner/access/{self.banner.token}/?type={BannerAccessType.VIEW.value}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)

    def test_track_banner_access_click(self):
        response = self.client.get(
            f"/api/banner/access/{self.banner.token}/?type={BannerAccessType.CLICK.value}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)

    def test_track_banner_access_not_found(self):
        invalid_uuid = uuid.uuid4()
        response = self.client.get(
            f"/api/banner/access/{invalid_uuid}/?type={BannerAccessType.VIEW.value}"
        )
        self.assertEqual(response.status_code, 404)

    def test_track_banner_access_invalid_type(self):
        response = self.client.get(
            f"/api/banner/access/{self.banner.token}/?type=invalid"
        )
        self.assertEqual(response.status_code, 400)
