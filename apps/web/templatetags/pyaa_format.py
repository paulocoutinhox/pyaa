import datetime
from decimal import Decimal

from babel.numbers import format_currency as babel_format_currency
from babel.numbers import format_decimal
from django import template
from django.conf import settings

register = template.Library()


@register.filter
@register.simple_tag
def format_currency(value, currency, remove_cents=True):
    # get the locale from settings
    locale = settings.LANGUAGE_CODE.replace("-", "_")

    # format the value with the given currency and locale
    value = float(value or 0)
    formatted_price = babel_format_currency(value, currency, locale=locale)

    # if remove_cents is true, remove ".00" or ",00" from the formatted string
    if remove_cents and (
        formatted_price.endswith(".00") or formatted_price.endswith(",00")
    ):
        formatted_price = formatted_price[:-3]

    return formatted_price


@register.filter
@register.simple_tag
def format_percentage(value, decimal_places=2):
    locale = settings.LANGUAGE_CODE.replace("-", "_")
    value = Decimal(value)
    formatted_value = format_decimal(
        value, format=f"#,##0.{decimal_places * '0'}", locale=locale
    )
    return f"{formatted_value}%"


@register.filter
def to_timestamp(value):
    if isinstance(value, datetime.datetime):
        return int(value.timestamp())

    return value


@register.filter
def raw_value(value):
    """
    Return the raw value from the database without any localization.
    """
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    return value


@register.filter
def widget_type(field):
    """
    Return the widget class name for a form field (lowercase).
    Usage: {% if field|widget_type == "textarea" %}
    """
    return field.field.widget.__class__.__name__.lower()
