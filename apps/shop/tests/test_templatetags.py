from django.test import TestCase

from apps.shop.enums import PlanFrequencyType, SubscriptionStatus
from apps.shop.templatetags.shop import (
    format_frequency_type,
    format_subscription_status,
)


class ShopTemplateTagsTest(TestCase):

    def test_format_frequency_type_valid(self):
        result = format_frequency_type(PlanFrequencyType.MONTH)
        self.assertEqual(result, PlanFrequencyType.MONTH.label)

    def test_format_frequency_type_invalid(self):
        result = format_frequency_type("INVALID_TYPE")
        self.assertEqual(result, "INVALID_TYPE")

    def test_format_subscription_status_valid(self):
        result = format_subscription_status(SubscriptionStatus.ACTIVE)
        self.assertEqual(result, SubscriptionStatus.ACTIVE.label)

    def test_format_subscription_status_invalid(self):
        result = format_subscription_status("INVALID_STATUS")
        self.assertEqual(result, "INVALID_STATUS")
