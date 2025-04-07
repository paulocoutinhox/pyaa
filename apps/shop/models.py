from datetime import timedelta

from django.contrib.sites.models import Site
from django.db import models, transaction
from django.db.models import F
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from apps.customer.models import Customer
from apps.shop import enums, fields
from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PlanFrequencyType,
    SubscriptionStatus,
)
from apps.site.models import Site
from pyaa.helpers.string import StringHelper


class Product(models.Model):
    class Meta:
        db_table = "shop_product"
        verbose_name = _("model.shop-product.name")
        verbose_name_plural = _("model.shop-product.name.plural")

        indexes = [
            models.Index(fields=["name"], name="shop_product_name"),
            models.Index(fields=["currency"], name="shop_product_currency"),
            models.Index(fields=["active"], name="shop_product_active"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("model.field.site"),
        blank=True,
        null=True,
    )

    name = models.CharField(
        _("model.field.name"),
        max_length=255,
        blank=False,
        null=False,
    )

    description = HTMLField(
        _("model.field.description"),
        blank=True,
        null=True,
    )

    image = fields.ProductImageField(
        _("model.field.image"),
        size=[1024, 1024],
        crop=["middle", "center"],
        quality=100,
        upload_to="images/product/%Y/%m/%d",
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

    def get_active_files(self):
        """
        Return all active files for this product
        """
        return self.files.filter(active=True).order_by("sort_order")

    def get_image_url(self):
        if not self.image:
            return static("images/product-no-image.png")

        image_url = str(self.image)

        if image_url.startswith(("http://", "https://")):
            return image_url

        return self.image.url

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.currency:
            self.currency = self.currency.upper()

        super(Product, self).save(*args, **kwargs)


class ProductFile(models.Model):
    class Meta:
        db_table = "shop_product_file"
        verbose_name = _("model.shop-product-file.name")
        verbose_name_plural = _("model.shop-product-file.name.plural")

        indexes = [
            models.Index(fields=["product"], name="shop_product_file_product"),
            models.Index(fields=["file_type"], name="shop_product_file_file_type"),
            models.Index(fields=["active"], name="shop_product_file_active"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("model.field.product"),
    )

    name = models.CharField(
        _("model.field.name"),
        max_length=255,
        blank=False,
        null=False,
    )

    description = models.TextField(
        _("model.field.description"),
        blank=True,
        null=True,
    )

    file = models.FileField(
        _("model.field.file"),
        upload_to="files/product/%Y/%m/%d",
        max_length=255,
    )

    file_type = models.CharField(
        _("model.field.file-type"),
        max_length=50,
        blank=True,
        null=True,
    )

    file_size = models.PositiveIntegerField(
        _("model.field.file-size"),
        default=0,
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        _("model.field.active"),
        default=True,
        blank=False,
        null=False,
    )

    sort_order = models.IntegerField(
        _("model.field.sort-order"),
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
        return self.name

    def get_file_url(self):
        if not self.file:
            return None

        file_url = str(self.file)

        if file_url.startswith(("http://", "https://")):
            return file_url

        return self.file.url


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
            models.Index(fields=["plan_type"], name="shop_plan_plan_type"),
            models.Index(fields=["frequency_type"], name="shop_plan_frequency_type"),
            models.Index(fields=["active"], name="shop_plan_active"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="plans",
        verbose_name=_("model.field.site"),
        blank=True,
        null=True,
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

    plan_type = models.CharField(
        _("model.field.plan-type"),
        max_length=255,
        choices=enums.PlanType.choices,
        default=None,
        blank=False,
        null=False,
    )

    gateway = models.CharField(
        _("model.field.payment-gateway"),
        max_length=255,
        choices=enums.PaymentGateway.choices,
        blank=False,
        null=False,
    )

    external_id = models.CharField(
        _("model.field.external-id"),
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

    featured = models.BooleanField(
        _("model.field.featured"),
        default=False,
        blank=False,
        null=False,
    )

    bonus = models.IntegerField(
        _("model.field.bonus"),
        blank=True,
        null=True,
        help_text=_("model.hint.plan-bonus"),
    )

    image = fields.PlanImageField(
        _("model.field.image"),
        size=[1024, 1024],
        crop=["middle", "center"],
        quality=100,
        upload_to="images/plan/%Y/%m/%d",
        blank=True,
        null=True,
    )

    sort_order = models.IntegerField(
        _("model.field.sort-order"),
        default=0,
    )

    active = models.BooleanField(
        _("model.field.active"),
        default=True,
        blank=False,
        null=False,
    )

    description = HTMLField(
        _("model.field.description"),
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

    def get_image_url(self):
        if not self.image:
            return static("images/plan-no-image.png")

        image_url = str(self.image)

        if image_url.startswith(("http://", "https://")):
            return image_url

        return self.image.url

    def get_name(self):
        if self.bonus and self.bonus > 0:
            return _("plan.bonus.description: %(name)s %(bonus)s") % {
                "name": self.name,
                "bonus": self.bonus,
            }

        return self.name

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

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        _("model.field.token"),
        max_length=255,
        default=StringHelper.generate_subscription_token,
        editable=False,
        unique=True,
    )

    external_id = models.CharField(
        _("model.field.external-id"),
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
            plan=self.plan,
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
            plan=self.plan,
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


class CreditPurchase(models.Model):
    class Meta:
        db_table = "credit_purchase"
        verbose_name = _("model.credit-puchase.name")
        verbose_name_plural = _("model.credit-purchase.name.plural")

        indexes = [
            models.Index(
                fields=["token"],
                name="shop_credit_purchase_token",
            ),
            models.Index(
                fields=["status"],
                name="shop_credit_purchase_status",
            ),
            models.Index(
                fields=["invoice_generated"],
                name="shop_credit_purchase_inv_gen",
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
        related_name="credit_purchases",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        verbose_name=_("model.field.plan"),
    )

    token = models.CharField(
        _("model.field.token"),
        max_length=255,
        default=StringHelper.generate_credit_purchase_token,
        editable=False,
        unique=True,
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

    invoice_generated = models.BooleanField(
        _("model.field.invoice-generated"),
        default=False,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        choices=enums.CreditPurchaseStatus.choices,
        default=enums.CreditPurchaseStatus.INITIAL,
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
        # update the status to approved
        self.status = enums.CreditPurchaseStatus.APPROVED
        self.save(update_fields=["status"])

        # add credits to customer
        from apps.customer.helpers import CustomerHelper

        CustomerHelper.add_credits(
            customer=self.customer,
            plan=self.plan,
            object_id=self.id,
            object_type=ObjectType.CREDIT_PURCHASE,
        )

        # send confirmation email
        CustomerHelper.send_credit_purchase_paid_email(self)

    @transaction.atomic
    def process_canceled(self):
        # update the status to canceled
        self.status = enums.CreditPurchaseStatus.CANCELED
        self.save(update_fields=["status"])

    @transaction.atomic
    def process_refunded(self):
        # update the status to refunded
        self.status = enums.CreditPurchaseStatus.REFUNDED
        self.save(update_fields=["status"])


class ProductPurchase(models.Model):
    class Meta:
        db_table = "product_purchase"
        verbose_name = _("model.product-purchase.name")
        verbose_name_plural = _("model.product-purchase.name.plural")

        indexes = [
            models.Index(
                fields=["token"],
                name="shop_product_purchase_token",
            ),
            models.Index(
                fields=["status"],
                name="shop_product_purchase_status",
            ),
            models.Index(
                fields=["invoice_generated"],
                name="shop_product_purchase_inv_gen",
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
        related_name="product_purchases",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("model.field.product"),
    )

    token = models.CharField(
        _("model.field.token"),
        max_length=255,
        default=StringHelper.generate_product_purchase_token,
        editable=False,
        unique=True,
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

    invoice_generated = models.BooleanField(
        _("model.field.invoice-generated"),
        default=False,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        choices=enums.ProductPurchaseStatus.choices,
        default=enums.ProductPurchaseStatus.INITIAL,
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
        # update the status to approved
        self.status = enums.ProductPurchaseStatus.APPROVED
        self.save(update_fields=["status"])

        # send confirmation email
        from apps.customer.helpers import CustomerHelper

        CustomerHelper.send_product_purchase_paid_email(self)

    @transaction.atomic
    def process_canceled(self):
        # update the status to canceled
        self.status = enums.ProductPurchaseStatus.CANCELED
        self.save(update_fields=["status"])

    @transaction.atomic
    def process_refunded(self):
        # update the status to refunded
        self.status = enums.ProductPurchaseStatus.REFUNDED
        self.save(update_fields=["status"])


class CreditLog(models.Model):
    class Meta:
        db_table = "shop_credit_log"
        verbose_name = _("model.shop-credit-log.name")
        verbose_name_plural = _("model.shop-credit-log.name.plural")

        indexes = [
            models.Index(
                fields=["object_id", "object_type"],
                name="shop_credit_log_object",
            ),
            models.Index(fields=["object_type"], name="shop_credit_log_object_type"),
            models.Index(fields=["is_refund"], name="shop_credit_log_is_refund"),
            models.Index(fields=["created_at"], name="shop_credit_log_created_at"),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="credit_logs",
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

    amount = models.IntegerField(
        _("model.field.amount"),
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
        result = ""

        if self.description:
            # if there is a specific description
            result = self.description
        elif self.object_type == enums.ObjectType.SUBSCRIPTION:
            # if the object type is subscription
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription and subscription.plan:
                result = subscription.plan.name
            else:
                key = f"enum.shop-object-type.{self.object_type}"
                result = _(key)
        elif self.object_type == enums.ObjectType.CREDIT_PURCHASE:
            # if the object type is credit purchase
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase and purchase.plan:
                result = purchase.plan.get_name()
            else:
                key = f"enum.shop-object-type.{self.object_type}"
                result = _(key)
        elif self.object_type == enums.ObjectType.BONUS:
            result = _("enum.shop-object-type.bonus")
        elif self.object_type == enums.ObjectType.VOUCHER:
            if self.object_id:
                plan = Plan.objects.filter(id=self.object_id).first()

                if plan:
                    result = plan.get_name()
                else:
                    result = _("enum.shop-object-type.voucher")
            else:
                result = _("enum.shop-object-type.voucher")
        elif self.object_type:
            # default case for other object types
            key = f"enum.shop-object-type.{self.object_type}"
            result = _(key)
        else:
            result = ""

        # if it is a refund, add the refund string
        if self.is_refund:
            result = result + " " + _("message.refund-in-list")
            result = result.strip()

        return result

    def get_image_url(self):
        from apps.shop.models import CreditPurchase, Subscription

        if self.object_type == enums.ObjectType.SUBSCRIPTION:
            # subscription
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription and subscription.plan:
                return subscription.plan.get_image_url()
        elif self.object_type == enums.ObjectType.CREDIT_PURCHASE:
            # credit purchase
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase and purchase.plan:
                return purchase.plan.get_image_url()
        elif self.object_type == enums.ObjectType.BONUS:
            # bonus
            return static("images/credit-bonus.png")

        # default case for other object types
        return static("images/no-image.png")

    def get_status(self):
        from apps.shop.models import CreditPurchase, Subscription

        if self.object_type == ObjectType.SUBSCRIPTION:
            # subscription
            subscription = Subscription.objects.filter(id=self.object_id).first()

            if subscription:
                return SubscriptionStatus(subscription.status).label
        elif self.object_type == ObjectType.CREDIT_PURCHASE:
            # credit purchase
            purchase = CreditPurchase.objects.filter(id=self.object_id).first()

            if purchase:
                return CreditPurchaseStatus(purchase.status).label

        return None


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

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="event_logs",
        verbose_name=_("model.field.site"),
        blank=False,
        null=False,
    )

    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        verbose_name=_("model.field.customer"),
        null=True,
    )

    object_type = models.CharField(
        _("model.field.object-type"),
        max_length=255,
        choices=enums.ObjectType.choices,
        default=enums.ObjectType.UNKNOWN,
        blank=False,
        null=False,
    )

    object_id = models.BigIntegerField(
        _("model.field.object-id"),
        blank=True,
        null=True,
        default=0,
    )

    currency = models.CharField(
        _("model.field.currency"),
        max_length=3,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        _("model.field.amount"),
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        _("model.field.status"),
        max_length=255,
        blank=True,
        null=True,
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
