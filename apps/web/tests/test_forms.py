from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.web.forms.contact import ContactForm


class ContactFormTest(TestCase):
    @override_settings(DEFAULT_TO_EMAIL="contact@example.com")
    @patch("apps.web.forms.contact.EmailHelper.send_email_async")
    def test_send_email_dispatches_async_message(self, mock_send):
        form = ContactForm()
        form.cleaned_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello there",
        }

        form.send_email()

        mock_send.assert_called_once()
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs["to"], ["contact@example.com"])
        self.assertEqual(kwargs["reply_to"], ["john@example.com"])
        self.assertEqual(kwargs["template"], "emails/site/contact.html")
        self.assertEqual(kwargs["context"]["form"], form.cleaned_data)
