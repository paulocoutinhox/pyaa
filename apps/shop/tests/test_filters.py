import uuid

from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.shop.enums import PlanType
from apps.shop.filters import TokenFilter
from apps.shop.models import Customer, Plan, Subscription

User = get_user_model()


class MockModelAdmin(ModelAdmin):
    pass


class TokenFilterTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/admin")
        self.model_admin = MockModelAdmin(Subscription, admin_site=None)

        self.filter_instance = TokenFilter(
            self.request, {}, Subscription, self.model_admin
        )

        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.site = Site.objects.get_current()

        self.customer = Customer.objects.create(user=self.user, language_id=1)

        self.plan = Plan.objects.create(
            site=self.site,
            name="Test Plan",
            tag="test-plan",
            plan_type=PlanType.SUBSCRIPTION,
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type="month",
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

    def test_token_filter_with_value(self):
        token = str(uuid.uuid4())

        subscription = Subscription.objects.create(
            site=self.site,
            token=token,
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: token

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset.first(), subscription)

    def test_token_filter_without_value(self):
        Subscription.objects.create(
            site=self.site,
            token=str(uuid.uuid4()),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: None

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        self.assertEqual(filtered_queryset.count(), queryset.count())

    def test_token_filter_with_empty_string(self):
        Subscription.objects.create(
            site=self.site,
            token=str(uuid.uuid4()),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: ""

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        self.assertEqual(filtered_queryset.count(), queryset.count())

    def test_token_filter_with_invalid_token(self):
        Subscription.objects.create(
            site=self.site,
            token=str(uuid.uuid4()),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: "invalid-token"

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        self.assertEqual(filtered_queryset.count(), 0)
