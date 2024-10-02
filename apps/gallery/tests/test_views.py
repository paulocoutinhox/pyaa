from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.gallery.models import Gallery
from apps.language.models import Language


class GalleryAPITest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.client = APIClient()

    def test_get_galleries(self):
        language = Language.objects.get(code_iso_language="en-US")

        Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        url = reverse("gallery")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            "Test Gallery" in [gallery["title"] for gallery in response.data["results"]]
        )

    def test_get_gallery_by_tag(self):
        language = Language.objects.get(code_iso_language="en-US")
        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        url = reverse("gallery-by-tag", kwargs={"tag": gallery.tag})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Gallery")

    def test_get_nonexistent_gallery_by_tag(self):
        url = reverse("gallery-by-tag", kwargs={"tag": "nonexistent-tag"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
