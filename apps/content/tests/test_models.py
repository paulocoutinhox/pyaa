from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from apps.content.models import Content, ContentCategory


class ContentModelTest(TestCase):
    fixtures = ["apps/content/fixtures/initial.json"]

    def setUp(self):
        self.category = ContentCategory.objects.create(
            name="Test Category", tag="test-category"
        )

    def test_content_creation_with_category(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            category=self.category,
            active=True,
        )

        self.assertTrue(Content.objects.filter(title="Test Content").exists())
        self.assertEqual(content.category, self.category)

    def test_content_deletion(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            category=self.category,
            active=True,
        )

        content.delete()

        self.assertFalse(Content.objects.filter(title="Test Content").exists())

    def test_get_content(self):
        Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            category=self.category,
            active=True,
        )

        fetched_content = Content.objects.get(title="Test Content")

        self.assertEqual(fetched_content.title, "Test Content")
        self.assertEqual(fetched_content.category, self.category)

    def test_get_nonexistent_content(self):
        with self.assertRaises(ObjectDoesNotExist):
            Content.objects.get(title="Nonexistent Content")

    def test_content_str(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            category=self.category,
            active=True,
        )

        self.assertEqual(str(content), "Test Content")

    def test_get_content_by_tag_from_fixture(self):
        content = Content.objects.get(tag="terms-and-conditions")
        self.assertEqual(content.title, "Terms and Conditions")
        self.assertEqual(content.tag, "terms-and-conditions")
        self.assertTrue(content.active)

    def test_get_content_by_tag_from_fixture_privacy_policy(self):
        content = Content.objects.get(tag="privacy-policy")
        self.assertEqual(content.title, "Privacy Policy")
        self.assertEqual(content.tag, "privacy-policy")
        self.assertTrue(content.active)

    def test_get_nonexistent_content_by_tag(self):
        with self.assertRaises(ObjectDoesNotExist):
            Content.objects.get(tag="nonexistent-tag")


class ContentCategoryModelTest(TestCase):
    def test_content_category_creation(self):
        category = ContentCategory.objects.create(
            name="Test Category", tag="test-category"
        )

        self.assertTrue(ContentCategory.objects.filter(name="Test Category").exists())
        self.assertEqual(category.tag, "test-category")

    def test_content_category_deletion(self):
        category = ContentCategory.objects.create(
            name="Test Category", tag="test-category"
        )
        category.delete()

        self.assertFalse(ContentCategory.objects.filter(name="Test Category").exists())

    def test_content_category_str(self):
        category = ContentCategory.objects.create(
            name="Test Category", tag="test-category"
        )

        self.assertEqual(str(category), "Test Category")

    def test_get_nonexistent_category(self):
        with self.assertRaises(ObjectDoesNotExist):
            ContentCategory.objects.get(name="Nonexistent Category")
