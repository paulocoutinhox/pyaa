import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class MailHelper:
    @staticmethod
    def send_mail(
        subject,
        to,
        template,
        context=None,
        attachments=None,
        from_email=None,
        reply_to=None,
    ):
        # render html message from the template
        html_message = render_to_string(template, context or {})

        # convert html message to plain text
        soup = BeautifulSoup(html_message, "html.parser")

        for br in soup.find_all("br"):
            br.replace_with("\n")
        for p in soup.find_all("p"):
            p.insert_before("\n")
            p.insert_after("\n")

        text_message = soup.get_text()
        text_message = re.sub(r"\n\s*\n+", "\n\n", text_message.strip())

        # use default from_email if not provided
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL

        # use reply_to if provided, otherwise default to from_email
        reply_to = reply_to or [from_email]

        # create email message object using EmailMultiAlternatives
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
