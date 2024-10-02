from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.customer.filters import EmailFilter, NameFilter
from apps.customer.models import Customer

User = get_user_model()


# mock model admin class to simulate the admin interface
class MockModelAdmin(ModelAdmin):
    pass


class CustomerFilterTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # create a user for testing
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        # create a customer for testing
        self.customer = Customer.objects.create(
            user=self.user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

    def test_name_filter_with_value(self):
        # setup request and model admin
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Customer, admin_site=None)
        filter_instance = NameFilter(request, {}, Customer, model_admin)

        # apply filter with a value
        filter_instance.value = lambda: "Test"
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # assert the filter works correctly
        self.assertTrue(filtered_queryset.filter(user__first_name="Test").exists())

    def test_name_filter_without_value(self):
        # setup request and model admin
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Customer, admin_site=None)
        filter_instance = NameFilter(request, {}, Customer, model_admin)

        # apply filter without a value
        filter_instance.value = lambda: None
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # handle case where filter returns None
        if filtered_queryset is None:
            filtered_queryset = queryset

        # assert the filter does not alter the queryset
        self.assertEqual(filtered_queryset.count(), queryset.count())

    def test_email_filter_with_value(self):
        # setup request and model admin
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Customer, admin_site=None)
        filter_instance = EmailFilter(request, {}, Customer, model_admin)

        # apply filter with a value
        filter_instance.value = lambda: "testuser@example.com"
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # assert the filter works correctly
        self.assertTrue(
            filtered_queryset.filter(user__email="testuser@example.com").exists()
        )

    def test_email_filter_without_value(self):
        # setup request and model admin
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Customer, admin_site=None)
        filter_instance = EmailFilter(request, {}, Customer, model_admin)

        # apply filter without a value
        filter_instance.value = lambda: None
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # handle case where filter returns None
        if filtered_queryset is None:
            filtered_queryset = queryset

        # assert the filter does not alter the queryset
        self.assertEqual(filtered_queryset.count(), queryset.count())
