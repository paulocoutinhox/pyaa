from django.db import models
from django.utils.translation import gettext_lazy as _


class NewsletterEntry(models.Model):
    class Meta:
        db_table = "newsletter_entry"
        verbose_name = _("model.newsletter-entry.name")
        verbose_name_plural = _("model.newsletter-entry.name.plural")
        indexes = [
            models.Index(
                fields=["email"],
                name="{0}_email".format(db_table),
            ),
            models.Index(
                fields=["created_at"],
                name="{0}_created_at".format(db_table),
            ),
        ]

    email = models.EmailField(
        _("model.field.email"),
        unique=True,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    def __str__(self):
        return self.email
