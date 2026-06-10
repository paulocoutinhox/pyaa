from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.content.models import Content, ContentCategory
from apps.language import models as language_models


class ContentViewsTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()

        self.category = ContentCategory.objects.create(name="News", tag="news")

        self.content = Content.objects.create(
            site=self.site,
            language=self.language,
            category=self.category,
            title="First Post",
            tag="first-post",
            active=True,
            published_at=timezone.now(),
        )

    def tearDown(self):
        cache.clear()

    def test_contents_index_renders(self):
        response = self.client.get(
            reverse("contents_index_view", kwargs={"category_tag": "news"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/content/index.html")
        self.assertEqual(response.context["category"], self.category)
        self.assertIn(self.content, list(response.context["page_obj"]))

    def test_contents_index_unknown_category_redirects_home(self):
        response = self.client.get(
            reverse("contents_index_view", kwargs={"category_tag": "missing"})
        )

        self.assertRedirects(response, reverse("home"))

    def test_content_by_id_renders(self):
        response = self.client.get(
            reverse("content_by_id", kwargs={"content_id": self.content.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/content/view.html")
        self.assertEqual(response.context["content"], self.content)

    def test_content_by_id_not_found_redirects_home(self):
        response = self.client.get(
            reverse("content_by_id", kwargs={"content_id": 999999})
        )

        self.assertRedirects(response, reverse("home"))

    def test_content_by_tag_renders(self):
        response = self.client.get(
            reverse("content_by_tag", kwargs={"content_tag": "first-post"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/content/view.html")
        self.assertEqual(response.context["content"], self.content)

    def test_content_by_tag_not_found_redirects_home(self):
        response = self.client.get(
            reverse("content_by_tag", kwargs={"content_tag": "missing"})
        )

        self.assertRedirects(response, reverse("home"))
