from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.templatetags.static import static
from django.test import TestCase
from django.utils.text import slugify

from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.enums import (
    CreditPurchaseStatus,
    ObjectType,
    PlanFrequencyType,
    PlanType,
    ProductPurchaseStatus,
    SubscriptionStatus,
)
from apps.shop.models import (
    CreditLog,
    CreditPurchase,
    Plan,
    Product,
    ProductFile,
    ProductPurchase,
    Subscription,
)

User = get_user_model()


class ProductModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)

    def test_product_str(self):
        product = Product.objects.create(
            name="My Product",
            slug="my-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

        self.assertEqual(str(product), "My Product")

    def test_product_save_uppercases_currency_and_slug(self):
        product = Product(
            name="Slugged Product",
            currency="usd",
            price=10.00,
            site=self.site,
        )

        product.save()

        self.assertEqual(product.currency, "USD")
        self.assertEqual(product.slug, slugify("Slugged Product"))

    def test_product_get_image_url_no_image(self):
        product = Product.objects.create(
            name="No Image Product",
            slug="no-image-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

        self.assertEqual(product.get_image_url(), static("images/product-no-image.png"))

    def test_product_get_image_url_with_external_url(self):
        product = Product.objects.create(
            name="External Image Product",
            slug="external-image-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

        product.image = "https://example.com/image.png"

        self.assertEqual(product.get_image_url(), "https://example.com/image.png")

    def test_product_get_image_url_with_local_file(self):
        product = Product.objects.create(
            name="Local Image Product",
            slug="local-image-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

        product.image = "images/product/local.png"

        self.assertIn("local.png", product.get_image_url())

    def test_product_get_active_files(self):
        product = Product.objects.create(
            name="Files Product",
            slug="files-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

        active_file = ProductFile.objects.create(
            product=product,
            name="Active File",
            file="files/product/active.pdf",
            active=True,
            sort_order=1,
        )

        ProductFile.objects.create(
            product=product,
            name="Inactive File",
            file="files/product/inactive.pdf",
            active=False,
            sort_order=2,
        )

        active_files = list(product.get_active_files())

        self.assertEqual(active_files, [active_file])


class ProductFileModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.product = Product.objects.create(
            name="Files Product",
            slug="files-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

    def test_product_file_str(self):
        product_file = ProductFile.objects.create(
            product=self.product,
            name="My File",
            file="files/product/my-file.pdf",
        )

        self.assertEqual(str(product_file), "My File")

    def test_get_file_url_no_file(self):
        product_file = ProductFile(product=self.product, name="No File")

        self.assertIsNone(product_file.get_file_url())

    def test_get_file_url_with_external_url(self):
        product_file = ProductFile.objects.create(
            product=self.product,
            name="External File",
            file="https://example.com/file.pdf",
        )

        self.assertEqual(product_file.get_file_url(), "https://example.com/file.pdf")

    def test_get_file_url_with_local_file(self):
        product_file = ProductFile.objects.create(
            product=self.product,
            name="Local File",
            file="files/product/local.pdf",
        )

        self.assertIn("local.pdf", product_file.get_file_url())


class PlanImageAndNameTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)

    def _make_plan(self, **kwargs):
        defaults = dict(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            site=self.site,
        )
        defaults.update(kwargs)
        return Plan.objects.create(**defaults)

    def test_get_image_url_no_image(self):
        plan = self._make_plan()

        self.assertEqual(plan.get_image_url(), static("images/plan-no-image.png"))

    def test_get_image_url_with_external_url(self):
        plan = self._make_plan()
        plan.image = "https://example.com/plan.png"

        self.assertEqual(plan.get_image_url(), "https://example.com/plan.png")

    def test_get_image_url_with_local_file(self):
        plan = self._make_plan()
        plan.image = "images/plan/local.png"

        self.assertIn("local.png", plan.get_image_url())

    def test_get_name_without_bonus(self):
        plan = self._make_plan(name="Plain Plan", tag="plain-plan", bonus=0)

        self.assertEqual(plan.get_name(), "Plain Plan")

    def test_get_name_with_bonus(self):
        plan = self._make_plan(name="Bonus Plan", tag="bonus-plan", bonus=5)

        name = plan.get_name()
        self.assertIn("Bonus Plan", name)
        self.assertIn("5", name)

    def test_get_frequency_in_days_no_frequency_type(self):
        plan = self._make_plan(
            name="No Freq Plan",
            tag="no-freq-plan",
            frequency_type=None,
        )

        self.assertEqual(plan.get_frequency_in_days(), 0)

    def test_get_frequency_in_days_zero_amount(self):
        plan = self._make_plan(
            name="Zero Amount Plan",
            tag="zero-amount-plan",
            frequency_amount=0,
        )

        self.assertEqual(plan.get_frequency_in_days(), 0)


class CreditPurchaseModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="cp@example.com", password="testpassword", site=self.site
        )
        self.language = Language.objects.create(name="English")
        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )
        self.plan = Plan.objects.create(
            name="Credit Plan",
            tag="credit-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=20,
            plan_type=PlanType.CREDIT_PURCHASE,
            site=self.site,
        )

    def _make_purchase(self, **kwargs):
        defaults = dict(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=9.99,
            site=self.site,
        )
        defaults.update(kwargs)
        return CreditPurchase.objects.create(**defaults)

    def test_process_completed(self):
        purchase = self._make_purchase()

        with patch(
            "apps.customer.helpers.CustomerHelper.send_credit_purchase_paid_email"
        ) as mock_email:
            purchase.process_completed()

        purchase.refresh_from_db()
        self.customer.refresh_from_db()

        self.assertEqual(purchase.status, CreditPurchaseStatus.APPROVED)
        self.assertEqual(self.customer.credits, self.plan.credits)
        mock_email.assert_called_once_with(purchase)

    def test_process_canceled(self):
        purchase = self._make_purchase()

        purchase.process_canceled()
        purchase.refresh_from_db()

        self.assertEqual(purchase.status, CreditPurchaseStatus.CANCELED)

    def test_process_refunded(self):
        purchase = self._make_purchase()

        purchase.process_refunded()
        purchase.refresh_from_db()

        self.assertEqual(purchase.status, CreditPurchaseStatus.REFUNDED)


class ProductPurchaseModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="pp@example.com", password="testpassword", site=self.site
        )
        self.language = Language.objects.create(name="English")
        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )
        self.product = Product.objects.create(
            name="Sellable Product",
            slug="sellable-product",
            currency="USD",
            price=15.00,
            site=self.site,
        )

    def _make_purchase(self, **kwargs):
        defaults = dict(
            customer=self.customer,
            product=self.product,
            currency="USD",
            price=15.00,
            site=self.site,
        )
        defaults.update(kwargs)
        return ProductPurchase.objects.create(**defaults)

    def test_process_completed(self):
        purchase = self._make_purchase()

        with patch(
            "apps.customer.helpers.CustomerHelper.send_product_purchase_paid_email"
        ) as mock_email:
            purchase.process_completed()

        purchase.refresh_from_db()

        self.assertEqual(purchase.status, ProductPurchaseStatus.APPROVED)
        mock_email.assert_called_once_with(purchase)

    def test_process_canceled(self):
        purchase = self._make_purchase()

        purchase.process_canceled()
        purchase.refresh_from_db()

        self.assertEqual(purchase.status, ProductPurchaseStatus.CANCELED)

    def test_process_refunded(self):
        purchase = self._make_purchase()

        purchase.process_refunded()
        purchase.refresh_from_db()

        self.assertEqual(purchase.status, ProductPurchaseStatus.REFUNDED)


class CreditLogExtraTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="cl@example.com", password="testpassword", site=self.site
        )
        self.language = Language.objects.create(name="English")
        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )
        self.plan = Plan.objects.create(
            name="Logged Plan",
            tag="logged-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            site=self.site,
        )

    def _make_log(self, **kwargs):
        defaults = dict(
            customer=self.customer,
            amount=10,
            site=self.site,
        )
        defaults.update(kwargs)
        return CreditLog.objects.create(**defaults)

    def test_get_description_subscription_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.SUBSCRIPTION,
            description=None,
        )

        self.assertIn("Subscription", log.get_description())

    def test_get_description_credit_purchase(self):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=9.99,
            site=self.site,
        )

        log = self._make_log(
            object_id=purchase.id,
            object_type=ObjectType.CREDIT_PURCHASE,
            description=None,
        )

        self.assertIn(self.plan.name, log.get_description())

    def test_get_description_credit_purchase_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.CREDIT_PURCHASE,
            description=None,
        )

        self.assertIn("Credit", log.get_description())

    def test_get_description_bonus(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.BONUS,
            description=None,
        )

        self.assertIn("Bonus", log.get_description())

    def test_get_description_voucher_with_plan(self):
        log = self._make_log(
            object_id=self.plan.id,
            object_type=ObjectType.VOUCHER,
            description=None,
        )

        self.assertIn(self.plan.name, log.get_description())

    def test_get_description_voucher_missing_plan(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.VOUCHER,
            description=None,
        )

        self.assertIn("Voucher", log.get_description())

    def test_get_description_voucher_no_object_id(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.VOUCHER,
            description=None,
        )

        self.assertIn("Voucher", log.get_description())

    def test_get_description_general(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.GENERAL,
            description=None,
        )

        self.assertIn("General", log.get_description())

    def test_get_description_empty_object_type(self):
        log = self._make_log(
            object_id=0,
            object_type="",
            description=None,
        )

        self.assertEqual(log.get_description(), "")

    def test_get_description_with_refund(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.BONUS,
            description=None,
            is_refund=True,
        )

        result = log.get_description()
        self.assertIn("Bonus", result)

    def test_get_image_url_subscription(self):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        log = self._make_log(
            object_id=subscription.id,
            object_type=ObjectType.SUBSCRIPTION,
        )

        self.assertEqual(log.get_image_url(), self.plan.get_image_url())

    def test_get_image_url_subscription_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.SUBSCRIPTION,
        )

        self.assertEqual(log.get_image_url(), static("images/no-image-h.png"))

    def test_get_image_url_credit_purchase(self):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=9.99,
            site=self.site,
        )

        log = self._make_log(
            object_id=purchase.id,
            object_type=ObjectType.CREDIT_PURCHASE,
        )

        self.assertEqual(log.get_image_url(), self.plan.get_image_url())

    def test_get_image_url_credit_purchase_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.CREDIT_PURCHASE,
        )

        self.assertEqual(log.get_image_url(), static("images/no-image-h.png"))

    def test_get_image_url_bonus(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        self.assertEqual(log.get_image_url(), static("images/credit-bonus.png"))

    def test_get_image_url_default(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.GENERAL,
        )

        self.assertEqual(log.get_image_url(), static("images/no-image-h.png"))

    def test_get_status_subscription(self):
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        log = self._make_log(
            object_id=subscription.id,
            object_type=ObjectType.SUBSCRIPTION,
        )

        self.assertEqual(log.get_status(), SubscriptionStatus.ACTIVE.label)

    def test_get_status_subscription_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.SUBSCRIPTION,
        )

        self.assertIsNone(log.get_status())

    def test_get_status_credit_purchase(self):
        purchase = CreditPurchase.objects.create(
            customer=self.customer,
            plan=self.plan,
            currency="USD",
            price=9.99,
            status=CreditPurchaseStatus.APPROVED,
            site=self.site,
        )

        log = self._make_log(
            object_id=purchase.id,
            object_type=ObjectType.CREDIT_PURCHASE,
        )

        self.assertEqual(log.get_status(), CreditPurchaseStatus.APPROVED.label)

    def test_get_status_credit_purchase_missing(self):
        log = self._make_log(
            object_id=99999,
            object_type=ObjectType.CREDIT_PURCHASE,
        )

        self.assertIsNone(log.get_status())

    def test_get_status_default(self):
        log = self._make_log(
            object_id=0,
            object_type=ObjectType.GENERAL,
        )

        self.assertIsNone(log.get_status())
