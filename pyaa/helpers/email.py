import logging
import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django_q.tasks import async_task

logger = logging.getLogger(__name__)


class EmailHelper:
    @staticmethod
    def send_email(
        subject,
        to,
        template,
        context=None,
        attachments=None,
        from_email=None,
        reply_to=None,
        language=None,
    ):
        """
        Sends an email with both HTML and plain text versions.
        """
        # render html message from the template
        if language:
            with translation.override(language):
                html_message = render_to_string(template, context or {})
        else:
            html_message = render_to_string(template, context or {})

        # convert html to plain text
        text_message = EmailHelper.html_to_text(html_message)

        # use default from_email if not provided
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        reply_to = reply_to or [from_email]

        # create email message object
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=from_email,
            to=to,
            reply_to=reply_to,
        )

        # attach the html alternative version
        email.attach_alternative(html_message, "text/html")

        # attach any provided files
        if attachments:
            for attachment in attachments:
                email.attach(
                    attachment["filename"],
                    attachment["content"],
                    attachment["mimetype"],
                )

        # send email
        email.send(fail_silently=False)
        logger.info(f"Email sent successfully to {to}")

    @staticmethod
    def html_to_text(html):
        """
        Converts HTML email content to plain text.
        """
        soup = BeautifulSoup(html, "html.parser")

        for br in soup.find_all("br"):
            br.replace_with("\n")
        for p in soup.find_all("p"):
            p.insert_before("\n")
            p.insert_after("\n")

        text_message = soup.get_text()
        return re.sub(r"\n\s*\n+", "\n\n", text_message.strip())

    @staticmethod
    def send_email_async(
        subject,
        to,
        template,
        context=None,
        attachments=None,
        from_email=None,
        reply_to=None,
        language=None,
    ):
        """
        Sends an email asynchronously using Django Q.
        Uses the same format and parameters as the send email method.
        """
        # schedule the email sending task for asynchronous execution
        task_id = async_task(
            EmailHelper.send_email,
            subject,
            to,
            template,
            context,
            attachments,
            from_email,
            reply_to,
            language,
        )

        logger.info(f"Async email scheduled for {to} with task_id: {task_id}")

        return task_id
