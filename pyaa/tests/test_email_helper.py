from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from pyaa.helpers.email import EmailHelper


class EmailHelperHtmlToTextTest(TestCase):
    def test_converts_br_to_newline(self):
        result = EmailHelper.html_to_text("Hello<br>World")
        self.assertEqual(result, "Hello\nWorld")

    def test_collapses_multiple_blank_lines(self):
        result = EmailHelper.html_to_text("<p>One</p><p>Two</p>")
        self.assertEqual(result, "One\n\nTwo")

    def test_strips_surrounding_whitespace(self):
        result = EmailHelper.html_to_text("   <p>Content</p>   ")
        self.assertEqual(result, "Content")


class EmailHelperSendEmailTest(TestCase):
    @patch("pyaa.helpers.email.render_to_string", return_value="<p>Body</p>")
    def test_send_email_delivers_message(self, mock_render):
        EmailHelper.send_email(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
        )

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Subject")
        self.assertEqual(message.to, ["user@example.com"])
        self.assertEqual(message.body, "Body")

    @patch("pyaa.helpers.email.render_to_string", return_value="<p>Body</p>")
    def test_send_email_attaches_html_alternative(self, mock_render):
        EmailHelper.send_email(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
        )

        alternatives = mail.outbox[0].alternatives
        self.assertEqual(alternatives[0][0], "<p>Body</p>")
        self.assertEqual(alternatives[0][1], "text/html")

    @patch("pyaa.helpers.email.render_to_string", return_value="<p>Body</p>")
    def test_send_email_with_attachment(self, mock_render):
        EmailHelper.send_email(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
            attachments=[
                {
                    "filename": "file.txt",
                    "content": b"data",
                    "mimetype": "text/plain",
                }
            ],
        )

        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "file.txt")

    @patch("pyaa.helpers.email.render_to_string", return_value="<p>Body</p>")
    @override_settings(DEFAULT_FROM_EMAIL="sender@example.com")
    def test_send_email_uses_default_from_and_reply_to(self, mock_render):
        EmailHelper.send_email(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
        )

        message = mail.outbox[0]
        self.assertEqual(message.from_email, "sender@example.com")
        self.assertEqual(message.reply_to, ["sender@example.com"])

    @patch("pyaa.helpers.email.render_to_string", return_value="<p>Body</p>")
    def test_send_email_with_language(self, mock_render):
        EmailHelper.send_email(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
            language="en",
        )

        self.assertEqual(len(mail.outbox), 1)

    @patch("pyaa.helpers.email.async_task", return_value="task-123")
    def test_send_email_async_schedules_task(self, mock_async_task):
        task_id = EmailHelper.send_email_async(
            subject="Subject",
            to=["user@example.com"],
            template="emails/dummy.html",
        )

        self.assertEqual(task_id, "task-123")
        mock_async_task.assert_called_once()
