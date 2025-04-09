from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.shop.admin import (
    BaseEventLogInlineAdmin,
    CreditLogAdmin,
    CreditPurchaseAdmin,
    EventLogAdmin,
    ProductPurchaseAdmin,
    ShopSubscriptionEventLogInlineAdmin,
    SubscriptionAdmin,
)
from apps.shop.enums import ObjectType
from apps.shop.models import CreditPurchase, EventLog, ProductPurchase, Subscription

User = get_user_model()


class MockRequest:
    path = "/admin"


class MockModel:
    """Mock model for testing without database dependencies"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = 1

    def get_status_display(self):
        return self.status


class BaseEventLogInlineAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = BaseEventLogInlineAdmin(EventLog, self.site)

    def test_init(self):
        # test that the admin is properly initialized
        self.assertEqual(self.admin.model, EventLog)
        self.assertEqual(self.admin.admin_site, self.site)
        self.assertEqual(self.admin.extra, 0)
        self.assertFalse(self.admin.can_delete)

    def test_description_modal(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
            site_id=1,
        )
        modal_html = self.admin.description_modal(event_log)
        self.assertIn("Test event log", modal_html)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_status_badge(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
            site_id=1,
        )
        badge_html = self.admin.status_badge(event_log)
        self.assertIn("completed", badge_html)
        self.assertIn("background-color", badge_html)


class ShopSubscriptionEventLogInlineAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ShopSubscriptionEventLogInlineAdmin(EventLog, self.site)

    @mock.patch("apps.shop.admin.models.EventLog.objects.filter")
    def test_get_nonrelated_queryset(self, mock_filter):
        # create a mock subscription
        subscription = MockModel(id=1)

        # set up our mock EventLog queryset
        mock_event_log = MockModel(
            id=1,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            description="Test event log",
        )
        mock_queryset = mock.MagicMock()
        mock_queryset.order_by.return_value = [mock_event_log]
        mock_filter.return_value = mock_queryset

        # run the test
        queryset = self.admin.get_nonrelated_queryset(subscription)

        # assert filter was called with correct args
        mock_filter.assert_called_with(
            object_type=ObjectType.SUBSCRIPTION, object_id=subscription.id
        )
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0], mock_event_log)

    def test_get_form_queryset(self):
        # for this test, we can just mock get_nonrelated_queryset
        with mock.patch.object(self.admin, "get_nonrelated_queryset") as mock_method:
            mock_queryset = [MockModel(id=1)]
            mock_method.return_value = mock_queryset

            result = self.admin.get_form_queryset(MockModel(id=1))
            self.assertEqual(result, mock_queryset)


class SubscriptionAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = SubscriptionAdmin(Subscription, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_status_badge(self):
        # create mock subscription to avoid db dependency
        subscription = MockModel(id=1, status="active")

        badge_html = self.admin.status_badge(subscription)
        self.assertIn("active", badge_html)
        self.assertIn("background-color", badge_html)


class EventLogAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = EventLogAdmin(EventLog, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_status_badge(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
            site_id=1,
        )
        badge_html = self.admin.status_badge(event_log)
        self.assertIn("completed", badge_html)
        self.assertIn("background-color", badge_html)


class CreditLogAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = CreditLogAdmin(EventLog, self.site)
        self.user = User.objects.create_superuser(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            first_name="John",
            last_name="Doe",
        )

    def test_has_add_permission(self):
        request = self.factory.get("/admin")
        request.user = self.user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_has_change_permission(self):
        self.assertFalse(self.admin.has_change_permission(None))


class CreditPurchaseAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = CreditPurchaseAdmin(CreditPurchase, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_status_badge(self):
        # create mock credit purchase to avoid db dependency
        credit_purchase = MockModel(id=1, status="approved")

        badge_html = self.admin.status_badge(credit_purchase)
        self.assertIn("approved", badge_html)
        self.assertIn("background-color", badge_html)


class ProductPurchaseAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ProductPurchaseAdmin(ProductPurchase, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_status_badge(self):
        # create mock product purchase to avoid db dependency
        product_purchase = MockModel(id=1, status="approved")

        badge_html = self.admin.status_badge(product_purchase)
        self.assertIn("approved", badge_html)
        self.assertIn("background-color", badge_html)
