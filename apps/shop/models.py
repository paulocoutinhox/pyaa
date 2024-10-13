import uuid
from datetime import timedelta

from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from apps.customer.models import Customer
from apps.shop import enums
from apps.shop.enums import ObjectType, PlanFrequencyType


class Plan(models.Model):
    class Meta:
        db_table = "shop_plan"
        verbose_name = _("model.shop-plan.name")
        verbose_name_plural = _("model.shop-plan.name.plural")

        indexes = [
            models.Index(fields=["name"], name="shop_plan_name"),
            models.Index(fields=["tag"], name="shop_plan_tag"),
            models.Index(fields=["gateway"], name="shop_plan_gateway"),
            models.Index(fields=["currency"], name="shop_plan_currency"),
            models.Index(fields=["frequency_type"], name="shop_plan_frequency_type"),
            models.Index(fields=["active"], name="shop_plan_active"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    name = models.CharField(
        _("model.field.name"),
        max_length=255,
        blank=False,
        null=False,
    )

    tag = models.SlugField(
        _("model.field.tag"),
        max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text=_("model.field.tag.help"),
    )

    gateway = models.CharField(
        _("model.field.payment-gateway"),
        max_length=255,
        choices=enums.PaymentGateway.choices,
        blank=False,
        null=False,
    )

    external_id = models.CharField(
        _("model.field.external_id"),
        max_length=255,
        blank=True,
        null=True,
    )

    currency = models.CharField(
        _("model.field.currency"),
        max_length=3,
        blank=False,
        null=False,
    )

    price = models.DecimalField(
        _("model.field.price"),
        max_digits=10,
        decimal_places=2,
    )

    credits = models.IntegerField(
        _("model.field.credits"),
        blank=True,
        null=True,
    )

    frequency_type = models.CharField(
        _("model.field.frequency-type"),
        max_length=255,
        choices=PlanFrequencyType.choices,
        blank=True,
        null=True,
    )

    frequency_amount = models.IntegerField(
        _("model.field.frequency-amount"),
        default=0,
        blank=True,
        null=True,
    )

    description = HTMLField(
        _("model.field.description"),
        blank=True,
        null=True,
    )

    sort_order = models.IntegerField(
        _("model.field.sort-order"),
        default=0,
    )

    featured = models.BooleanField(
        _("model.field.featured"),
        default=False,
        blank=False,
        null=False,
    )

    active = models.BooleanField(
        _("model.field.active"),
        default=True,
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

    def clean(self):
        super().clean()

        if self.currency:
            self.currency = self.currency.upper()

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = slugify(self.name)

        self.currency = self.currency.upper()

        super(Plan, self).save(*args, **kwargs)

    def get_frequency_in_days(self):
        if self.frequency_type is None or not self.frequency_type:
            return 0
        if self.frequency_amount is None or self.frequency_amount <= 0:
            return 0

        frequency_mapping = {
            PlanFrequencyType.DAY: 1,
            PlanFrequencyType.WEEK: 7,
            PlanFrequencyType.MONTH: 30,
            PlanFrequencyType.YEAR: 365,
            PlanFrequencyType.QUARTER: 90,
            PlanFrequencyType.SEMI_ANNUAL: 182,
        }

        return frequency_mapping.get(self.frequency_type, 0) * self.frequency_amount

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Meta:
        db_table = "shop_subscription"
        verbose_name = _("model.shop-subscription.name")
        verbose_name_plural = _("model.shop-subscription.name.plural")

        indexes = [
            models.Index(fields=["token"], name="shop_subscription_token"),
            models.Index(fields=["customer"], name="shop_subscription_customer"),
            models.Index(fields=["plan"], name="shop_subscription_plan"),
            models.Index(fields=["external_id"], name="shop_subscription_external_id"),
            models.Index(fields=["expire_at"], name="shop_subscription_expire_at"),
            models.Index(fields=["status"], name="shop_subscription_status"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    token = models.UUIDField(
        _("model.field.token"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
    )

    external_id = models.CharField(
        _("model.field.external_id"),
        max_length=255,
        blank=True,
        null=True,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        choices=enums.SubscriptionStatus.choices,
        default=enums.SubscriptionStatus.INITIAL,
        blank=False,
        null=False,
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

    @transaction.atomic
    def process_completed(self):
        # update the subscription status to active
        self.status = enums.SubscriptionStatus.ACTIVE

        # calculate the expiration based on the current expire_at or the current time
        days_to_add = self.plan.get_frequency_in_days()

        if self.expire_at:
            self.expire_at = F("expire_at") + timedelta(days=days_to_add)
        else:
            self.expire_at = timezone.now() + timedelta(days=days_to_add)

        self.save(update_fields=["status", "expire_at"])

        # add credits to the customer using CustomerHelper
        from apps.customer.helpers import CustomerHelper

        CustomerHelper.add_credits(
            customer=self.customer,
            amount=self.plan.credits,
            is_refund=False,
            add_log=True,
            object_id=self.id,
            object_type=ObjectType.SUBSCRIPTION,
        )

    @transaction.atomic
    def process_refunded(self):
        # update the subscription status to canceled
        self.status = enums.SubscriptionStatus.CANCELED

        # calculate the expiration based on the current expire_at or the current time
        days_to_add = self.plan.get_frequency_in_days()

        if self.expire_at:
            self.expire_at = F("expire_at") - timedelta(days=days_to_add)
        else:
            self.expire_at = timezone.now() - timedelta(days=days_to_add)

        self.save(update_fields=["status", "expire_at"])

        # remove credits from the customer using CustomerHelper
        from apps.customer.helpers import CustomerHelper

        CustomerHelper.add_credits(
            customer=self.customer,
            amount=-self.plan.credits,
            is_refund=False,
            add_log=True,
            object_id=self.id,
            object_type=ObjectType.SUBSCRIPTION,
        )

    @transaction.atomic
    def process_canceled(self):
        # update the status
        self.status = enums.SubscriptionStatus.CANCELED
        self.save()

    @transaction.atomic
    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def can_be_canceled(self):
        if self.status == enums.SubscriptionStatus.ACTIVE:
            return True

        return False

    def is_expired(self):
        if not self.expire_at:
            return False
        return timezone.now() > self.expire_at

    def __str__(self):
        return str(self.token)


class CreditLog(models.Model):
    class Meta:
        db_table = "shop_credit_log"
        verbose_name = _("model.shop-credit-log.name")
        verbose_name_plural = _("model.shop-credit-log.name.plural")

        indexes = [
            models.Index(
                fields=["object_id", "object_type"], name="shop_credit_log_object"
            ),
            models.Index(fields=["object_type"], name="shop_credit_log_object_type"),
            models.Index(fields=["customer"], name="shop_credit_log_customer"),
            models.Index(fields=["created_at"], name="shop_credit_log_created_at"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
        null=False,
    )

    amount = models.IntegerField(
        _("model.field.amount"),
        default=0,
    )

    object_type = models.CharField(
        _("model.field.object-type"),
        max_length=255,
        choices=enums.ObjectType.choices,
        default=enums.ObjectType.UNKNOWN,
        blank=True,
        null=True,
    )

    object_id = models.BigIntegerField(
        _("model.field.object-id"),
        blank=True,
        null=True,
        default=0,
    )

    is_refund = models.BooleanField(
        _("model.field.is-refund"),
        default=False,
    )

    description = models.TextField(
        _("model.field.description"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    def get_description(self):
        if self.object_type == enums.ObjectType.SUBSCRIPTION:
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription and subscription.plan:
                return subscription.plan.name

        if self.description:
            return self.description

        key = f"enum.shop-object-type.{self.object_type}"
        return _(key)


class EventLog(models.Model):
    class Meta:
        db_table = "shop_event_log"
        verbose_name = _("model.shop-event-log.name")
        verbose_name_plural = _("model.shop-event-log.name.plural")

        indexes = [
            models.Index(
                fields=["object_id", "object_type"], name="shop_event_log_object"
            ),
            models.Index(fields=["object_type"], name="shop_event_log_object_type"),
            models.Index(fields=["customer"], name="shop_event_log_customer"),
            models.Index(fields=["status"], name="shop_event_log_status"),
            models.Index(fields=["created_at"], name="shop_event_log_created_at"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    object_id = models.BigIntegerField(
        _("model.field.object-id"),
        blank=True,
        null=True,
        default=0,
    )

    object_type = models.CharField(
        _("model.field.object-type"),
        max_length=255,
        choices=enums.ObjectType.choices,
        default=enums.ObjectType.UNKNOWN,
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
        null=True,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        blank=True,
        null=True,
    )

    currency = models.CharField(
        _("model.field.currency"),
        max_length=3,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        _("model.field.amount"), max_digits=10, decimal_places=2, default=0
    )

    description = models.TextField(
        _("model.field.description"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if self.currency:
            self.currency = self.currency.upper()

        super(EventLog, self).save(*args, **kwargs)
