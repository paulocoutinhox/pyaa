from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.content.models import Content


class ContentAPITest(APITestCase):
    fixtures = ["apps/content/fixtures/initial.json"]

    def setUp(self):
        self.client = APIClient()

    def test_get_content_by_tag(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            active=True,
        )

        url = reverse("content-by-tag", kwargs={"tag": content.tag})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Content")

    def test_get_content_by_nonexistent_tag(self):
        url = reverse("content-by-tag", kwargs={"tag": "nonexistent-tag"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_content_by_tag_from_fixture(self):
        url = reverse("content-by-tag", kwargs={"tag": "terms-and-conditions"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Terms and Conditions")

    def test_get_content_by_nonexistent_tag(self):
        url = reverse("content-by-tag", kwargs={"tag": "nonexistent-tag"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_content_tag_creation(self):
        content = Content.objects.create(
            title="Test Content",
            content="<p>Test content</p>",
            active=True,
        )

        self.assertEqual(content.tag, "test-content")
