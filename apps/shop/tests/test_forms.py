from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.enums import (
    ObjectType,
    PaymentGateway,
    PlanFrequencyType,
    PlanType,
)
from apps.shop.forms import CheckoutForm
from apps.shop.models import Plan, Product

User = get_user_model()


class CheckoutFormTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.language = Language.objects.create(name="English")
        self.user = User.objects.create_user(
            email="buyer@example.com", password="pass", site=self.site
        )
        self.customer = Customer.objects.create(
            user=self.user, site=self.site, language=self.language
        )
        self.plan = Plan.objects.create(
            name="Gold Plan",
            tag="gold-plan",
            gateway=PaymentGateway.STRIPE,
            currency="USD",
            price=49.90,
            credits=100,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            site=self.site,
        )
        self.product = Product.objects.create(
            name="Book",
            slug="book",
            currency="USD",
            price=29.90,
            site=self.site,
        )

    def test_create_for_subscription(self):
        form = CheckoutForm()
        form.create_for_subscription(self.plan, self.customer)

        self.assertEqual(form.gateway, PaymentGateway.STRIPE)
        self.assertEqual(form.object_type, ObjectType.SUBSCRIPTION)
        self.assertEqual(form.object_id, self.plan.id)
        self.assertEqual(form.customer, self.customer)
        self.assertEqual(form.price, self.plan.price)
        self.assertEqual(form.total_price, self.plan.price)
        self.assertEqual(form.currency, self.plan.currency)
        self.assertFalse(form.show_price_data)

    def test_create_for_credit_purchase(self):
        form = CheckoutForm()
        form.create_for_credit_purchase(self.plan, self.customer)

        self.assertEqual(form.object_type, ObjectType.CREDIT_PURCHASE)
        self.assertEqual(form.object_id, self.plan.id)
        self.assertEqual(form.title, self.plan.name)
        self.assertEqual(form.total_price, self.plan.price)
        self.assertFalse(form.show_price_data)

    def test_create_for_product_purchase(self):
        form = CheckoutForm()
        form.create_for_product_purchase(self.product, self.customer)

        self.assertEqual(form.gateway, PaymentGateway.STRIPE)
        self.assertEqual(form.object_type, ObjectType.PRODUCT_PURCHASE)
        self.assertEqual(form.object_id, self.product.id)
        self.assertEqual(form.price, self.product.price)
        self.assertEqual(form.currency, self.product.currency)
        self.assertTrue(form.show_price_data)

    def test_clean_returns_cleaned_data(self):
        form = CheckoutForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get("options"), "")
