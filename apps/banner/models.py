import uuid

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.banner.enums import BannerAccessType, BannerZone
from apps.customer.models import Customer
from apps.language import models as language_models


class Banner(models.Model):
    class Meta:
        db_table = "banner"
        verbose_name = _("model.banner.name")
        verbose_name_plural = _("model.banner.name.plural")

        indexes = [
            models.Index(fields=["title"], name="{0}_title".format(db_table)),
            models.Index(fields=["token"], name="{0}_token".format(db_table)),
            models.Index(fields=["zone"], name="{0}_zone".format(db_table)),
            models.Index(fields=["sort_order"], name="{0}_sort_order".format(db_table)),
            models.Index(fields=["active"], name="{0}_active".format(db_table)),
            models.Index(fields=["start_at"], name="{0}_start_at".format(db_table)),
            models.Index(fields=["end_at"], name="{0}_end_at".format(db_table)),
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
        related_name="banners",
        verbose_name=_("model.field.site"),
        blank=True,
        null=True,
    )

    language = models.ForeignKey(
        language_models.Language,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("model.field.language"),
    )

    token = models.UUIDField(
        _("model.field.token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    title = models.CharField(
        _("model.field.title"),
        max_length=255,
    )

    image = models.ImageField(
        _("model.field.image"),
        upload_to="images/banner/%Y/%m/%d",
    )

    link = models.URLField(
        _("model.field.link"),
        max_length=255,
        blank=True,
        null=True,
    )

    target_blank = models.BooleanField(
        _("model.field.target-blank"),
        default=False,
    )

    zone = models.CharField(
        _("model.field.zone"),
        max_length=50,
        choices=BannerZone.choices,
    )

    sort_order = models.IntegerField(
        _("model.field.sort-order"),
        default=0,
    )

    start_at = models.DateTimeField(
        _("model.field.start-at"),
        blank=True,
        null=True,
    )

    end_at = models.DateTimeField(
        _("model.field.end-at"),
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        _("model.field.active"),
        default=True,
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
        return self.title


class BannerAccess(models.Model):
    class Meta:
        db_table = "banner_access"
        verbose_name = _("model.banner-access.name")
        verbose_name_plural = _("model.banner-access.name.plural")

        indexes = [
            models.Index(
                fields=["ip_address"],
                name="{0}_ip_address".format(db_table),
            ),
            models.Index(
                fields=["country_code"],
                name="{0}_country_code".format(db_table),
            ),
            models.Index(
                fields=["access_type"],
                name="{0}_access_type".format(db_table),
            ),
            models.Index(
                fields=["created_at"],
                name="{0}_created_at".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="accesses",
        verbose_name=_("model.field.banner"),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="banner_accesses",
        verbose_name=_("model.field.customer"),
        blank=True,
        null=True,
    )

    access_type = models.CharField(
        _("model.field.access-type"),
        max_length=25,
        choices=BannerAccessType.choices,
    )

    ip_address = models.GenericIPAddressField(
        _("model.field.ip"),
        protocol="both",
    )

    country_code = models.CharField(
        _("model.field.country-code"),
        max_length=2,
        help_text=_("model.field.country-code.help"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    def get_ip_address(self):
        return str(self.ip_address)

    def clean(self):
        super().clean()

        if self.country_code:
            self.country_code = self.country_code.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.banner.title} - {self.access_type} - {self.get_ip_address()} - {self.created_at}"
