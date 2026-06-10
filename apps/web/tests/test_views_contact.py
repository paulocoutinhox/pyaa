from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


class ContactIndexViewTest(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(reverse("contact_index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact/index.html")
        self.assertIn("form", response.context)

    @override_settings(DEFAULT_TO_EMAIL="contact@example.com")
    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.web.forms.contact.EmailHelper.send_email_async")
    def test_post_valid_sends_email_and_redirects(self, mock_send, mock_captcha):
        response = self.client.post(
            reverse("contact_index"),
            {
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Hello there",
                "g-recaptcha-response": "PASSED",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("contact_index"))
        mock_send.assert_called_once()

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.web.forms.contact.EmailHelper.send_email_async")
    def test_post_invalid_rerenders_form(self, mock_send, mock_captcha):
        response = self.client.post(
            reverse("contact_index"),
            {
                "name": "",
                "email": "not-an-email",
                "message": "",
                "g-recaptcha-response": "PASSED",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact/index.html")
        self.assertTrue(response.context["form"].errors)
        mock_send.assert_not_called()
