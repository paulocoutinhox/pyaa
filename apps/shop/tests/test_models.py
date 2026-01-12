from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from apps.customer.models import Customer
from apps.language.models import Language
from apps.shop.enums import ObjectType, PlanFrequencyType, PlanType, SubscriptionStatus
from apps.shop.models import CreditLog, EventLog, Plan, Subscription

User = get_user_model()


class PlanModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)

    def test_plan_creation(self):
        Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.DAY,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.WEEK,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.QUARTER,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.SEMI_ANNUAL,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
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
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.YEAR,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )
        self.assertEqual(plan.get_frequency_in_days(), 365)

        plan.frequency_amount = 2
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 730)

        plan.frequency_amount = 3
        plan.save()
        self.assertEqual(plan.get_frequency_in_days(), 1095)

    def test_plan_with_language(self):
        language = Language.objects.create(
            name="Portuguese",
            native_name="Português",
            code_iso_639_1="pt",
            code_iso_language="pt-br",
        )

        plan = Plan.objects.create(
            name="Plan with Language",
            tag="plan-with-language",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.CREDIT_PURCHASE,
            description="Test plan with language",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
            language=language,
        )

        self.assertEqual(plan.language, language)
        self.assertEqual(plan.language.code_iso_language, "pt-br")

    def test_plan_without_language(self):
        plan = Plan.objects.create(
            name="Plan without Language",
            tag="plan-without-language",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.CREDIT_PURCHASE,
            description="Test plan without language",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

        self.assertIsNone(plan.language)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(name="English")

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        self.assertTrue(Subscription.objects.filter(token=subscription.token).exists())

    def test_subscription_deletion(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        subscription.delete()

        self.assertFalse(Subscription.objects.filter(token=subscription.token).exists())

    def test_get_subscription(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        fetched_subscription = Subscription.objects.get(token=subscription.token)

        self.assertEqual(fetched_subscription.token, subscription.token)

    def test_subscription_str(self):
        token = str(uuid4())
        subscription = Subscription.objects.create(
            token=token,
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        self.assertIsNotNone(str(subscription))

    def test_process_completed(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.INITIAL,
            site=self.site,
        )

        subscription.process_completed()
        self.customer.refresh_from_db()

        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(self.customer.credits, self.plan.credits)

    def test_process_refunded(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        self.customer.credits = self.plan.credits
        self.customer.save()

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.credits, self.plan.credits)

        subscription.process_refunded()
        self.customer.refresh_from_db()

        self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)
        self.assertEqual(self.customer.credits, self.plan.credits)

    def test_process_canceled(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        subscription.process_canceled()

        self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)

    def test_update_status(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.INITIAL,
            site=self.site,
        )

        subscription.update_status(SubscriptionStatus.ACTIVE)

        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)

    def test_can_be_canceled(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        self.assertTrue(subscription.can_be_canceled())

        subscription.update_status(SubscriptionStatus.CANCELED)

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
                name=f"Test Plan {frequency_type}",
                tag=f"test-plan-{frequency_type}",
                gateway="stripe",
                currency="USD",
                price=9.99,
                credits=10,
                plan_type=PlanType.SUBSCRIPTION,
                frequency_type=frequency_type,
                frequency_amount=frequency_amount,
                description="Test plan description",
                sort_order=1,
                featured=True,
                active=True,
                site=self.site,
            )

            subscription = Subscription.objects.create(
                token=str(uuid4()),
                customer=self.customer,
                plan=plan,
                status=SubscriptionStatus.INITIAL,
                site=self.site,
            )

            current_time = timezone.now()
            subscription.process_completed()
            subscription.refresh_from_db()

            self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
            self.assertIsNotNone(subscription.expire_at)
            self.assertAlmostEqual(
                subscription.expire_at,
                current_time + expected_timedelta,
                delta=timedelta(seconds=1),
            )

    def test_process_completed_with_existing_expiration(self):
        plan = Plan.objects.create(
            name="Test Plan With Expiration",
            tag="test-plan-expiration",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=plan,
            status=SubscriptionStatus.INITIAL,
            expire_at=timezone.now() + timedelta(days=30),
            site=self.site,
        )

        current_expire_at = subscription.expire_at
        subscription.process_completed()
        subscription.refresh_from_db()

        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertIsNotNone(subscription.expire_at)
        self.assertAlmostEqual(
            subscription.expire_at,
            current_expire_at + timedelta(days=30),
            delta=timedelta(seconds=1),
        )

    def test_process_refunded_resets_expiration(self):
        plan = Plan.objects.create(
            name="Test Plan Refund",
            tag="test-plan-refund",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() + timedelta(days=30),
            site=self.site,
        )

        current_expire_at = subscription.expire_at
        subscription.process_refunded()
        subscription.refresh_from_db()

        self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)
        self.assertIsNotNone(subscription.expire_at)
        self.assertAlmostEqual(
            subscription.expire_at,
            current_expire_at - timedelta(days=30),
            delta=timedelta(seconds=1),
        )

    def test_is_expired_with_future_expiration(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() + timedelta(days=30),
            site=self.site,
        )

        self.assertFalse(subscription.is_expired())

    def test_is_expired_with_past_expiration(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=timezone.now() - timedelta(days=1),
            site=self.site,
        )

        self.assertTrue(subscription.is_expired())

    def test_is_expired_with_null_expiration(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            expire_at=None,
            site=self.site,
        )

        self.assertFalse(subscription.is_expired())


class CreditLogModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(
            name="English",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
            gender="male",
        )

        self.plan = Plan.objects.create(
            name="Test Plan",
            tag="test-plan",
            gateway="stripe",
            currency="USD",
            price=9.99,
            credits=10,
            plan_type=PlanType.SUBSCRIPTION,
            frequency_type=PlanFrequencyType.MONTH,
            frequency_amount=1,
            description="Test plan description",
            sort_order=1,
            featured=True,
            active=True,
            site=self.site,
        )

    def test_credit_log_creation(self):
        credit_log = CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100,
            description="Test credit log",
            customer=self.customer,
            site=self.site,
        )

        self.assertTrue(
            CreditLog.objects.filter(description="Test credit log").exists()
        )

    def test_credit_log_deletion(self):
        credit_log = CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100,
            description="Test credit log",
            customer=self.customer,
            site=self.site,
        )

        credit_log.delete()

        self.assertFalse(
            CreditLog.objects.filter(description="Test credit log").exists()
        )

    def test_get_credit_log(self):
        CreditLog.objects.create(
            object_id=1,
            object_type=ObjectType.GENERAL,
            amount=100,
            description="Test credit log",
            customer=self.customer,
            site=self.site,
        )

        fetched_credit_log = CreditLog.objects.get(description="Test credit log")

        self.assertEqual(fetched_credit_log.description, "Test credit log")

    def test_get_description(self):
        credit_log = CreditLog.objects.create(
            object_id=0,
            object_type=ObjectType.UNKNOWN,
            amount=100,
            description="Test credit log",
            customer=self.customer,
            site=self.site,
        )

        self.assertEqual("Test credit log", credit_log.get_description())

    def test_get_description_for_subscription(self):
        subscription = Subscription.objects.create(
            token=str(uuid4()),
            customer=self.customer,
            plan=self.plan,
            status=SubscriptionStatus.ACTIVE,
            site=self.site,
        )

        credit_log = CreditLog.objects.create(
            object_id=subscription.id,
            object_type=ObjectType.SUBSCRIPTION,
            amount=100,
            description=None,
            customer=self.customer,
            site=self.site,
        )

        description = credit_log.get_description()
        self.assertIn(self.plan.name, description)

    def test_get_description_default_return(self):
        credit_log = CreditLog.objects.create(
            object_id=999,
            object_type=ObjectType.UNKNOWN,
            amount=100,
            customer=self.customer,
            site=self.site,
        )

        self.assertIn("Unknown", credit_log.get_description())


class EventLogModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.language = Language.objects.create(
            name="English",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            language=self.language,
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
            site=self.site,
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
            site=self.site,
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
            site=self.site,
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
            site=self.site,
        )

        event_log.save()

        self.assertEqual(event_log.currency, "USD")
