from django.test import TestCase

from apps.shop.enums import (
    ObjectType,
    PaymentGateway,
    PlanFrequencyType,
    SubscriptionStatus,
)


class ShopEnumsTest(TestCase):

    def test_payment_gateway_choices(self):
        choices = PaymentGateway.get_choices()
        expected_keys = ["STRIPE"]
        actual_keys = [choice[0] for choice in choices]
        self.assertCountEqual(actual_keys, expected_keys)

    def test_plan_frequency_type_choices(self):
        expected_keys = [
            "DAY",
            "WEEK",
            "MONTH",
            "YEAR",
            "QUARTER",
            "SEMI_ANNUAL",
        ]
        actual_keys = [freq.name for freq in PlanFrequencyType]
        self.assertCountEqual(actual_keys, expected_keys)

    def test_subscription_status_choices(self):
        expected_keys = [
            "INITIAL",
            "ANALYSIS",
            "ACTIVE",
            "SUSPENDED",
            "CANCELED",
            "FAILED",
            "CHARGED_BACK",
            "REJECTED",
            "REFUNDED",
        ]
        actual_keys = [status.name for status in SubscriptionStatus]
        self.assertCountEqual(actual_keys, expected_keys)

    def test_object_type_choices(self):
        expected_keys = [
            "GENERAL",
            "UNKNOWN",
            "SUBSCRIPTION",
            "BONUS",
            "CREDIT_PURCHASE",
            "PRODUCT_PURCHASE",
            "VOUCHER",
        ]
        actual_keys = [obj_type.name for obj_type in ObjectType]
        self.assertCountEqual(actual_keys, expected_keys)
