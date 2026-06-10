import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from pyaa.helpers.format import FormatHelper


class FormatHelperTest(TestCase):
    def test_format_currency_removes_cents_by_default(self):
        result = FormatHelper.format_currency(10, "USD")
        self.assertNotIn(".00", result)
        self.assertIn("10", result)

    def test_format_currency_keeps_cents_when_disabled(self):
        result = FormatHelper.format_currency(10, "USD", remove_cents=False)
        self.assertIn("10.00", result)

    def test_format_currency_with_fractional_value(self):
        result = FormatHelper.format_currency(Decimal("19.90"), "USD")
        self.assertIn("19.90", result)

    def test_format_currency_handles_none_as_zero(self):
        result = FormatHelper.format_currency(None, "USD")
        self.assertIn("0", result)

    def test_format_percentage_default_places(self):
        self.assertEqual(FormatHelper.format_percentage(Decimal("12.5")), "12.50%")

    def test_format_percentage_custom_places(self):
        self.assertEqual(
            FormatHelper.format_percentage(Decimal("12.5"), decimal_places=1), "12.5%"
        )

    def test_to_timestamp_with_datetime(self):
        moment = timezone.now()
        self.assertEqual(FormatHelper.to_timestamp(moment), int(moment.timestamp()))

    def test_to_timestamp_with_non_datetime(self):
        self.assertEqual(FormatHelper.to_timestamp("not-a-date"), "not-a-date")

    def test_raw_value_with_decimal(self):
        self.assertEqual(FormatHelper.raw_value(Decimal("19.90")), "19.90")

    def test_raw_value_with_integer(self):
        self.assertEqual(FormatHelper.raw_value(42), "42")

    def test_raw_value_with_string_is_unchanged(self):
        self.assertEqual(FormatHelper.raw_value("hello"), "hello")
