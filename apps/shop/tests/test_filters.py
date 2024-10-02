import uuid

from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

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

        self.customer = Customer.objects.create(user=self.user, language_id=1)

        self.plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type="monthly",
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

    def test_token_filter_with_value(self):
        token = str(uuid.uuid4())

        Subscription.objects.create(
            token=token,
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: token

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        self.assertTrue(filtered_queryset.filter(token=token).exists())

    def test_token_filter_without_value(self):
        Subscription.objects.create(
            token=str(uuid.uuid4()),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.filter_instance.value = lambda: None

        queryset = Subscription.objects.all()
        filtered_queryset = self.filter_instance.queryset(self.request, queryset)

        if filtered_queryset is None:
            filtered_queryset = queryset

        self.assertEqual(filtered_queryset.count(), queryset.count())
