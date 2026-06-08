from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase

from apps.newsletter.models import NewsletterEntry


class NewsletterEntryModelTest(TestCase):
    def test_newsletter_entry_creation(self):
        entry = NewsletterEntry.objects.create(email="user@example.com")

        self.assertTrue(
            NewsletterEntry.objects.filter(email="user@example.com").exists()
        )
        self.assertIsNotNone(entry.created_at)

    def test_newsletter_entry_str(self):
        entry = NewsletterEntry.objects.create(email="user@example.com")
        self.assertEqual(str(entry), "user@example.com")

    def test_newsletter_entry_email_is_unique(self):
        NewsletterEntry.objects.create(email="user@example.com")

        with self.assertRaises(IntegrityError):
            NewsletterEntry.objects.create(email="user@example.com")

    def test_newsletter_entry_deletion(self):
        entry = NewsletterEntry.objects.create(email="user@example.com")
        entry.delete()

        self.assertFalse(
            NewsletterEntry.objects.filter(email="user@example.com").exists()
        )

    def test_get_nonexistent_entry(self):
        with self.assertRaises(ObjectDoesNotExist):
            NewsletterEntry.objects.get(email="missing@example.com")
