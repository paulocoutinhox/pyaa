from django.test import TestCase

from apps.newsletter.forms import NewsletterForm


class NewsletterFormTest(TestCase):
    def test_valid_email(self):
        form = NewsletterForm(data={"email": "user@example.com"})
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = NewsletterForm(data={"email": "not-an-email"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_is_required(self):
        form = NewsletterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
