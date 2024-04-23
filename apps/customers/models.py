from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField
from tinymce.models import HTMLField

from apps.customers import enums, fields
from apps.languages import models as language_models
from pyaa.settings import AUTH_USER_MODEL, DEFAULT_TIME_ZONE


class Customer(models.Model):
    class Meta:
        db_table = "customer"
        verbose_name = _("model.customer.name")
        verbose_name_plural = _("model.customer.name.plural")

        indexes = [
            models.Index(
                fields=["language"],
                name="{0}_language".format(db_table),
            ),
            models.Index(
                fields=["mobile_phone"],
                name="{0}_mobile_phone".format(db_table),
            ),
            models.Index(
                fields=["home_phone"],
                name="{0}_home_phone".format(db_table),
            ),
            models.Index(
                fields=["gender"],
                name="{0}_gender".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user",
        verbose_name=_("model.field.user"),
    )

    language = models.ForeignKey(
        language_models.Language,
        on_delete=models.RESTRICT,
        blank=False,
        null=False,
        default=0,
        verbose_name=_("model.field.language"),
    )

    mobile_phone = models.CharField(
        _("model.field.mobile-phone"),
        max_length=11,
        blank=True,
        null=True,
    )

    home_phone = models.CharField(
        _("model.field.home-phone"),
        max_length=11,
        blank=True,
        null=True,
    )

    gender = models.CharField(
        _("model.field.gender"),
        max_length=255,
        choices=enums.CustomerGender.choices,
        default=enums.CustomerGender.NONE,
        blank=True,
        null=True,
    )

    avatar = fields.CustomerImageField(
        _("model.field.avatar"),
        upload_to="images/customer/avatar/%Y/%m/%d",
        blank=True,
        null=True,
    )

    obs = HTMLField(
        _("model.field.obs"),
        blank=True,
        null=True,
    )

    timezone = TimeZoneField(
        _("model.field.timezone"),
        max_length=255,
        default=DEFAULT_TIME_ZONE,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("model.field.updated-at"),
        auto_now=True,
    )

    def __str__(self):
        return self.user.get_full_name()

    def setup_initial_data(self):
        pass


@receiver(models.signals.pre_save, sender=Customer)
def customer_pre_save_callback(sender, instance: Customer, *args, **kwargs):
    instance.setup_initial_data()
