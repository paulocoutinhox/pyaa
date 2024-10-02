from decimal import Decimal

from babel import numbers
from django import template

register = template.Library()


@register.filter
def format_currency(value, currency, remove_cents=True):
    try:
        # check if the value is a decimal or float and has no fractional part, convert it to an integer
        if isinstance(value, Decimal) or isinstance(value, float):
            if value % 1 == 0:
                value = int(value)

        # format the value with the given currency
        formatted_price = numbers.format_currency(value, currency)

        # if remove_cents is True, remove ".00" or ",00" at the end of the formatted string
        if remove_cents and (
            formatted_price.endswith(".00") or formatted_price.endswith(",00")
        ):
            formatted_price = formatted_price[:-3]

        return formatted_price
    except Exception:
        # in case of any errors, return the value with the currency as a fallback
        return f"{value} {currency}"
