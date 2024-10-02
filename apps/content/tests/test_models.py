from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from apps.content.models import Content


class ContentModelTest(TestCase):
    fixtures = ["apps/content/fixtures/initial.json"]

    def test_content_creation(self):
        Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            active=True,
        )

        self.assertTrue(Content.objects.filter(title="Test Content").exists())

    def test_content_deletion(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            active=True,
        )

        content.delete()

        self.assertFalse(Content.objects.filter(title="Test Content").exists())

    def test_get_content(self):
        Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
            active=True,
        )

        fetched_content = Content.objects.get(title="Test Content")

        self.assertEqual(fetched_content.title, "Test Content")

    def test_get_nonexistent_content(self):
        with self.assertRaises(ObjectDoesNotExist):
            Content.objects.get(title="Nonexistent Content")

    def test_content_str(self):
        content = Content.objects.create(
            title="Test Content",
            tag="test-content",
            content="<p>Test content</p>",
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
