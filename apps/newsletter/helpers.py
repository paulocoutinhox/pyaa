from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.newsletter.models import NewsletterEntry


class NewsletterHelper:
    @staticmethod
    @transaction.atomic
    def subscribe(email):
        """
        Subscribe an email to the newsletter.
        If the email already exists, it will not raise an error.

        :param email: The email to subscribe
        :return: The newsletter object
        """
        newsletter, _ = NewsletterEntry.objects.get_or_create(
            email=email,
            defaults={"email": email},
        )
        return newsletter
