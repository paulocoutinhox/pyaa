from django import template

from apps.shop.enums import SubscriptionStatus
from apps.shop.models import PlanFrequencyType

register = template.Library()


@register.filter
def format_frequency_type(value):
    try:
        return PlanFrequencyType(value).label
    except ValueError:
        return value


@register.filter
def format_subscription_status(value):
    try:
        return SubscriptionStatus(value).label
    except ValueError:
        return value
