from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
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
