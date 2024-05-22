from django.db import models
from django.utils.translation import gettext_lazy as _

from pyaa.settings import AUTH_USER_MODEL


class Subscription(models.Model):
    class Meta:
        db_table = "subscription"
        verbose_name = _("model.subscription.name")
        verbose_name_plural = _("model.subscription.name.plural")

        indexes = [
            models.Index(
                fields=["external_id"],
                name="{0}_external_id".format(db_table),
            ),
            models.Index(
                fields=["gateway"],
                name="{0}_gateway".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name=_("model.field.user"),
    )

    external_id = models.CharField(
        _("model.field.external-id"),
        max_length=255,
    )

    gateway = models.CharField(
        _("model.field.gateway"),
        max_length=255,
    )

    def __str__(self):
        return f"{self.gateway} - {self.external_id}"
