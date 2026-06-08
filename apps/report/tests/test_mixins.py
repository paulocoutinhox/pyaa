import datetime

from django.test import TestCase
from django.utils import timezone

from apps.report.mixins import DateParserMixin


class DateParserMixinTest(TestCase):
    def setUp(self):
        self.mixin = DateParserMixin()

    def test_parse_date_with_valid_format(self):
        result = self.mixin.parse_date("12/31/2025")

        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 31)
        self.assertTrue(timezone.is_aware(result))

    def test_parse_date_with_iso_datetime(self):
        result = self.mixin.parse_date("2025-12-31T10:30:00")

        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.hour, 10)

    def test_parse_date_with_empty_value(self):
        self.assertIsNone(self.mixin.parse_date(""))

    def test_parse_date_with_none(self):
        self.assertIsNone(self.mixin.parse_date(None))

    def test_parse_date_with_invalid_value(self):
        self.assertIsNone(self.mixin.parse_date("not-a-date"))

    def test_get_month_range_for_given_date(self):
        date = timezone.make_aware(datetime.datetime(2025, 2, 15, 12, 0, 0))
        start, end = self.mixin.get_month_range(date)

        self.assertEqual(start.day, 1)
        self.assertEqual(start.hour, 0)
        self.assertEqual(start.minute, 0)

        # february 2025 has 28 days
        self.assertEqual(end.day, 28)
        self.assertEqual(end.hour, 23)
        self.assertEqual(end.minute, 59)

    def test_get_month_range_for_leap_year(self):
        date = timezone.make_aware(datetime.datetime(2024, 2, 10))
        start, end = self.mixin.get_month_range(date)

        self.assertEqual(end.day, 29)

    def test_get_month_range_defaults_to_now(self):
        start, end = self.mixin.get_month_range()

        now = timezone.now()
        self.assertEqual(start.month, now.month)
        self.assertEqual(end.month, now.month)
        self.assertEqual(start.day, 1)
