from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from apps.customer.models import Customer
from apps.shop.enums import SubscriptionStatus
from apps.shop.models import Plan, Subscription

User = get_user_model()


class CustomerModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_customer_creation(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_customer_deletion(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        customer.delete()

        self.assertFalse(
            User.objects.filter(
                email="testuser@example.com",
            ).exists()
        )

        self.assertFalse(
            Customer.objects.filter(
                user__email="testuser@example.com",
            ).exists()
        )

    def test_get_customer(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        fetched_customer = Customer.objects.get(user=user)

        self.assertEqual(fetched_customer.user.email, "testuser@example.com")

    def test_get_nonexistent_customer(self):
        with self.assertRaises(ObjectDoesNotExist):
            Customer.objects.get(user__email="nonexistent@example.com")

    def test_customer_str_with_full_name(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        self.assertEqual(str(customer), "John Doe")

    def test_customer_str_with_email(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        self.assertEqual(str(customer), "testuser")

    def test_customer_str_with_id(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        user.email = ""
        user.save()

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        self.assertIn("#", str(customer))

    def test_has_active_subscription_without_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_expired_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        plan = Plan.objects.create(
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

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() - timedelta(days=1),
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_active_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        plan = Plan.objects.create(
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

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() + timedelta(days=30),
        )

        self.assertTrue(customer.has_active_subscription())

    def test_has_active_subscription_with_canceled_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        plan = Plan.objects.create(
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

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.CANCELED,
            expire_at=timezone.now() + timedelta(days=30),
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_no_expiration(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        plan = Plan.objects.create(
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

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=None,
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_credits_without_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            credits=0,
        )

        self.assertFalse(customer.has_credits(1))

    def test_has_credits_with_sufficient_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            credits=10,
        )

        self.assertTrue(customer.has_credits(5))

    def test_has_credits_with_insufficient_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            credits=5,
        )

        self.assertFalse(customer.has_credits(10))
