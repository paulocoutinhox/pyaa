from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.enums import ObjectType, PlanFrequencyType
from apps.shop.models import CreditLog, EventLog, Plan, Subscription

User = get_user_model()


class PlanModelTest(TestCase):
    def test_plan_creation(self):
        Plan.objects.create(
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

        self.assertTrue(Plan.objects.filter(name="Test Plan").exists())

    def test_plan_deletion(self):
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

        plan.delete()

        self.assertFalse(Plan.objects.filter(name="Test Plan").exists())

    def test_get_plan(self):
        Plan.objects.create(
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

        fetched_plan = Plan.objects.get(name="Test Plan")

        self.assertEqual(fetched_plan.name, "Test Plan")

    def test_plan_clean(self):
        plan = Plan(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="usd",
            price=9.99,
            credits=10,
            frequency_type="monthly",
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        plan.clean()

        self.assertEqual(plan.currency, "USD")

    def test_plan_save(self):
        plan = Plan(
            name="Test Plan",
            gateway="stripe",
            currency="usd",
            price=9.99,
            credits=10,
            frequency_type="monthly",
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        plan.save()

        self.assertEqual(plan.currency, "USD")
        self.assertEqual(plan.tag, slugify(plan.name))

    def test_plan_str(self):
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

        self.assertEqual(str(plan), "Test Plan")

    def test_plan_frequency_in_days_for_daily(self):
        plan = Plan.objects.create(
            name="Daily Plan",
            tag="daily-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.DAY,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 1)

        plan.frequency_amount = 5
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 5)

        plan.frequency_amount = 10
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 10)

    def test_plan_frequency_in_days_for_weekly(self):
        plan = Plan.objects.create(
            name="Weekly Plan",
            tag="weekly-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.WEEK,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 7)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 14)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 21)

    def test_plan_frequency_in_days_for_monthly(self):
        plan = Plan.objects.create(
            name="Monthly Plan",
            tag="monthly-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 30)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 60)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 90)

    def test_plan_frequency_in_days_for_quarterly(self):
        plan = Plan.objects.create(
            name="Quarterly Plan",
            tag="quarterly-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.QUARTER,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 90)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 180)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 270)

    def test_plan_frequency_in_days_for_semi_annual(self):
        plan = Plan.objects.create(
            name="Semi-Annual Plan",
            tag="semi-annual-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.SEMI_ANNUAL,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 182)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 364)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 546)

    def test_plan_frequency_in_days_for_yearly(self):
        plan = Plan.objects.create(
            name="Yearly Plan",
            tag="yearly-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.YEAR,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )
        self.assertEqual(plan.get_frequency_in_days(), 365)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 730)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 1095)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(name="English")

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

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

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.assertTrue(Subscription.objects.filter(token=subscription.token).exists())

    def test_subscription_deletion(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        subscription.delete()

        self.assertFalse(Subscription.objects.filter(token=subscription.token).exists())

    def test_get_subscription(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        fetched_subscription = Subscription.objects.get(token=subscription.token)

        self.assertEqual(fetched_subscription.token, subscription.token)

    def test_subscription_str(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.assertEqual(str(subscription), str(subscription.token))

    def test_process_completed(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="initial",
        )

        subscription.process_completed()
        self.customer.refresh_from_db()

        self.assertEqual(subscription.status, "active")
        self.assertEqual(self.customer.credits, self.plan.credits)

    def test_process_refunded(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.customer, _ = CustomerHelper.add_credits(
            self.customer,
            self.plan.credits,
            True,
            0,
            ObjectType.GENERAL,
        )

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.credits, self.plan.credits)

        subscription.process_refunded()
        self.customer.refresh_from_db()

        self.assertEqual(subscription.status, "canceled")
        self.assertEqual(self.customer.credits, 0)

    def test_process_canceled(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        subscription.process_canceled()

        self.assertEqual(subscription.status, "canceled")

    def test_update_status(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="initial",
        )

        subscription.update_status("active")

        self.assertEqual(subscription.status, "active")

    def test_can_be_canceled(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        self.assertTrue(subscription.can_be_canceled())

        subscription.update_status("canceled")

        self.assertFalse(subscription.can_be_canceled())

    def test_process_completed_with_expiration(self):
        test_cases = [
            (PlanFrequencyType.DAY, 1, timedelta(days=1)),
            (PlanFrequencyType.WEEK, 2, timedelta(weeks=2)),
            (PlanFrequencyType.MONTH, 3, timedelta(days=90)),
            (PlanFrequencyType.YEAR, 1, timedelta(days=365)),
        ]

        for frequency_type, frequency_amount, expected_timedelta in test_cases:
            plan = Plan.objects.create(
                name="Test Plan",
                tag="test-plan",
                gateway="stripe",
                currency="USD",
                price=9.99,
                credits=10,
                frequency_type=frequency_type,
                frequency_amount=frequency_amount,
                description="Test plan description",
                sort_order=1,
                featured=True,
                active=True,
            )

            subscription = Subscription.objects.create(
                token=uuid4(),
                customer=self.customer,
                plan=plan,
                status="initial",
            )

            current_time = timezone.now()
            subscription.process_completed()
            subscription.refresh_from_db()

            self.assertEqual(subscription.status, "active")
            self.assertIsNotNone(subscription.expire_at)
            self.assertAlmostEqual(
                subscription.expire_at,
                current_time + expected_timedelta,
                delta=timedelta(seconds=1),
            )

    def test_process_completed_with_existing_expiration(self):
        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=plan,
            status="initial",
            expire_at=timezone.now() + timedelta(days=30),
        )

        current_expire_at = subscription.expire_at
        subscription.process_completed()
        subscription.refresh_from_db()

        self.assertEqual(subscription.status, "active")
        self.assertIsNotNone(subscription.expire_at)
        self.assertAlmostEqual(
            subscription.expire_at,
            current_expire_at + timedelta(days=30),
            delta=timedelta(seconds=1),
        )

    def test_process_refunded_resets_expiration(self):
        plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
        )

        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=plan,
            status="active",
            expire_at=timezone.now() + timedelta(days=30),
        )

        current_expire_at = subscription.expire_at
        subscription.process_refunded()
        subscription.refresh_from_db()

        self.assertEqual(subscription.status, "canceled")
        self.assertIsNotNone(subscription.expire_at)
        self.assertAlmostEqual(
            subscription.expire_at,
            current_expire_at - timedelta(days=30),
            delta=timedelta(seconds=1),
        )

    def test_is_expired_with_future_expiration(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
            expire_at=timezone.now() + timedelta(days=30),
        )

        self.assertFalse(subscription.is_expired())

    def test_is_expired_with_past_expiration(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
            expire_at=timezone.now() - timedelta(days=1),
        )

        self.assertTrue(subscription.is_expired())

    def test_is_expired_with_null_expiration(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
            expire_at=None,
        )

        self.assertFalse(subscription.is_expired())


class CreditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(
            name="English",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

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

    def test_credit_log_creation(self):
        CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100.0,
            description="Test credit log",
            customer=self.customer,
        )

        self.assertTrue(
            CreditLog.objects.filter(description="Test credit log").exists()
        )

    def test_credit_log_deletion(self):
        credit_log = CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100.0,
            description="Test credit log",
            customer=self.customer,
        )

        credit_log.delete()

        self.assertFalse(
            CreditLog.objects.filter(description="Test credit log").exists()
        )

    def test_get_credit_log(self):
        CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100.0,
            description="Test credit log",
            customer=self.customer,
        )

        fetched_credit_log = CreditLog.objects.get(description="Test credit log")

        self.assertEqual(fetched_credit_log.description, "Test credit log")

    def test_get_description(self):
        credit_log = CreditLog.objects.create(
            object_id=0,
            object_type=ObjectType.UNKNOWN,
            amount=100.0,
            description="Test credit log",
            customer=self.customer,
        )

        self.assertEqual("Test credit log", credit_log.get_description())

    def test_get_description_for_subscription(self):
        subscription = Subscription.objects.create(
            token=uuid4(),
            customer=self.customer,
            plan=self.plan,
            status="active",
        )

        credit_log = CreditLog.objects.create(
            object_id=subscription.id,
            object_type=ObjectType.SUBSCRIPTION,
            amount=100.0,
            description="Test credit log",
            customer=self.customer,
        )

        self.assertIn("Test Plan", credit_log.get_description())

    def test_get_description_default_return(self):
        credit_log = CreditLog.objects.create(
            object_id=999,
            object_type=ObjectType.UNKNOWN,
            amount=100.0,
            customer=self.customer,
        )

        self.assertIn("Unknown", credit_log.get_description())


class EventLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(
            name="English",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

    def test_event_log_creation(self):
        EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=self.customer,
        )

        self.assertTrue(EventLog.objects.filter(description="Test event log").exists())

    def test_event_log_deletion(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=self.customer,
        )

        event_log.delete()

        self.assertFalse(EventLog.objects.filter(description="Test event log").exists())

    def test_get_event_log(self):
        EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=self.customer,
        )

        fetched_event_log = EventLog.objects.get(description="Test event log")

        self.assertEqual(fetched_event_log.description, "Test event log")

    def test_event_log_save(self):
        event_log = EventLog(
            object_id=1,
            object_type=ObjectType.GENERAL,
            status="completed",
            currency="usd",
            amount=100.0,
            description="Test event log",
            customer=self.customer,
        )

        event_log.save()

        self.assertEqual(event_log.currency, "USD")
