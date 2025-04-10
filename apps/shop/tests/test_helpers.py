from unittest.mock import patch

from django.test import TestCase

from apps.shop.enums import ObjectType, PaymentGateway
from apps.shop.helpers import ShopHelper
from apps.shop.models import CreditPurchase, Plan, ProductPurchase, Subscription


class ShopHelperTest(TestCase):
    def setUp(self):
        self.request = None

        self.plan = Plan(
            name="Test Plan",
            tag="test-plan",
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=9.99,
            credits=10,
            plan_type="credit-purchase",
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        self.subscription = Subscription(plan=self.plan)
        self.credit_purchase = CreditPurchase(plan=self.plan)
        self.product_purchase = ProductPurchase(product=None)

    @patch("apps.shop.gateways.stripe.process_checkout_for_subscription")
    def test_process_checkout_for_subscription_stripe(self, mock_process_checkout):
        mock_process_checkout.return_value = {
            "action": "redirect",
            "url": "http://example.com",
        }

        result = ShopHelper.process_checkout_for_subscription(
            self.request, self.subscription
        )

        self.assertEqual(result, {"action": "redirect", "url": "http://example.com"})
        mock_process_checkout.assert_called_once_with(self.request, self.subscription)

    @patch("apps.shop.gateways.stripe.process_checkout_for_credit_purchase")
    def test_process_checkout_for_credit_purchase_stripe(self, mock_process_checkout):
        mock_process_checkout.return_value = {
            "action": "redirect",
            "url": "http://example.com",
        }

        result = ShopHelper.process_checkout_for_credit_purchase(
            self.request, self.credit_purchase
        )

        self.assertEqual(result, {"action": "redirect", "url": "http://example.com"})
        mock_process_checkout.assert_called_once_with(
            self.request, self.credit_purchase
        )

    @patch("apps.shop.gateways.stripe.process_checkout_for_product_purchase")
    def test_process_checkout_for_product_purchase_stripe(self, mock_process_checkout):
        mock_process_checkout.return_value = {
            "action": "redirect",
            "url": "http://example.com",
        }

        result = ShopHelper.process_checkout_for_product_purchase(
            self.request, self.product_purchase
        )

        self.assertEqual(result, {"action": "redirect", "url": "http://example.com"})
        mock_process_checkout.assert_called_once_with(
            self.request, self.product_purchase
        )

    @patch("apps.shop.gateways.stripe.process_webhook")
    def test_process_webhook_stripe(self, mock_process_webhook):
        result = ShopHelper.process_webhook(self.request, PaymentGateway.STRIPE)

        mock_process_webhook.assert_called_once_with(self.request)
        self.assertIsNotNone(result)

    @patch("apps.shop.gateways.stripe.process_cancel_for_subscription")
    def test_process_cancel_for_subscription_stripe(self, mock_process_cancel):
        mock_process_cancel.return_value = True

        result = ShopHelper.process_cancel_for_subscription(
            self.request, self.subscription
        )

        self.assertTrue(result)
        mock_process_cancel.assert_called_once_with(self.request, self.subscription)

    def test_process_checkout_for_subscription_invalid_gateway(self):
        self.plan.gateway = "INVALID_GATEWAY"
        result = ShopHelper.process_checkout_for_subscription(
            self.request, self.subscription
        )
        self.assertIsNone(result)

    def test_process_webhook_invalid_gateway(self):
        result = ShopHelper.process_webhook(self.request, "INVALID_GATEWAY")
        self.assertIsNone(result)

    def test_process_cancel_for_subscription_invalid_gateway(self):
        self.plan.gateway = "INVALID_GATEWAY"
        result = ShopHelper.process_cancel_for_subscription(
            self.request, self.subscription
        )
        self.assertIsNone(result)

    @patch("django.core.cache.cache.get")
    @patch("django.core.cache.cache.set")
    def test_get_plans_by_type(self, mock_cache_set, mock_cache_get):
        mock_cache_get.return_value = None

        with patch("apps.shop.models.Plan.objects.filter") as mock_filter:
            mock_filter.return_value.order_by.return_value.all.return_value = [
                "plan1",
                "plan2",
            ]

            # test getting plans by type
            result = ShopHelper.get_plans_by_type(plan_type="credit-purchase")
            self.assertEqual(result, ["plan1", "plan2"])
            mock_cache_get.assert_called_once()
            mock_cache_set.assert_called_once()

            # reset mocks
            mock_cache_get.reset_mock()
            mock_cache_set.reset_mock()

            # test when plans are already in cache
            mock_cache_get.return_value = ["cached_plan1", "cached_plan2"]
            result = ShopHelper.get_plans_by_type(plan_type="credit-purchase")
            self.assertEqual(result, ["cached_plan1", "cached_plan2"])
            mock_cache_get.assert_called_once()
            mock_cache_set.assert_not_called()

    def test_get_item_by_token(self):
        # test invalid token
        result = ShopHelper.get_item_by_token(None, None)
        self.assertIsNone(result)

        # test invalid customer
        result = ShopHelper.get_item_by_token("token", None)
        self.assertIsNone(result)

        # test invalid token format
        result = ShopHelper.get_item_by_token("invalid_token", "customer")
        self.assertIsNone(result)

        # test with credit purchase token
        with patch("apps.shop.models.CreditPurchase.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = self.credit_purchase
            result = ShopHelper.get_item_by_token(
                f"{ObjectType.CREDIT_PURCHASE}.123", "customer"
            )
            self.assertEqual(result, self.credit_purchase)

        # test with subscription token
        with patch("apps.shop.models.Subscription.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = self.subscription
            result = ShopHelper.get_item_by_token(
                f"{ObjectType.SUBSCRIPTION}.123", "customer"
            )
            self.assertEqual(result, self.subscription)

        # test with product purchase token
        with patch("apps.shop.models.ProductPurchase.objects.filter") as mock_filter:
            mock_filter.return_value.first.return_value = self.product_purchase
            result = ShopHelper.get_item_by_token(
                f"{ObjectType.PRODUCT_PURCHASE}.123", "customer"
            )
            self.assertEqual(result, self.product_purchase)

    def test_get_item_type_by_token(self):
        # test invalid token
        result = ShopHelper.get_item_type_by_token(None)
        self.assertIsNone(result)

        # test valid token
        result = ShopHelper.get_item_type_by_token(f"{ObjectType.CREDIT_PURCHASE}.123")
        self.assertEqual(result, ObjectType.CREDIT_PURCHASE)
