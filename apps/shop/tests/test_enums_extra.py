from django.test import TestCase

from apps.shop.enums import SubscriptionStatus


class ShopEnumsExtraTest(TestCase):
    def test_subscription_status_get_choices(self):
        choices = SubscriptionStatus.get_choices()

        self.assertIsInstance(choices, tuple)
        self.assertGreater(len(choices), 0)

        actual_keys = [choice[0] for choice in choices]
        self.assertIn("ACTIVE", actual_keys)
