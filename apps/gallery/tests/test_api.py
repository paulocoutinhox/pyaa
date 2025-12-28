from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

from apps.gallery.models import Gallery
from apps.language.models import Language


class GalleryAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = Language.objects.get(id=1)
        self.gallery1 = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="Gallery 1",
            tag="gallery-1",
            active=True,
            published_at=timezone.now(),
        )
        self.gallery2 = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="Gallery 2",
            tag="gallery-2",
            active=True,
            published_at=timezone.now(),
        )
        self.inactive_gallery = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="Inactive Gallery",
            tag="inactive-gallery",
            active=False,
            published_at=timezone.now(),
        )

    def test_list_galleries(self):
        response = self.client.get("/api/gallery/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertEqual(data["count"], 2)

    def test_list_galleries_pagination(self):
        response = self.client.get("/api/gallery/?limit=1&offset=0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 1)

    def test_list_galleries_excludes_inactive(self):
        response = self.client.get("/api/gallery/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        tags = [item["tag"] for item in data["items"]]
        self.assertNotIn("inactive-gallery", tags)

    def test_get_gallery_by_tag(self):
        response = self.client.get("/api/gallery/gallery-1/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Gallery 1")
        self.assertEqual(data["tag"], "gallery-1")

    def test_get_gallery_by_tag_not_found(self):
        response = self.client.get("/api/gallery/non-existent/")
        self.assertEqual(response.status_code, 404)

    def test_get_inactive_gallery(self):
        response = self.client.get("/api/gallery/inactive-gallery/")
        self.assertEqual(response.status_code, 404)
