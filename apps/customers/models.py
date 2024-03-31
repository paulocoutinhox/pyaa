import uuid
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField
from tinymce.models import HTMLField

from apps.customers import enums, fields
from apps.languages import models as language_models
from pyaa.settings import DEFAULT_TIME_ZONE


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
                fields=["name"],
                name="{0}_name".format(db_table),
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
                fields=["status"],
                name="{0}_status".format(db_table),
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

    name = models.CharField(
        _("model.field.name"),
        max_length=255,
    )

    language = models.ForeignKey(
        language_models.Language,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
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

    email = models.CharField(
        _("model.field.email"),
        max_length=255,
        blank=False,
        unique=True,
        null=False,
        validators=[EmailValidator()],
    )

    auth_key = models.CharField(
        _("model.field.auth-key"),
        max_length=32,
        default=uuid.uuid4,
        blank=False,
        unique=True,
        null=False,
        editable=False,
    )

    password_hash = models.CharField(
        _("model.field.password-hash"),
        max_length=255,
        blank=False,
        unique=True,
        null=False,
        editable=False,
    )

    password_reset_token = models.CharField(
        _("model.field.password-reset-token"),
        max_length=32,
        blank=True,
        unique=True,
        null=True,
        editable=False,
    )

    verification_token = models.CharField(
        _("model.field.verification-token"),
        max_length=32,
        blank=True,
        unique=True,
        null=True,
        editable=False,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        choices=enums.CustomerStatus.choices,
        default=enums.CustomerStatus.ACTIVE,
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
    )

    logged_at = models.DateTimeField(
        _("model.field.logged-at"),
        editable=False,
        blank=True,
        null=True,
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
        return self.name

    def setup_initial_data(self):
        self.verification_token = uuid.uuid4()

    def setup_password_data(self, password):
        self.password_hash = make_password(password)

    def setup_logged_at(self):
        self.logged_at = datetime.now()


@receiver(models.signals.pre_save, sender=Customer)
def customer_pre_save_callback(sender, instance, *args, **kwargs):
    # instance.logged_at = datetime.now()
    pass
