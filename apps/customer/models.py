import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField
from tinymce.models import HTMLField

from apps.customer import enums, fields
from apps.language import models as language_models
from apps.shop.enums import SubscriptionStatus


class Customer(models.Model):
    class Meta:
        db_table = "customer"
        verbose_name = _("model.customer.name")
        verbose_name_plural = _("model.customer.name.plural")

        indexes = [
            models.Index(
                fields=["nickname"],
                name="{0}_nickname".format(db_table),
            ),
            models.Index(
                fields=["gender"],
                name="{0}_gender".format(db_table),
            ),
            models.Index(
                fields=["activate_token"],
                name="{0}_activate_token".format(db_table),
            ),
            models.Index(
                fields=["recovery_token"],
                name="{0}_recovery_token".format(db_table),
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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="customer",
        verbose_name=_("model.field.user"),
        null=True,
        blank=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="customers",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    language = models.ForeignKey(
        language_models.Language,
        on_delete=models.RESTRICT,
        blank=False,
        null=False,
        default=0,
        verbose_name=_("model.field.language"),
    )

    nickname = models.CharField(
        _("model.field.nickname"),
        max_length=255,
        null=True,
        blank=True,
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
        size=[1024, 1024],
        crop=["middle", "center"],
        quality=100,
        upload_to="images/customer/avatar/%Y/%m/%d",
        blank=True,
        null=True,
    )

    timezone = TimeZoneField(
        _("model.field.timezone"),
        max_length=255,
        default=settings.DEFAULT_TIME_ZONE,
        blank=False,
        null=False,
    )

    activate_token = models.UUIDField(
        _("model.field.activate-token"),
        default=None,
        editable=False,
        unique=True,
        blank=True,
        null=True,
    )

    recovery_token = models.UUIDField(
        _("model.field.recovery-token"),
        default=None,
        editable=False,
        unique=True,
        blank=True,
        null=True,
    )

    credits = models.IntegerField(
        _("model.field.credits"),
        blank=False,
        null=False,
        default=0,
    )

    obs = HTMLField(
        _("model.field.obs"),
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
        if self.nickname:
            return self.nickname

        if self.user:
            user_name = self.user.get_full_name()
            if user_name:
                return user_name

            if self.user.email:
                if "@" in self.user.email:
                    return self.user.email.split("@")[0]

        return _("model.str.customer #{id}").format(id=self.id)

    def validate_unique_nickname(self, site_id):
        from apps.customer.helpers import CustomerHelper

        CustomerHelper.validate_unique_nickname(
            nickname=self.nickname,
            site_id=site_id,
            exclude_pk=self.pk,
        )

    def clean(self):
        super().clean()

        if self.pk is None:
            site_id = self.site_id or settings.SITE_ID

            if not site_id:
                raise ValidationError({"site_id": _("error.site-id-required")})
        else:
            site_id = self.site.id

    def setup_initial_data(self):
        if not self.pk:
            self.site = Site.objects.filter(id=settings.SITE_ID).first()

            # set the activation token only if account activation is required
            if settings.CUSTOMER_ACTIVATION_REQUIRED:
                self.activate_token = uuid.uuid4()
            else:
                self.activate_token = None

    def save(self, *args, **kwargs):
        self.setup_initial_data()
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = self.user

        result = super().delete(*args, **kwargs)

        if user:
            user.delete()

        return result

    def has_active_subscription(self):
        return self.subscription_set.filter(
            status=SubscriptionStatus.ACTIVE,
            expire_at__isnull=False,
            expire_at__gt=Now(),
        ).exists()

    def has_credits(self, amount=0):
        with transaction.atomic():
            self.refresh_from_db(fields=["credits"])
            return self.credits is not None and self.credits >= amount

    def has_purchased_product(self, product_id):
        """
        Check if the customer has purchased a specific product
        """
        from apps.shop.enums import ProductPurchaseStatus
        from apps.shop.models import ProductPurchase

        return ProductPurchase.objects.filter(
            customer=self, product_id=product_id, status=ProductPurchaseStatus.APPROVED
        ).exists()

    def get_address_by_type(self, address_type):
        """
        Get a customer's address by type

        :param address_type: the type of address to get
        :return: the first address found with the specified type, or None if not found
        """
        return self.addresses.filter(address_type=address_type).first()


class CustomerAddress(models.Model):
    class Meta:
        db_table = "customer_address"
        verbose_name = _("model.customer-address.name")
        verbose_name_plural = _("model.customer-address.name.plural")

        indexes = [
            models.Index(
                fields=["address_type"],
                name="{0}_address_type".format(db_table),
            ),
            models.Index(
                fields=["city"],
                name="{0}_city".format(db_table),
            ),
            models.Index(
                fields=["state"],
                name="{0}_state".format(db_table),
            ),
            models.Index(
                fields=["postal_code"],
                name="{0}_postal_code".format(db_table),
            ),
            models.Index(
                fields=["country_code"],
                name="{0}_country_code".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("model.field.customer"),
    )

    address_type = models.CharField(
        _("model.field.address-type"),
        max_length=255,
        choices=enums.CustomerAddressType.choices,
        default=enums.CustomerAddressType.MAIN,
    )

    address_line1 = models.CharField(
        _("model.field.address-line1"),
        max_length=255,
    )

    address_line2 = models.CharField(
        _("model.field.address-line2"),
        max_length=255,
        null=True,
        blank=True,
    )

    street_number = models.CharField(
        _("model.field.street-number"),
        max_length=255,
        null=True,
        blank=True,
    )

    complement = models.CharField(
        _("model.field.complement"),
        max_length=255,
        null=True,
        blank=True,
    )

    city = models.CharField(
        _("model.field.city"),
        max_length=255,
    )

    state = models.CharField(
        _("model.field.state"),
        max_length=255,
    )

    postal_code = models.CharField(
        _("model.field.postal-code"),
        max_length=255,
    )

    country_code = models.CharField(
        _("model.field.country-code"),
        max_length=2,
        help_text=_("model.field.country-code.help"),
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
        return f"{self.address_line1}, {self.street_number} - {self.city}/{self.state}"

    def clean(self):
        super().clean()
        if self.country_code:
            self.country_code = self.country_code.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
