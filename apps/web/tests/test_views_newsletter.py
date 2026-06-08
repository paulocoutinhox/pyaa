from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class NewsletterSubscribeViewTest(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(reverse("newsletter_subscribe"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/newsletter/subscribe.html")
        self.assertIn("form", response.context)

    @patch("apps.web.views.newsletter.NewsletterHelper.subscribe")
    def test_post_valid_subscribes_and_redirects(self, mock_subscribe):
        response = self.client.post(
            reverse("newsletter_subscribe"),
            {"email": "user@example.com"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("newsletter_success"))
        mock_subscribe.assert_called_once_with("user@example.com")

    @patch("apps.web.views.newsletter.NewsletterHelper.subscribe")
    def test_post_invalid_rerenders_form(self, mock_subscribe):
        response = self.client.post(
            reverse("newsletter_subscribe"),
            {"email": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        mock_subscribe.assert_not_called()


class NewsletterSuccessViewTest(TestCase):
    def test_success_page_renders(self):
        response = self.client.get(reverse("newsletter_success"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/newsletter/success.html")
