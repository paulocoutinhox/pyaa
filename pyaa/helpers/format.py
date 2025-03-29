import datetime
from decimal import Decimal

from babel.numbers import format_currency as babel_format_currency
from babel.numbers import format_decimal
from django.conf import settings


class FormatHelper:
    @staticmethod
    def format_currency(value, currency, remove_cents=True):
        """
        Format a value as a currency string.
        """
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

    @staticmethod
    def format_percentage(value, decimal_places=2):
        locale = settings.LANGUAGE_CODE.replace("-", "_")
        value = Decimal(value)
        formatted_value = format_decimal(
            value, format=f"#,##0.{decimal_places * '0'}", locale=locale
        )
        return f"{formatted_value}%"

    @staticmethod
    def to_timestamp(value):
        if isinstance(value, datetime.datetime):
            return int(value.timestamp())

        return value

    @staticmethod
    def raw_value(value):
        """
        Return the raw value from the database without any localization.
        """
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        return value
