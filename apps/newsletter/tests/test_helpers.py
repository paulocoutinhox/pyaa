from django.test import TestCase

from apps.newsletter.helpers import NewsletterHelper
from apps.newsletter.models import NewsletterEntry


class NewsletterHelperTest(TestCase):
    def test_subscribe_creates_entry(self):
        entry = NewsletterHelper.subscribe("user@example.com")

        self.assertIsInstance(entry, NewsletterEntry)
        self.assertEqual(entry.email, "user@example.com")
        self.assertEqual(NewsletterEntry.objects.count(), 1)

    def test_subscribe_is_idempotent(self):
        first = NewsletterHelper.subscribe("user@example.com")
        second = NewsletterHelper.subscribe("user@example.com")

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(NewsletterEntry.objects.count(), 1)
