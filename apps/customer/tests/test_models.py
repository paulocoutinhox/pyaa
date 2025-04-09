from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from apps.customer.enums import CustomerGender
from apps.customer.models import Customer
from apps.shop.enums import PlanType, ProductPurchaseStatus, SubscriptionStatus
from apps.shop.models import Plan, Subscription
from apps.site.models import Site

User = get_user_model()


class CustomerModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()

    def test_customer_creation(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_customer_deletion(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
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
            email="testuser@example.com", password="testpassword", site=self.site
        )

        Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        fetched_customer = Customer.objects.get(user=user)

        self.assertEqual(fetched_customer.user.email, "testuser@example.com")

    def test_get_nonexistent_customer(self):
        with self.assertRaises(ObjectDoesNotExist):
            Customer.objects.get(user__email="nonexistent@example.com")

    def test_customer_str_with_full_name(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        user.first_name = "John"
        user.last_name = "Doe"
        user.save()

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        self.assertEqual(str(customer), "John Doe")

    def test_customer_str_with_email(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        self.assertEqual(str(customer), "testuser")

    def test_customer_str_with_nickname(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
            nickname="TestNick",
        )

        self.assertEqual(str(customer), "TestNick")

    def test_customer_str_with_id(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        # create a new instance that will use id in string representation
        from unittest.mock import patch

        # mock the __str__ method's dependencies without modifying the original object
        with patch.object(customer, "nickname", None):
            with patch.object(user, "get_full_name", return_value=""):
                with patch.object(user, "email", None):
                    # now the string representation should include the id
                    self.assertIn("#", str(customer))

    def test_has_active_subscription_without_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_expired_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            plan_type=PlanType.SUBSCRIPTION,
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
            site=self.site,
        )

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() - timedelta(days=1),
            site=self.site,
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_active_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            plan_type=PlanType.SUBSCRIPTION,
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
            site=self.site,
        )

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() + timedelta(days=30),
            site=self.site,
        )

        self.assertTrue(customer.has_active_subscription())

    def test_has_active_subscription_with_canceled_subscription(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            plan_type=PlanType.SUBSCRIPTION,
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
            site=self.site,
        )

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.CANCELED,
            expire_at=timezone.now() + timedelta(days=30),
            site=self.site,
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_active_subscription_with_no_expiration(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            plan_type=PlanType.SUBSCRIPTION,
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
            site=self.site,
        )

        Subscription.objects.create(
            token=uuid4(),
            customer=customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=None,
            site=self.site,
        )

        self.assertFalse(customer.has_active_subscription())

    def test_has_credits_without_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
            credits=0,
        )

        self.assertFalse(customer.has_credits(1))

    def test_has_credits_with_sufficient_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
            credits=10,
        )

        self.assertTrue(customer.has_credits(5))

    def test_has_credits_with_insufficient_credits(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
            credits=5,
        )

        self.assertFalse(customer.has_credits(10))

    def test_has_purchased_product(self):
        from apps.shop.models import Product, ProductPurchase

        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )

        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender=CustomerGender.MALE,
        )

        product = Product.objects.create(
            name="Test Product",
            price=9.99,
            active=True,
            site=self.site,
            currency="USD",
        )

        # test without a purchase
        self.assertFalse(customer.has_purchased_product(product.id))

        # create a purchase
        ProductPurchase.objects.create(
            customer=customer,
            product=product,
            status=ProductPurchaseStatus.APPROVED,
            site=self.site,
            currency="USD",
            price=product.price,
        )

        # test with a purchase
        self.assertTrue(customer.has_purchased_product(product.id))
