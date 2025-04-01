import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Sum
from django.db.models.functions import Now
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils import timezone
from django.utils.timezone import make_aware, now
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField
from tinymce.models import HTMLField

from apps.customer import enums, fields
from apps.language import models as language_models
from apps.shop.enums import (
    CreditPurchaseStatus,
    CreditType,
    ObjectType,
    SubscriptionStatus,
)
from apps.site.models import Site


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
        on_delete=models.CASCADE,
        related_name="customer",
        verbose_name=_("model.field.user"),
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

    activate_token = models.UUIDField(
        _("model.field.activate-token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    recovery_token = models.UUIDField(
        _("model.field.recovery-token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
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

    def has_active_subscription(self):
        from apps.shop.enums import SubscriptionStatus

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

    def get_remaining_credits(self):
        from apps.customer.models import CustomerCredit

        credits = CustomerCredit.objects.filter(
            customer=self, current_amount__gt=0, expire_at__gt=now()
        ).aggregate(total_credits=Sum("current_amount"))

        return credits["total_credits"] or 0

    def get_active_credit(self, only_paid=False):
        """
        Retrieves the active customer credit based on the provided conditions.

        :param only_paid: flag to determine if only paid credits should be considered.
        :return: the active customer credit instance or None if no valid credit is found.
        """
        from apps.customer.models import CustomerCredit

        # filter for valid credits
        credits_queryset = CustomerCredit.objects.annotate(current_time=Now()).filter(
            customer=self,
            current_amount__gt=0,
            expire_at__gt=F("current_time"),
        )

        # if only_paid is true, filter for paid credits
        if only_paid:
            credits_queryset = credits_queryset.filter(credit_type=CreditType.PAID)

        # order by expiration date
        credits_queryset = credits_queryset.order_by("expire_at")

        # return the first valid credit or None
        return credits_queryset.first()


class CustomerCredit(models.Model):
    class Meta:
        db_table = "customer_credit"
        verbose_name = _("model.customer-credit.name")
        verbose_name_plural = _("model.customer-credit.name.plural")

        indexes = [
            models.Index(
                fields=["object_id", "object_type"],
                name="customer_credit_object",
            ),
            models.Index(
                fields=["object_type"],
                name="customer_credit_object_type",
            ),
            models.Index(
                fields=["credit_type"],
                name="customer_credit_credit_type",
            ),
            models.Index(
                fields=["expire_at"],
                name="customer_credit_expire_at",
            ),
            models.Index(
                fields=["created_at"],
                name="customer_credit_created_at",
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="customer_credits",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
        null=False,
    )

    plan_id = models.BigIntegerField(
        _("model.field.plan"),
        blank=True,
        null=True,
        default=0,
    )

    object_type = models.CharField(
        _("model.field.object-type"),
        max_length=255,
        choices=ObjectType.choices,
        default=ObjectType.UNKNOWN,
        blank=True,
        null=True,
    )

    object_id = models.BigIntegerField(
        _("model.field.object-id"),
        blank=True,
        null=True,
        default=0,
    )

    credit_type = models.CharField(
        _("model.field.credit-type"),
        max_length=255,
        choices=CreditType.choices,
        default=CreditType.PAID,
        blank=True,
        null=True,
    )

    initial_amount = models.IntegerField(
        _("model.field.initial-amount"),
        default=0,
    )

    current_amount = models.IntegerField(
        _("model.field.current-amount"),
        default=0,
    )

    price = models.DecimalField(
        _("model.field.price"),
        max_digits=10,
        decimal_places=2,
    )

    expire_at = models.DateTimeField(
        _("model.field.expire-at"),
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

    def get_description(self):
        from apps.shop.models import CreditPurchase, Subscription

        # bonus
        if self.credit_type == CreditType.BONUS:
            return _("credit-type.bonus.description")

        if self.object_type == ObjectType.SUBSCRIPTION:
            # if the object type is subscription
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription and subscription.plan:
                return subscription.plan.get_name()
            else:
                key = f"enum.shop-object-type.{self.object_type}"
                return _(key)
        elif self.object_type == ObjectType.CREDIT_PURCHASE:
            # if the object type is credit purchase
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase and purchase.plan:
                return purchase.plan.get_name()
        else:
            # default case for other object types
            key = f"enum.shop-object-type.{self.object_type}"
            return _(key)

        return None

    def get_image_url(self):
        from apps.shop.models import CreditPurchase, Subscription

        # bonus
        if self.credit_type == CreditType.BONUS:
            return static("images/credit-bonus.png")

        if self.object_type == ObjectType.SUBSCRIPTION:
            # subscription
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription and subscription.plan:
                return subscription.plan.get_image_url()
        elif self.object_type == ObjectType.CREDIT_PURCHASE:
            # purchase
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase and purchase.plan:
                return purchase.plan.get_image_url()

        return static("images/plan-default.png")

    def get_status(self):
        from apps.shop.models import CreditPurchase, Subscription

        if self.object_type == ObjectType.SUBSCRIPTION:
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription:
                return SubscriptionStatus(subscription.status).label

        elif self.object_type == ObjectType.CREDIT_PURCHASE:
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase:
                return CreditPurchaseStatus(purchase.status).label

        return None

    def get_validity_description(self):
        max_date = make_aware(datetime(9999, 12, 31, 23, 59, 59))

        if self.expire_at == max_date:
            return _("plan.validity.no-expiration")

        if self.expire_at:
            current_time = now()

            if self.expire_at < current_time:
                return _("plan.validity.expired: %(expire-at)s") % {
                    "expire-at": self.expire_at.strftime("%d/%m/%Y %H:%M:%S")
                }
            else:
                return _("plan.validity.not-expired: %(expire-at)s") % {
                    "expire-at": self.expire_at.strftime("%d/%m/%Y %H:%M:%S")
                }

        return None


@receiver(models.signals.pre_save, sender=Customer)
def customer_pre_save_callback(sender, instance: Customer, *args, **kwargs):
    instance.setup_initial_data()


@receiver(models.signals.post_delete, sender=Customer)
def customer_post_delete_callback(sender, instance: Customer, **kwargs):
    if instance.user:
        instance.user.delete()
