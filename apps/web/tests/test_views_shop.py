from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.customer.enums import CustomerGender
from apps.customer.models import Customer
from apps.language import models as language_models
from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PaymentGateway,
    PaymentGatewayAction,
    PlanType,
    ProductPurchaseStatus,
    SubscriptionStatus,
)
from apps.shop.models import (
    CreditPurchase,
    Plan,
    Product,
    ProductPurchase,
    Subscription,
)

User = get_user_model()


def create_customer(email="shop@example.com"):
    site = Site.objects.get_current()
    language = language_models.Language.objects.first()
    user = User.objects.create_user(email=email, password="StrongPass123", site=site)
    customer = Customer.objects.create(
        user=user,
        site=site,
        language=language,
        gender=CustomerGender.MALE,
    )
    return user, customer


def create_plan(plan_type=PlanType.SUBSCRIPTION):
    return Plan.objects.create(
        site=Site.objects.get_current(),
        name="Test Plan",
        plan_type=plan_type,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price="10.00",
        active=True,
    )


def create_product():
    return Product.objects.create(
        site=Site.objects.get_current(),
        name="Test Product",
        slug="test-product",
        currency="USD",
        price="20.00",
        active=True,
    )


class ShopProductsViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def tearDown(self):
        cache.clear()

    def test_products_list_renders(self):
        product = create_product()
        response = self.client.get(reverse("shop_products"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/product/index.html")
        self.assertIn(product, list(response.context["products"]))


class ShopProductDetailsViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.product = create_product()

    def tearDown(self):
        cache.clear()

    def test_details_renders_with_matching_slug(self):
        response = self.client.get(
            reverse(
                "shop_product_details",
                kwargs={"product_token": self.product.token, "slug": "test-product"},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/product/detail.html")
        self.assertEqual(response.context["product"], self.product)

    def test_details_redirects_to_correct_slug(self):
        response = self.client.get(
            reverse(
                "shop_product_details",
                kwargs={"product_token": self.product.token, "slug": "wrong-slug"},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("test-product", response.url)

    def test_details_no_slug_redirects_to_slug(self):
        response = self.client.get(
            reverse(
                "shop_product_details_no_slug",
                kwargs={"product_token": self.product.token},
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_details_not_found_redirects_to_products(self):
        response = self.client.get(
            reverse(
                "shop_product_details_no_slug",
                kwargs={"product_token": "00000000-0000-0000-0000-000000000000"},
            )
        )
        self.assertRedirects(response, reverse("shop_products"))


class ShopPlansViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def tearDown(self):
        cache.clear()

    def test_plans_renders(self):
        create_plan(PlanType.SUBSCRIPTION)
        response = self.client.get(
            reverse("shop_plans", kwargs={"plan_type": PlanType.SUBSCRIPTION})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/plans.html")

    def test_invalid_plan_type_redirects_home(self):
        response = self.client.get(
            reverse("shop_plans", kwargs={"plan_type": "invalid"})
        )
        self.assertRedirects(response, reverse("home"))

    def test_subscription_plans_redirect_when_already_subscriber(self):
        user, customer = create_customer()
        plan = create_plan(PlanType.SUBSCRIPTION)
        Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() + timezone.timedelta(days=30),
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("shop_plans", kwargs={"plan_type": PlanType.SUBSCRIPTION})
        )
        self.assertRedirects(response, reverse("account_profile"))


class ShopCheckoutViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_checkout_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={"type": ObjectType.SUBSCRIPTION, "code": "abc"},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_checkout_get_subscription_renders(self):
        plan = create_plan(PlanType.SUBSCRIPTION)
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={"type": ObjectType.SUBSCRIPTION, "code": str(plan.token)},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/checkout/index.html")

    def test_checkout_get_credit_purchase_renders(self):
        plan = create_plan(PlanType.CREDIT_PURCHASE)
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.CREDIT_PURCHASE,
                    "code": str(plan.token),
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_get_product_purchase_renders(self):
        product = create_product()
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.PRODUCT_PURCHASE,
                    "code": str(product.token),
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_get_invalid_type_redirects_home(self):
        response = self.client.get(
            reverse("shop_checkout", kwargs={"type": "invalid", "code": "abc"})
        )
        self.assertRedirects(response, reverse("home"))

    @patch("apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_subscription")
    def test_checkout_post_subscription_redirects_to_gateway(self, mock_checkout):
        plan = create_plan(PlanType.SUBSCRIPTION)
        mock_checkout.return_value = {
            "action": PaymentGatewayAction.REDIRECT,
            "url": "https://gateway.example/pay",
            "external_reference": "ref-123",
        }

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={"type": ObjectType.SUBSCRIPTION, "code": str(plan.token)},
            ),
            {},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://gateway.example/pay")
        self.assertTrue(
            Subscription.objects.filter(
                customer=self.customer, status=SubscriptionStatus.INITIAL
            ).exists()
        )

    @patch(
        "apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_credit_purchase"
    )
    def test_checkout_post_credit_purchase_redirects(self, mock_checkout):
        plan = create_plan(PlanType.CREDIT_PURCHASE)
        mock_checkout.return_value = {
            "action": PaymentGatewayAction.REDIRECT,
            "url": "https://gateway.example/credit",
            "external_reference": "ref-456",
        }

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.CREDIT_PURCHASE,
                    "code": str(plan.token),
                },
            ),
            {},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://gateway.example/credit")
        self.assertTrue(
            CreditPurchase.objects.filter(
                customer=self.customer, status=CreditPurchaseStatus.INITIAL
            ).exists()
        )

    @patch(
        "apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_product_purchase"
    )
    def test_checkout_post_product_purchase_redirects(self, mock_checkout):
        product = create_product()
        mock_checkout.return_value = {
            "action": PaymentGatewayAction.REDIRECT,
            "url": "https://gateway.example/product",
            "external_reference": "ref-789",
        }

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.PRODUCT_PURCHASE,
                    "code": str(product.token),
                },
            ),
            {},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://gateway.example/product")
        self.assertTrue(
            ProductPurchase.objects.filter(
                customer=self.customer, status=ProductPurchaseStatus.INITIAL
            ).exists()
        )

    def test_checkout_post_plan_not_found_redirects_home(self):
        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.SUBSCRIPTION,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    def test_checkout_post_credit_plan_not_found_redirects_home(self):
        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.CREDIT_PURCHASE,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    def test_checkout_post_product_not_found_redirects_home(self):
        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.PRODUCT_PURCHASE,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    @patch("apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_subscription")
    def test_checkout_post_missing_external_reference_redirects_home(
        self, mock_checkout
    ):
        plan = create_plan(PlanType.SUBSCRIPTION)
        # non-redirect action returns invalid action error and redirects home
        mock_checkout.return_value = {"action": "invalid"}

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={"type": ObjectType.SUBSCRIPTION, "code": str(plan.token)},
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    @patch(
        "apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_credit_purchase"
    )
    def test_checkout_post_credit_invalid_action_redirects_home(self, mock_checkout):
        plan = create_plan(PlanType.CREDIT_PURCHASE)
        mock_checkout.return_value = {"action": "invalid"}

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.CREDIT_PURCHASE,
                    "code": str(plan.token),
                },
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    @patch(
        "apps.web.views.shop.shop_web.ShopHelper.process_checkout_for_product_purchase"
    )
    def test_checkout_post_product_invalid_action_redirects_home(self, mock_checkout):
        product = create_product()
        mock_checkout.return_value = {"action": "invalid"}

        response = self.client.post(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.PRODUCT_PURCHASE,
                    "code": str(product.token),
                },
            ),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    def test_checkout_get_subscription_plan_not_found_still_renders(self):
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.SUBSCRIPTION,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_get_credit_plan_not_found_still_renders(self):
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.CREDIT_PURCHASE,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_get_product_not_found_still_renders(self):
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={
                    "type": ObjectType.PRODUCT_PURCHASE,
                    "code": "00000000-0000-0000-0000-000000000000",
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_post_invalid_type_redirects_home(self):
        response = self.client.post(
            reverse("shop_checkout", kwargs={"type": "invalid", "code": "abc"}),
            {},
        )
        self.assertRedirects(response, reverse("home"))

    def test_checkout_without_customer_redirects_home(self):
        plain_user = User.objects.create_user(
            email="plain@example.com",
            password="StrongPass123",
            site=Site.objects.get_current(),
        )
        self.client.force_login(plain_user)
        response = self.client.get(
            reverse(
                "shop_checkout",
                kwargs={"type": ObjectType.SUBSCRIPTION, "code": "abc"},
            )
        )
        self.assertRedirects(response, reverse("home"))


class ShopPaymentResultViewsTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)
        self.plan = create_plan(PlanType.SUBSCRIPTION)
        self.subscription = Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
        )

    def test_payment_success_renders(self):
        response = self.client.get(
            reverse("shop_payment_success", kwargs={"token": self.subscription.token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/payment/success.html")
        self.assertEqual(response.context["paid_item"], self.subscription)

    def test_payment_error_renders(self):
        response = self.client.get(
            reverse("shop_payment_error", kwargs={"token": self.subscription.token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/payment/error.html")

    def test_payment_pending_renders(self):
        response = self.client.get(
            reverse("shop_payment_pending", kwargs={"token": self.subscription.token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop/payment/pending.html")

    def test_payment_success_unknown_token_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_success", kwargs={"token": "subscription.unknown"})
        )
        self.assertRedirects(response, reverse("home"))

    def test_payment_error_unknown_token_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_error", kwargs={"token": "subscription.unknown"})
        )
        self.assertRedirects(response, reverse("home"))

    def test_payment_pending_unknown_token_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_pending", kwargs={"token": "subscription.unknown"})
        )
        self.assertRedirects(response, reverse("home"))


class ShopPaymentResultNoCustomerTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # logged-in user without a customer record
        self.user = User.objects.create_user(
            email="plain@example.com",
            password="StrongPass123",
            site=Site.objects.get_current(),
        )
        self.client.force_login(self.user)

    def test_payment_success_without_customer_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_success", kwargs={"token": "subscription.x"})
        )
        self.assertRedirects(response, reverse("home"))

    def test_payment_error_without_customer_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_error", kwargs={"token": "subscription.x"})
        )
        self.assertRedirects(response, reverse("home"))

    def test_payment_pending_without_customer_redirects_home(self):
        response = self.client.get(
            reverse("shop_payment_pending", kwargs={"token": "subscription.x"})
        )
        self.assertRedirects(response, reverse("home"))


class ShopWebhookViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    @patch("apps.web.views.shop.shop_webhook.ShopHelper.process_webhook")
    def test_webhook_returns_helper_response(self, mock_process):
        mock_process.return_value = {"response": HttpResponse("ok", status=200)}

        response = self.client.post(
            reverse("shop_webhook_stripe"),
            data="{}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
        mock_process.assert_called_once()

    @patch("apps.web.views.shop.shop_webhook.SystemLogHelper.create")
    @patch("apps.web.views.shop.shop_webhook.ShopHelper.process_webhook")
    def test_webhook_logs_when_enabled(self, mock_process, mock_log):
        mock_process.return_value = {"response": HttpResponse(status=200)}

        with self.settings(SYSTEM_LOG_WEBHOOK_ENABLED=True):
            response = self.client.post(
                reverse("shop_webhook_stripe"),
                data="{}",
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        mock_log.assert_called_once()
