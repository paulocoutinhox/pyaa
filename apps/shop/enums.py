from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class PaymentGateway(TextChoices):
    STRIPE = "stripe", _("enum.shop-payment-gateway.stripe")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PaymentGatewayAction(TextChoices):
    REDIRECT = "redirect"


class PaymentGatewayCancelAction(TextChoices):
    REDIRECT = "redirect"


class PlanFrequencyType(TextChoices):
    DAY = "day", _("enum.shop-plan-frequency-type.day")
    WEEK = "week", _("enum.shop-plan-frequency-type.week")
    MONTH = "month", _("enum.shop-plan-frequency-type.month")
    YEAR = "year", _("enum.shop-plan-frequency-type.year")
    QUARTER = "quarter", _("enum.shop-plan-frequency-type.quarter")
    SEMI_ANNUAL = "semi_annual", _("enum.shop-plan-frequency-type.semi_annual")


class SubscriptionStatus(TextChoices):
    INITIAL = "initial", _("enum.shop-subscription-status.initial")
    ANALYSIS = "analysis", _("enum.shop-subscription-status.analysis")
    ACTIVE = "active", _("enum.shop-subscription-status.active")
    SUSPENDED = "suspended", _("enum.shop-subscription-status.suspended")
    CANCELED = "canceled", _("enum.shop-subscription-status.canceled")
    FAILED = "failed", _("enum.shop-subscription-status.failed")
    CHARGED_BACK = "charged-back", _("enum.shop-subscription-status.charged-back")
    REJECTED = "rejected", _("enum.shop-subscription-status.rejected")
    REFUNDED = "refunded", _("enum.shop-subscription-status.refunded")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ObjectType(TextChoices):
    GENERAL = "general", _("enum.shop-object-type.general")
    UNKNOWN = "unknown", _("enum.shop-object-type.unknown")
    BONUS = "bonus", _("enum.shop-object-type.bonus")
    CREDIT_PURCHASE = "credit-purchase", _("enum.shop-object-type.credit-purchase")
    PRODUCT_PURCHASE = "product-purchase", _("enum.shop-object-type.product-purchase")
    SUBSCRIPTION = "subscription", _("enum.shop-object-type.subscription")
    VOUCHER = "voucher", _("enum.shop-object-type.voucher")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PlanType(TextChoices):
    CREDIT_PURCHASE = "credit-purchase", _("enum.shop-plan-type.credit-purchase")
    SUBSCRIPTION = "subscription", _("enum.shop-plan-type.subscription")
    VOUCHER = "voucher", _("enum.shop-plan-type.voucher")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class CreditPurchaseStatus(TextChoices):
    INITIAL = "initial", _("enum.shop-credit-purchase-status.initial")
    ANALYSIS = "analysis", _("enum.shop-credit-purchase-status.analysis")
    APPROVED = "approved", _("enum.shop-credit-purchase-status.approved")
    CANCELED = "canceled", _("enum.shop-credit-purchase-status.canceled")
    FAILED = "failed", _("enum.shop-credit-purchase-status.failed")
    CHARGED_BACK = "charged-back", _("enum.shop-credit-purchase-status.charged-back")
    REJECTED = "rejected", _("enum.shop-credit-purchase-status.rejected")
    REFUNDED = "refunded", _("enum.shop-credit-purchase-status.refunded")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ProductPurchaseStatus(TextChoices):
    INITIAL = "initial", _("enum.shop-product-purchase-status.initial")
    ANALYSIS = "analysis", _("enum.shop-product-purchase-status.analysis")
    APPROVED = "approved", _("enum.shop-product-purchase-status.approved")
    CANCELED = "canceled", _("enum.shop-product-purchase-status.canceled")
    FAILED = "failed", _("enum.shop-product-purchase-status.failed")
    CHARGED_BACK = "charged-back", _("enum.shop-product-purchase-status.charged-back")
    REJECTED = "rejected", _("enum.shop-product-purchase-status.rejected")
    REFUNDED = "refunded", _("enum.shop-product-purchase-status.refunded")

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class CheckoutStep(TextChoices):
    CHECKOUT = "checkout"
    PAYMENT = "payment"

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)
