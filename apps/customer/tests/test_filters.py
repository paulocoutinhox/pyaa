from datetime import timedelta

from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.customer.filters import CreatedAtFilter, EmailFilter, NameFilter
from apps.customer.models import Customer
from apps.site.models import Site

User = get_user_model()


# mock model admin class to simulate the admin interface
class MockModelAdmin(ModelAdmin):
    pass


class CustomerFilterTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # get current site
        self.site = Site.objects.get_current()

        # create a user for testing
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            site=self.site,
        )

        # create a customer for testing with valid fields
        self.customer = Customer.objects.create(
            user=self.user,
            site=self.site,
            language_id=1,
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

        # assert the filter does not alter the queryset
        self.assertEqual(filtered_queryset.count(), queryset.count())

    def test_created_at_filter_with_value(self):
        # setup request and model admin
        factory = RequestFactory()
        model_admin = MockModelAdmin(Customer, admin_site=None)

        # get dates for filtering
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # setup filter parameters
        date_params = {
            "created_at__range__gte": yesterday.strftime("%Y-%m-%d"),
            "created_at__range__lte": today.strftime("%Y-%m-%d"),
        }

        # create request with date parameters
        request = factory.get("/admin", date_params)

        # create filter instance - fix with proper parameter order and field_path
        field = Customer._meta.get_field("created_at")
        filter_instance = CreatedAtFilter(
            field,
            request,
            date_params,
            Customer,
            model_admin,
            "created_at",
        )

        # apply filter
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # assert the filter works correctly - should include our customer
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertTrue(filtered_queryset.filter(pk=self.customer.pk).exists())

    def test_created_at_filter_without_value(self):
        # setup request and model admin
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Customer, admin_site=None)

        # create filter instance with no date params - fix with proper parameter order and field_path
        field = Customer._meta.get_field("created_at")
        filter_instance = CreatedAtFilter(
            field,
            request,
            {},
            Customer,
            model_admin,
            "created_at",
        )

        # apply filter without values
        queryset = Customer.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)

        # assert the filter does not alter the queryset
        self.assertEqual(filtered_queryset.count(), queryset.count())
