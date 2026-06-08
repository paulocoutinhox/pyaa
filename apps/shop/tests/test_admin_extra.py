from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.admin import (
    CreditLogAdmin,
    CreditPurchaseAdmin,
    EventLogAdmin,
    PlanAdmin,
    ProductAdmin,
    ProductFileInline,
    ProductPurchaseAdmin,
    ShopCreditPurchaseEventLogInlineAdmin,
    ShopProductPurchaseEventLogInlineAdmin,
    SubscriptionAdmin,
)
from apps.shop.enums import ObjectType, PlanFrequencyType, PlanType
from apps.shop.models import (
    CreditLog,
    CreditPurchase,
    EventLog,
    Plan,
    Product,
    ProductFile,
    ProductPurchase,
    Subscription,
)

User = get_user_model()


class MockModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = 1


class PlanAdminExtraTest(TestCase):
    def setUp(self):
        self.admin = PlanAdmin(Plan, AdminSite())

    def test_formatted_price_with_currency(self):
        obj = MockModel(price=9.99, currency="USD")

        self.assertIsNotNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_price(self):
        obj = MockModel(price=None, currency="USD")

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_currency(self):
        obj = MockModel(price=9.99, currency=None)

        self.assertEqual(self.admin.formatted_price(obj), 9.99)


class SubscriptionAdminFormattedPriceTest(TestCase):
    def setUp(self):
        self.admin = SubscriptionAdmin(Subscription, AdminSite())

    def test_formatted_price_no_plan(self):
        obj = MockModel(plan=None)

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_with_currency(self):
        obj = MockModel(plan=MockModel(price=9.99, currency="USD"))

        self.assertIsNotNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_price(self):
        obj = MockModel(plan=MockModel(price=None, currency="USD"))

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_currency(self):
        obj = MockModel(plan=MockModel(price=9.99, currency=None))

        self.assertEqual(self.admin.formatted_price(obj), 9.99)


class CreditPurchaseAdminFormattedPriceTest(TestCase):
    def setUp(self):
        self.admin = CreditPurchaseAdmin(CreditPurchase, AdminSite())

    def test_formatted_price_with_currency(self):
        obj = MockModel(price=9.99, currency="USD")

        self.assertIsNotNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_price(self):
        obj = MockModel(price=None, currency="USD")

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_currency(self):
        obj = MockModel(price=9.99, currency=None)

        self.assertEqual(self.admin.formatted_price(obj), 9.99)


class ProductAdminFormattedPriceTest(TestCase):
    def setUp(self):
        self.admin = ProductAdmin(Product, AdminSite())

    def test_formatted_price_with_currency(self):
        obj = MockModel(price=9.99, currency="USD")

        self.assertIsNotNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_price(self):
        obj = MockModel(price=None, currency="USD")

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_currency(self):
        obj = MockModel(price=9.99, currency=None)

        self.assertEqual(self.admin.formatted_price(obj), 9.99)


class ProductPurchaseAdminFormattedPriceTest(TestCase):
    def setUp(self):
        self.admin = ProductPurchaseAdmin(ProductPurchase, AdminSite())

    def test_formatted_price_with_currency(self):
        obj = MockModel(price=9.99, currency="USD")

        self.assertIsNotNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_price(self):
        obj = MockModel(price=None, currency="USD")

        self.assertIsNone(self.admin.formatted_price(obj))

    def test_formatted_price_no_currency(self):
        obj = MockModel(price=9.99, currency=None)

        self.assertEqual(self.admin.formatted_price(obj), 9.99)


class EventLogAdminFormattedAmountTest(TestCase):
    def setUp(self):
        self.admin = EventLogAdmin(EventLog, AdminSite())

    def test_formatted_amount_with_currency(self):
        obj = MockModel(amount=9.99, currency="USD")

        self.assertIsNotNone(self.admin.formatted_amount(obj))

    def test_formatted_amount_no_amount(self):
        obj = MockModel(amount=None, currency="USD")

        self.assertIsNone(self.admin.formatted_amount(obj))

    def test_formatted_amount_no_currency(self):
        obj = MockModel(amount=9.99, currency=None)

        self.assertEqual(self.admin.formatted_amount(obj), 9.99)


class CreditLogAdminAmountBadgeTest(TestCase):
    def setUp(self):
        self.admin = CreditLogAdmin(CreditLog, AdminSite())

    def test_amount_badge_positive(self):
        obj = MockModel(amount=100)

        badge = self.admin.amount_badge(obj)
        self.assertIn("+100", badge)
        self.assertIn("#22c55e", badge)

    def test_amount_badge_negative(self):
        obj = MockModel(amount=-50)

        badge = self.admin.amount_badge(obj)
        self.assertIn("-50", badge)
        self.assertIn("#ef4444", badge)

    def test_amount_badge_zero(self):
        obj = MockModel(amount=0)

        badge = self.admin.amount_badge(obj)
        self.assertIn("0", badge)
        self.assertIn("#6b7280", badge)

    def test_amount_badge_none(self):
        obj = MockModel(amount=None)

        self.assertIsNone(self.admin.amount_badge(obj))


class CreditLogAdminSaveModelTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = CreditLogAdmin(CreditLog, AdminSite())
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="savemodel@example.com",
            password="testpassword",
            site=self.site,
        )
        self.language = Language.objects.create(name="English")
        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )

    def test_save_model_create_updates_credits(self):
        request = self.factory.post("/admin")
        request.user = self.user

        credit_log = CreditLog(
            customer=self.customer,
            object_id=0,
            object_type=ObjectType.GENERAL,
            amount=25,
            site=self.site,
        )

        with mock.patch(
            "apps.shop.admin.CustomerHelper.update_customer_credits"
        ) as mock_update:
            self.admin.save_model(request, credit_log, None, change=False)

        mock_update.assert_called_once_with(self.customer.id, 25)
        self.assertTrue(CreditLog.objects.filter(id=credit_log.id).exists())

    def test_save_model_change_does_not_update_credits(self):
        request = self.factory.post("/admin")
        request.user = self.user

        credit_log = CreditLog.objects.create(
            customer=self.customer,
            object_id=0,
            object_type=ObjectType.GENERAL,
            amount=25,
            site=self.site,
        )

        with mock.patch(
            "apps.shop.admin.CustomerHelper.update_customer_credits"
        ) as mock_update:
            self.admin.save_model(request, credit_log, None, change=True)

        mock_update.assert_not_called()


class CreditPurchaseInlineQuerysetTest(TestCase):
    @mock.patch("apps.shop.admin.models.EventLog.objects.filter")
    def test_get_nonrelated_queryset(self, mock_filter):
        admin = ShopCreditPurchaseEventLogInlineAdmin(EventLog, AdminSite())
        obj = MockModel(id=7)

        mock_queryset = mock.MagicMock()
        mock_queryset.order_by.return_value = ["item"]
        mock_filter.return_value = mock_queryset

        result = admin.get_nonrelated_queryset(obj)

        mock_filter.assert_called_with(
            object_type=ObjectType.CREDIT_PURCHASE, object_id=obj.id
        )
        self.assertEqual(result, ["item"])

    def test_get_form_queryset(self):
        admin = ShopCreditPurchaseEventLogInlineAdmin(EventLog, AdminSite())

        with mock.patch.object(admin, "get_nonrelated_queryset") as mock_method:
            mock_method.return_value = ["x"]
            self.assertEqual(admin.get_form_queryset(MockModel(id=1)), ["x"])


class ProductPurchaseInlineQuerysetTest(TestCase):
    @mock.patch("apps.shop.admin.models.EventLog.objects.filter")
    def test_get_nonrelated_queryset(self, mock_filter):
        admin = ShopProductPurchaseEventLogInlineAdmin(EventLog, AdminSite())
        obj = MockModel(id=9)

        mock_queryset = mock.MagicMock()
        mock_queryset.order_by.return_value = ["item"]
        mock_filter.return_value = mock_queryset

        result = admin.get_nonrelated_queryset(obj)

        mock_filter.assert_called_with(
            object_type=ObjectType.PRODUCT_PURCHASE, object_id=obj.id
        )
        self.assertEqual(result, ["item"])

    def test_get_form_queryset(self):
        admin = ShopProductPurchaseEventLogInlineAdmin(EventLog, AdminSite())

        with mock.patch.object(admin, "get_nonrelated_queryset") as mock_method:
            mock_method.return_value = ["x"]
            self.assertEqual(admin.get_form_queryset(MockModel(id=1)), ["x"])


class ProductFileInlineTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ProductFileInline(Product, AdminSite())
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_superuser(
            username="inlineuser",
            email="inline@example.com",
            password="testpassword",
        )
        self.product = Product.objects.create(
            name="Inline Product",
            slug="inline-product",
            currency="USD",
            price=10.00,
            site=self.site,
        )

    def test_clean_file_sets_metadata_on_new_file(self):
        request = self.factory.get("/admin")
        request.user = self.user
        formset = self.admin.get_formset(request)
        form_class = formset.form

        uploaded = mock.MagicMock()
        uploaded.content_type = "application/pdf"
        uploaded.size = 1234

        form = form_class()
        form.cleaned_data = {"file": uploaded}
        form.changed_data = ["file"]

        result = form.clean_file()

        self.assertEqual(result, uploaded)
        self.assertEqual(form.instance.file_type, "application/pdf")
        self.assertEqual(form.instance.file_size, 1234)

    def test_clean_file_no_file(self):
        request = self.factory.get("/admin")
        request.user = self.user
        formset = self.admin.get_formset(request)
        form_class = formset.form

        form = form_class()
        form.cleaned_data = {"file": None}

        result = form.clean_file()

        self.assertIsNone(result)

    def test_clean_file_without_metadata_attrs(self):
        # a stored file without content_type/size attributes should be returned as-is
        request = self.factory.get("/admin")
        request.user = self.user
        formset = self.admin.get_formset(request)
        form_class = formset.form

        existing_file = "files/product/existing.pdf"

        form = form_class()
        form.cleaned_data = {"file": existing_file}

        result = form.clean_file()

        self.assertEqual(result, existing_file)
