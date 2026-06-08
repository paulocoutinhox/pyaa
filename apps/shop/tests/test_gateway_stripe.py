from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import stripe
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.http import JsonResponse
from django.test import RequestFactory, TestCase, override_settings

from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PaymentGatewayAction,
    PaymentGatewayCancelAction,
    PlanFrequencyType,
    PlanType,
    ProductPurchaseStatus,
    SubscriptionStatus,
)
from apps.shop.gateways import stripe as gateway
from apps.shop.models import (
    CreditPurchase,
    EventLog,
    Plan,
    Product,
    ProductPurchase,
    Subscription,
)

User = get_user_model()


@override_settings(
    STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_WEBHOOK_SECRET="whsec_dummy"
)
class StripeGatewayTestBase(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            email="buyer@example.com",
            password="testpassword",
            site=self.site,
        )

        self.language = Language.objects.create(name="English")

        self.customer = Customer.objects.create(
            user=self.user,
            site=self.site,
            language=self.language,
            gender="male",
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            external_id="price_123",
            currency="USD",
            price=Decimal("9.99"),
            credits=10,
            bonus=0,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            currency="USD",
            price=Decimal("19.99"),
            active=True,
            site=self.site,
        )

    def build_request(self):
        # build an authenticated request with absolute uri support
        request = self.factory.post("/webhook/")
        request.user = self.user
        return request


class ProcessCheckoutSubscriptionTest(StripeGatewayTestBase):
    @patch("apps.shop.gateways.stripe.stripe.checkout.Session.create")
    def test_creates_session_and_returns_redirect(self, mock_create):
        mock_create.return_value = SimpleNamespace(url="https://stripe.test/session")

        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.INITIAL,
            site=self.site,
        )

        request = self.build_request()
        result = gateway.process_checkout_for_subscription(request, subscription)

        # verify the redirect action and url are returned
        self.assertEqual(result["action"], PaymentGatewayAction.REDIRECT)
        self.assertEqual(result["url"], "https://stripe.test/session")

        # verify stripe was called with subscription mode and the plan price id
        self.assertEqual(stripe.api_key, "sk_test_dummy")
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["mode"], "subscription")
        self.assertEqual(kwargs["line_items"][0]["price"], "price_123")
        self.assertEqual(kwargs["customer_email"], "buyer@example.com")
        self.assertEqual(kwargs["client_reference_id"], str(subscription.token))
        self.assertEqual(kwargs["metadata"]["token"], subscription.token)

        # verify an event log was created
        log = EventLog.objects.get(
            object_type=ObjectType.SUBSCRIPTION, object_id=subscription.id
        )
        self.assertEqual(log.customer, self.customer)
        self.assertEqual(log.amount, Decimal(self.plan.price))


class ProcessCheckoutCreditPurchaseTest(StripeGatewayTestBase):
    @patch("apps.shop.gateways.stripe.stripe.checkout.Session.create")
    def test_creates_payment_session(self, mock_create):
        mock_create.return_value = SimpleNamespace(url="https://stripe.test/credit")

        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        request = self.build_request()
        result = gateway.process_checkout_for_credit_purchase(request, purchase)

        self.assertEqual(result["action"], PaymentGatewayAction.REDIRECT)
        self.assertEqual(result["url"], "https://stripe.test/credit")

        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["mode"], "payment")
        line = kwargs["line_items"][0]
        self.assertEqual(line["price_data"]["currency"], "usd")
        self.assertEqual(line["price_data"]["product_data"]["name"], self.plan.name)
        # unit amount is in cents
        self.assertEqual(line["price_data"]["unit_amount"], int(self.plan.price * 100))

        log = EventLog.objects.get(
            object_type=ObjectType.CREDIT_PURCHASE, object_id=purchase.id
        )
        self.assertEqual(log.amount, Decimal(purchase.price))


class ProcessCheckoutProductPurchaseTest(StripeGatewayTestBase):
    @patch("apps.shop.gateways.stripe.stripe.checkout.Session.create")
    def test_creates_payment_session(self, mock_create):
        mock_create.return_value = SimpleNamespace(url="https://stripe.test/product")

        purchase = ProductPurchase.objects.create(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=Decimal("19.99"),
            status=ProductPurchaseStatus.INITIAL,
            site=self.site,
        )

        request = self.build_request()
        result = gateway.process_checkout_for_product_purchase(request, purchase)

        self.assertEqual(result["action"], PaymentGatewayAction.REDIRECT)
        self.assertEqual(result["url"], "https://stripe.test/product")

        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["mode"], "payment")
        line = kwargs["line_items"][0]
        self.assertEqual(line["price_data"]["currency"], "usd")
        self.assertEqual(line["price_data"]["product_data"]["name"], self.product.name)
        self.assertEqual(line["price_data"]["unit_amount"], int(purchase.price * 100))

        log = EventLog.objects.get(
            object_type=ObjectType.PRODUCT_PURCHASE, object_id=purchase.id
        )
        self.assertEqual(log.amount, Decimal(purchase.price))


class ProcessCancelSubscriptionTest(StripeGatewayTestBase):
    def _request_with_messages(self):
        request = self.factory.post("/cancel/")
        request.user = self.user
        # attach a message storage backend
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(request, "session", {})
        setattr(request, "_messages", FallbackStorage(request))
        return request

    @patch("apps.shop.gateways.stripe.stripe.Subscription.cancel")
    def test_cancel_success(self, mock_cancel):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            external_id="sub_123",
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        request = self._request_with_messages()
        result = gateway.process_cancel_for_subscription(request, subscription)

        mock_cancel.assert_called_once_with("sub_123")
        self.assertEqual(result["action"], PaymentGatewayCancelAction.REDIRECT)

        from django.contrib import messages as messages_constants

        stored = list(request._messages)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].level, messages_constants.SUCCESS)

    @patch("apps.shop.gateways.stripe.stripe.Subscription.cancel")
    def test_cancel_failure_adds_error_message(self, mock_cancel):
        mock_cancel.side_effect = Exception("boom")

        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            external_id="sub_456",
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        request = self._request_with_messages()
        result = gateway.process_cancel_for_subscription(request, subscription)

        mock_cancel.assert_called_once_with("sub_456")
        self.assertEqual(result["action"], PaymentGatewayCancelAction.REDIRECT)

        from django.contrib import messages as messages_constants

        stored = list(request._messages)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].level, messages_constants.ERROR)


@override_settings(
    STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_WEBHOOK_SECRET="whsec_dummy"
)
class ProcessWebhookErrorTest(StripeGatewayTestBase):
    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_invalid_payload_returns_400(self, mock_construct):
        mock_construct.side_effect = ValueError("bad payload")

        request = self.factory.post(
            "/webhook/", data=b"{}", content_type="application/json"
        )
        result = gateway.process_webhook(request)

        response = result["response"]
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct):
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "bad sig", "sig_header"
        )

        request = self.factory.post(
            "/webhook/", data=b"{}", content_type="application/json"
        )
        result = gateway.process_webhook(request)

        self.assertEqual(result["response"].status_code, 400)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_generic_exception_returns_500(self, mock_construct):
        mock_construct.side_effect = Exception("unexpected")

        request = self.factory.post(
            "/webhook/", data=b"{}", content_type="application/json"
        )
        result = gateway.process_webhook(request)

        self.assertEqual(result["response"].status_code, 500)


@override_settings(
    STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_WEBHOOK_SECRET="whsec_dummy"
)
class ProcessWebhookDispatchTest(StripeGatewayTestBase):
    def _webhook_request(self):
        request = self.factory.post(
            "/webhook/", data=b"{}", content_type="application/json"
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "sig"
        return request

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_no_token_returns_success_without_logging(self, mock_construct):
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "evt_no_token"}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        # no event log should be created when there is no token
        self.assertEqual(EventLog.objects.count(), 0)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_subscription_payment_succeeded(self, mock_construct):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "metadata": {"token": subscription.token},
                    "subscription": "sub_remote_1",
                    "amount_paid": 999,
                    "currency": "usd",
                }
            },
        }

        with patch.object(Subscription, "process_completed") as mock_completed:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_called_once()

        # external id is recorded from the event data
        subscription.refresh_from_db()
        self.assertEqual(subscription.external_id, "sub_remote_1")

        # event log is created and linked to the subscription
        log = EventLog.objects.latest("id")
        self.assertEqual(log.object_type, ObjectType.SUBSCRIPTION)
        self.assertEqual(log.object_id, subscription.id)
        self.assertEqual(log.customer, self.customer)
        self.assertEqual(log.amount, Decimal("9.99"))
        self.assertEqual(log.currency, "USD")

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_subscription_deleted_calls_canceled(self, mock_construct):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            external_id="sub_existing",
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"metadata": {"token": subscription.token}}},
        }

        with patch.object(Subscription, "process_canceled") as mock_canceled:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_canceled.assert_called_once()

        # external id is not overwritten when already set
        subscription.refresh_from_db()
        self.assertEqual(subscription.external_id, "sub_existing")

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_subscription_refunded_calls_refunded(self, mock_construct):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            external_id="sub_ref",
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "charge.refunded",
            "data": {
                "object": {
                    "metadata": {"token": subscription.token},
                    "amount": 999,
                    "currency": "usd",
                }
            },
        }

        with patch.object(Subscription, "process_refunded") as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_refunded.assert_called_once()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_subscription_not_found_is_ignored(self, mock_construct):
        mock_construct.return_value = {
            "type": "invoice.payment_succeeded",
            "data": {"object": {"metadata": {"token": "subscription.missing"}}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        # an event log is still created before lookup
        self.assertEqual(EventLog.objects.count(), 1)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_completed(self, mock_construct):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"token": purchase.token},
                    "amount_total": 999,
                    "currency": "usd",
                }
            },
        }

        with patch.object(CreditPurchase, "process_completed") as mock_completed:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_called_once()

        log = EventLog.objects.latest("id")
        self.assertEqual(log.object_type, ObjectType.CREDIT_PURCHASE)
        self.assertEqual(log.object_id, purchase.id)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_canceled(self, mock_construct):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "payment_intent.canceled",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(CreditPurchase, "process_canceled") as mock_canceled:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_canceled.assert_called_once()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_refunded(self, mock_construct):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "charge.refunded",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(CreditPurchase, "process_refunded") as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_refunded.assert_called_once()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_not_found_is_ignored(self, mock_construct):
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"metadata": {"token": "credit-purchase.missing"}}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        self.assertEqual(EventLog.objects.count(), 1)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_product_purchase_completed(self, mock_construct):
        purchase = ProductPurchase.objects.create(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=Decimal("19.99"),
            status=ProductPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"token": purchase.token},
                    "amount_total": 1999,
                    "currency": "usd",
                }
            },
        }

        with patch.object(ProductPurchase, "process_completed") as mock_completed:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_called_once()

        log = EventLog.objects.latest("id")
        self.assertEqual(log.object_type, ObjectType.PRODUCT_PURCHASE)
        self.assertEqual(log.object_id, purchase.id)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_product_purchase_canceled(self, mock_construct):
        purchase = ProductPurchase.objects.create(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=Decimal("19.99"),
            status=ProductPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "payment_intent.canceled",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(ProductPurchase, "process_canceled") as mock_canceled:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_canceled.assert_called_once()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_product_purchase_refunded(self, mock_construct):
        purchase = ProductPurchase.objects.create(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=Decimal("19.99"),
            status=ProductPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "charge.refunded",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(ProductPurchase, "process_refunded") as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_refunded.assert_called_once()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_product_purchase_not_found_is_ignored(self, mock_construct):
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"metadata": {"token": "product-purchase.missing"}}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        self.assertEqual(EventLog.objects.count(), 1)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_unknown_token_prefix_not_dispatched(self, mock_construct):
        # a token with no recognized prefix should not be dispatched
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"metadata": {"token": "voucher.unknown"}}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        # event log is still created
        self.assertEqual(EventLog.objects.count(), 1)

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_subscription_unhandled_event_type(self, mock_construct):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            external_id="sub_x",
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "invoice.created",
            "data": {"object": {"metadata": {"token": subscription.token}}},
        }

        with patch.object(
            Subscription, "process_completed"
        ) as mock_completed, patch.object(
            Subscription, "process_canceled"
        ) as mock_canceled, patch.object(
            Subscription, "process_refunded"
        ) as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_not_called()
        mock_canceled.assert_not_called()
        mock_refunded.assert_not_called()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_unhandled_event_type(self, mock_construct):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "invoice.created",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(
            CreditPurchase, "process_completed"
        ) as mock_completed, patch.object(
            CreditPurchase, "process_canceled"
        ) as mock_canceled, patch.object(
            CreditPurchase, "process_refunded"
        ) as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_not_called()
        mock_canceled.assert_not_called()
        mock_refunded.assert_not_called()

    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_product_purchase_unhandled_event_type(self, mock_construct):
        purchase = ProductPurchase.objects.create(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=Decimal("19.99"),
            status=ProductPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "invoice.created",
            "data": {"object": {"metadata": {"token": purchase.token}}},
        }

        with patch.object(
            ProductPurchase, "process_completed"
        ) as mock_completed, patch.object(
            ProductPurchase, "process_canceled"
        ) as mock_canceled, patch.object(
            ProductPurchase, "process_refunded"
        ) as mock_refunded:
            result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        mock_completed.assert_not_called()
        mock_canceled.assert_not_called()
        mock_refunded.assert_not_called()


@override_settings(
    STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_WEBHOOK_SECRET="whsec_dummy"
)
class WebhookRealProcessTest(StripeGatewayTestBase):
    # tests that exercise the real model process methods to verify db updates
    def _webhook_request(self):
        request = self.factory.post(
            "/webhook/", data=b"{}", content_type="application/json"
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "sig"
        return request

    @patch("apps.customer.helpers.CustomerHelper.send_credit_purchase_paid_email")
    @patch("apps.shop.gateways.stripe.stripe.Webhook.construct_event")
    def test_credit_purchase_completed_updates_db(self, mock_construct, mock_email):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=Decimal("9.99"),
            status=CreditPurchaseStatus.INITIAL,
            site=self.site,
        )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"client_reference_id": purchase.token}},
        }

        result = gateway.process_webhook(self._webhook_request())

        self.assertEqual(result["response"].status_code, 200)
        purchase.refresh_from_db()
        self.assertEqual(purchase.status, CreditPurchaseStatus.APPROVED)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.credits, self.plan.credits)
        mock_email.assert_called_once()


class CreateEventLogTest(StripeGatewayTestBase):
    def test_create_event_log_sets_amount_and_currency(self):
        event_log = gateway.create_event_log(
            "invoice.payment_succeeded",
            {"amount_paid": 1500, "currency": "eur"},
        )

        self.assertEqual(event_log.status, "invoice.payment_succeeded")
        self.assertEqual(event_log.amount, Decimal("15"))
        self.assertEqual(event_log.currency, "EUR")


class ExtractAmountAndCurrencyTest(TestCase):
    def test_total(self):
        amount, currency = gateway.extract_amount_and_currency(
            {"total": 5000, "currency": "usd"}
        )
        self.assertEqual(amount, Decimal("50"))
        self.assertEqual(currency, "usd")

    def test_amount_paid(self):
        amount, _currency = gateway.extract_amount_and_currency({"amount_paid": 2500})
        self.assertEqual(amount, Decimal("25"))

    def test_amount_total(self):
        amount, _currency = gateway.extract_amount_and_currency({"amount_total": 100})
        self.assertEqual(amount, Decimal("1"))

    def test_amount(self):
        amount, _currency = gateway.extract_amount_and_currency({"amount": 999})
        self.assertEqual(amount, Decimal("9.99"))

    def test_plan_amount(self):
        amount, currency = gateway.extract_amount_and_currency(
            {"plan": {"amount": 1200, "currency": "gbp"}}
        )
        self.assertEqual(amount, Decimal("12"))
        self.assertEqual(currency, "gbp")

    def test_no_amount_or_currency(self):
        amount, currency = gateway.extract_amount_and_currency({"foo": "bar"})
        self.assertEqual(amount, Decimal(0))
        self.assertIsNone(currency)


class ExtractTokenTest(TestCase):
    def test_metadata_token(self):
        self.assertEqual(
            gateway.extract_token({"metadata": {"token": "subscription.a"}}),
            "subscription.a",
        )

    def test_client_reference_id(self):
        self.assertEqual(
            gateway.extract_token({"client_reference_id": "credit-purchase.b"}),
            "credit-purchase.b",
        )

    def test_subscription_details_metadata(self):
        self.assertEqual(
            gateway.extract_token(
                {"subscription_details": {"metadata": {"token": "subscription.c"}}}
            ),
            "subscription.c",
        )

    def test_parent_subscription_details_metadata(self):
        self.assertEqual(
            gateway.extract_token(
                {
                    "parent": {
                        "subscription_details": {
                            "metadata": {"token": "subscription.d"}
                        }
                    }
                }
            ),
            "subscription.d",
        )

    def test_lines_data_metadata(self):
        self.assertEqual(
            gateway.extract_token(
                {"lines": {"data": [{"metadata": {"token": "product-purchase.e"}}]}}
            ),
            "product-purchase.e",
        )

    def test_no_token_returns_none(self):
        self.assertIsNone(gateway.extract_token({"id": "evt_1"}))

    def test_metadata_without_token_falls_through(self):
        # metadata present but without a token and no other source
        self.assertIsNone(gateway.extract_token({"metadata": {"foo": "bar"}}))

    def test_lines_without_token_returns_none(self):
        self.assertIsNone(
            gateway.extract_token({"lines": {"data": [{"metadata": {"foo": "bar"}}]}})
        )

    def test_subscription_details_without_metadata(self):
        # subscription details present but without metadata
        self.assertIsNone(gateway.extract_token({"subscription_details": {}}))

    def test_subscription_details_metadata_without_token(self):
        self.assertIsNone(
            gateway.extract_token({"subscription_details": {"metadata": {"x": "y"}}})
        )

    def test_parent_without_subscription_details(self):
        self.assertIsNone(gateway.extract_token({"parent": {"foo": "bar"}}))

    def test_parent_subscription_details_without_token(self):
        self.assertIsNone(
            gateway.extract_token(
                {"parent": {"subscription_details": {"metadata": {"x": "y"}}}}
            )
        )

    def test_lines_data_line_without_metadata(self):
        # iterate lines where a line item has no metadata key
        self.assertIsNone(gateway.extract_token({"lines": {"data": [{"id": "li_1"}]}}))

    def test_lines_without_data_key(self):
        # lines present but with no usable data list
        self.assertIsNone(gateway.extract_token({"lines": {"other": "x"}}))

    def test_lines_data_multiple_lines_then_token(self):
        # first line has no token, second line provides the token
        self.assertEqual(
            gateway.extract_token(
                {
                    "lines": {
                        "data": [
                            {"metadata": {"foo": "bar"}},
                            {"metadata": {"token": "subscription.f"}},
                        ]
                    }
                }
            ),
            "subscription.f",
        )
