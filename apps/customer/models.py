from django.conf import settings
from django.db import models, transaction
from django.dispatch import receiver
from django.utils import timezone
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
        on_delete=models.CASCADE,
        related_name="customer",
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
        size=[1024, 1024],
        crop=["middle", "center"],
        quality=100,
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
        default=settings.DEFAULT_TIME_ZONE,
        blank=False,
        null=False,
    )

    credits = models.IntegerField(
        _("model.field.credits"),
        blank=False,
        null=False,
        default=0,
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
        user_name = self.user.get_full_name()

        if user_name:
            return user_name

        if self.user.email:
            if "@" in self.user.email:
                return self.user.email.split("@")[0]

        return _("model.str.customer #{id}").format(id=self.id)

    def setup_initial_data(self):
        pass

    def has_active_subscription(self):
        with transaction.atomic():
            return (
                self.subscription_set.filter(
                    status=SubscriptionStatus.ACTIVE,
                    expire_at__isnull=False,
                    expire_at__gt=timezone.now(),
                )
                .select_for_update()
                .exists()
            )

    def has_credits(self, amount=0):
        with transaction.atomic():
            self.refresh_from_db(fields=["credits"])
            return self.credits is not None and self.credits >= amount


@receiver(models.signals.pre_save, sender=Customer)
def customer_pre_save_callback(sender, instance: Customer, *args, **kwargs):
    instance.setup_initial_data()


@receiver(models.signals.post_delete, sender=Customer)
def customer_post_delete_callback(sender, instance: Customer, **kwargs):
    if instance.user:
        instance.user.delete()
