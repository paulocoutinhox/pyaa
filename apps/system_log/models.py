from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.system_log import enums


class SystemLog(models.Model):
    class Meta:
        db_table = "system_log"
        verbose_name = _("model.system-log.name")
        verbose_name_plural = _("model.system-log.name.plural")

        indexes = [
            models.Index(fields=["level"], name="{0}_level".format(db_table)),
            models.Index(fields=["category"], name="{0}_category".format(db_table)),
            models.Index(fields=["created_at"], name="{0}_created_at".format(db_table)),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="system_logs",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="system_logs",
        verbose_name=_("model.field.customer"),
        blank=True,
        null=True,
    )

    level = models.CharField(
        _("model.field.level"),
        max_length=255,
        choices=enums.LogLevel.choices,
        default=enums.LogLevel.DEBUG,
        blank=False,
        null=False,
    )

    category = models.CharField(
        _("model.field.category"),
        max_length=255,
        blank=True,
        null=True,
    )

    description = models.TextField(
        _("model.field.description"),
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.level} - {self.category or 'No Category'}"
