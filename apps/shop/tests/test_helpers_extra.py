from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase
from django.utils.translation import override

from apps.shop.enums import ObjectType, PaymentGateway, PlanType
from apps.shop.helpers import ShopHelper
from apps.shop.models import CreditPurchase, Plan, ProductPurchase, Subscription


class ShopHelperExtraTest(TestCase):
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
        )

        self.subscription = Subscription(plan=self.plan)
        self.credit_purchase = CreditPurchase(plan=self.plan)
        self.product_purchase = ProductPurchase(product=None)

    def test_process_checkout_for_credit_purchase_invalid_gateway(self):
        self.plan.gateway = "INVALID_GATEWAY"

        result = ShopHelper.process_checkout_for_credit_purchase(
            self.request, self.credit_purchase
        )

        self.assertIsNone(result)

    @patch("apps.shop.helpers.settings")
    def test_process_checkout_for_product_purchase_invalid_gateway(self, mock_settings):
        mock_settings.GATEWAY_FOR_PRODUCT_PURCHASE = "INVALID_GATEWAY"

        result = ShopHelper.process_checkout_for_product_purchase(
            self.request, self.product_purchase
        )

        self.assertIsNone(result)

    @patch("django.utils.translation.get_language")
    @patch("django.core.cache.cache.get")
    @patch("django.core.cache.cache.set")
    def test_get_plans_by_type_no_language_uses_general_cache(
        self, mock_cache_set, mock_cache_get, mock_get_language
    ):
        # no language set and general plans already cached
        mock_get_language.return_value = None
        mock_cache_get.return_value = ["cached_general"]

        result = ShopHelper.get_plans_by_type(plan_type=None)

        self.assertEqual(result, ["cached_general"])
        mock_cache_get.assert_called_once()
        mock_cache_set.assert_not_called()

    def test_get_plans_by_type_no_language_queries_general_plans(self):
        # exercise the real no-language database branch
        cache.clear()
        site = Site.objects.get(pk=1)

        general_plan = Plan.objects.create(
            name="General Plan",
            tag="general-plan",
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.CREDIT_PURCHASE,
            sort_order=1,
            active=True,
            site=site,
            language=None,
        )

        with override(None):
            plans = ShopHelper.get_plans_by_type(plan_type=PlanType.CREDIT_PURCHASE)

        self.assertIn(general_plan, list(plans))
        cache.clear()

    def test_get_item_by_token_unknown_object_type(self):
        result = ShopHelper.get_item_by_token("unknown-type.123", "customer")

        self.assertIsNone(result)

    def test_get_item_type_by_token_invalid_format(self):
        result = ShopHelper.get_item_type_by_token("no-separator")

        self.assertIsNone(result)
