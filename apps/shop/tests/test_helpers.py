from unittest.mock import patch

from django.test import TestCase

from apps.shop.enums import PaymentGateway
from apps.shop.helpers import process_cancel, process_checkout, process_webhook
from apps.shop.models import Plan, Subscription


class HelpersTest(TestCase):
    def setUp(self):
        self.request = None

        self.plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type="monthly",
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        self.subscription = Subscription(plan=self.plan)

    @patch("apps.shop.gateways.stripe.process_checkout")
    def test_process_checkout_stripe(self, mock_process_checkout):
        mock_process_checkout.return_value = {
            "action": "redirect",
            "url": "http://example.com",
        }

        result = process_checkout(self.request, self.subscription)

        self.assertEqual(result, {"action": "redirect", "url": "http://example.com"})
        mock_process_checkout.assert_called_once_with(self.request, self.subscription)

    @patch("apps.shop.gateways.stripe.process_webhook")
    def test_process_webhook_stripe(self, mock_process_webhook):
        result = process_webhook(self.request, PaymentGateway.STRIPE)

        mock_process_webhook.assert_called_once_with(self.request)
        self.assertIsNotNone(result)

    @patch("apps.shop.gateways.stripe.process_cancel")
    def test_process_cancel_stripe(self, mock_process_cancel):
        mock_process_cancel.return_value = True

        result = process_cancel(self.request, self.subscription)

        self.assertTrue(result)
        mock_process_cancel.assert_called_once_with(self.request, self.subscription)

    def test_process_checkout_invalid_gateway(self):
        self.subscription.plan.gateway = "INVALID_GATEWAY"
        result = process_checkout(self.request, self.subscription)
        self.assertIsNone(result)

    def test_process_webhook_invalid_gateway(self):
        result = process_webhook(self.request, "INVALID_GATEWAY")
        self.assertIsNone(result)

    def test_process_cancel_invalid_gateway(self):
        self.subscription.plan.gateway = "INVALID_GATEWAY"
        result = process_cancel(self.request, self.subscription)
        self.assertIsNone(result)
