from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.gallery.models import Gallery, GalleryPhoto
from apps.language import models as language_models


class GalleryViewsTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        # use the language matching the active translation so list filtering matches
        self.language = language_models.Language.objects.filter(
            code_iso_639_1="en"
        ).first()

        self.gallery = Gallery.objects.create(
            site=self.site,
            language=self.language,
            title="My Gallery",
            tag="my-gallery",
            active=True,
        )

        self.photo = GalleryPhoto.objects.create(
            gallery=self.gallery,
            image="images/gallery/photo.jpg",
            main=True,
        )

    def tearDown(self):
        cache.clear()

    def test_gallery_index_renders(self):
        response = self.client.get(reverse("gallery_index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/gallery/index.html")
        self.assertIn("page_obj", response.context)

    def test_gallery_by_id_renders(self):
        response = self.client.get(
            reverse("gallery_by_id", kwargs={"gallery_id": self.gallery.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/gallery/view.html")
        self.assertEqual(response.context["gallery"], self.gallery)
        self.assertIn(self.photo, list(response.context["page_obj"]))

    def test_gallery_by_id_not_found_redirects_home(self):
        response = self.client.get(
            reverse("gallery_by_id", kwargs={"gallery_id": 999999})
        )

        self.assertRedirects(response, reverse("home"))

    def test_gallery_by_tag_renders(self):
        response = self.client.get(
            reverse("gallery_by_tag", kwargs={"gallery_tag": "my-gallery"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/gallery/view.html")
        self.assertEqual(response.context["gallery"], self.gallery)

    def test_gallery_by_tag_not_found_redirects_home(self):
        response = self.client.get(
            reverse("gallery_by_tag", kwargs={"gallery_tag": "missing"})
        )

        self.assertRedirects(response, reverse("home"))
