from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.customer.admin import CustomerAdmin
from apps.customer.models import Customer

User = get_user_model()


class MockRequest:
    pass


class CustomerAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = CustomerAdmin(Customer, self.site)
        self.request = self.factory.get("/admin")

    def test_get_queryset(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="John",
            last_name="Doe",
            mobile_phone="1234567890",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        request = MockRequest()
        queryset = self.admin.get_queryset(request)

        self.assertTrue(queryset.exists())

    def test_user_name(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="John",
            last_name="Doe",
            mobile_phone="1234567890",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        self.assertEqual(self.admin.user_name(customer), "John Doe")

    def test_user_email(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            mobile_phone="1234567890",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        self.assertEqual(self.admin.user_email(customer), "testuser@example.com")

    def test_user_is_active(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            is_active=True,
            mobile_phone="1234567890",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        self.assertTrue(self.admin.user_is_active(customer))


class CustomerAdminExtraTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = CustomerAdmin(Customer, self.admin_site)
        self.request = self.factory.get("/admin")
        self.site = Site.objects.get_current()

    def make_customer(self):
        user = User.objects.create_user(
            email="adminx@example.com",
            password="testpassword",
            first_name="Jane",
            last_name="Roe",
            cpf="52998224725",
            mobile_phone="11999999999",
            is_active=True,
            site=self.site,
        )
        return Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender="male",
        )

    def test_has_add_permission_false(self):
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_user_cpf(self):
        customer = self.make_customer()
        self.assertEqual(self.admin.user_cpf(customer), "52998224725")

    def test_user_mobile_phone(self):
        customer = self.make_customer()
        self.assertEqual(self.admin.user_mobile_phone(customer), "11999999999")

    def test_user_name_no_user(self):
        customer = self.make_customer()
        customer.user = None
        self.assertEqual(self.admin.user_name(customer), "-")

    def test_user_email_no_user(self):
        customer = self.make_customer()
        customer.user = None
        self.assertEqual(self.admin.user_email(customer), "-")

    def test_user_cpf_no_user(self):
        customer = self.make_customer()
        customer.user = None
        self.assertEqual(self.admin.user_cpf(customer), "-")

    def test_user_mobile_phone_no_user(self):
        customer = self.make_customer()
        customer.user = None
        self.assertEqual(self.admin.user_mobile_phone(customer), "-")

    def test_user_is_active_no_user(self):
        customer = self.make_customer()
        customer.user = None
        self.assertFalse(self.admin.user_is_active(customer))

    def test_get_search_results_with_term(self):
        self.make_customer()
        queryset = Customer.objects.all()
        result, use_distinct = self.admin.get_search_results(
            self.request, queryset, "Jane"
        )
        self.assertTrue(result.exists())

    def test_get_search_results_without_term(self):
        self.make_customer()
        queryset = Customer.objects.all()
        result, use_distinct = self.admin.get_search_results(self.request, queryset, "")
        self.assertEqual(result.count(), queryset.count())

    def test_save_model_new_calls_post_save(self):
        customer = self.make_customer()
        with patch("apps.customer.admin.CustomerHelper.post_save") as mock_post:
            self.admin.save_model(self.request, customer, Mock(), change=False)
            mock_post.assert_called_once_with(customer)

    def test_save_model_change_skips_post_save(self):
        customer = self.make_customer()
        with patch("apps.customer.admin.CustomerHelper.post_save") as mock_post:
            self.admin.save_model(self.request, customer, Mock(), change=True)
            mock_post.assert_not_called()
