from django.contrib.sites.models import Site
from django.test import TestCase

from apps.content.models import Content, ContentCategory
from apps.language.models import Language


class ContentAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = Language.objects.get(id=1)
        self.category = ContentCategory.objects.create(
            name="Test Category", tag="test-category"
        )
        self.content = Content.objects.create(
            site=self.site,
            language=self.language,
            category=self.category,
            title="Test Content",
            tag="test-content",
            content="Test content text",
            active=True,
        )

    def test_get_content_by_tag(self):
        response = self.client.get("/api/content/test-content/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Test Content")
        self.assertEqual(data["tag"], "test-content")
        self.assertEqual(data["content"], "Test content text")

    def test_get_content_by_tag_not_found(self):
        response = self.client.get("/api/content/non-existent/")
        self.assertEqual(response.status_code, 404)

    def test_get_inactive_content(self):
        self.content.active = False
        self.content.save()

        response = self.client.get("/api/content/test-content/")
        self.assertEqual(response.status_code, 404)
