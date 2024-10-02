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


class ObjectType(TextChoices):
    GENERAL = "general", _("enum.shop-object-type.general")
    UNKNOWN = "unknown", _("enum.shop-object-type.unknown")
    BONUS = "bonus", _("enum.shop-object-type.bonus")
    SUBSCRIPTION = "subscription", _("enum.shop-object-type.subscription")
