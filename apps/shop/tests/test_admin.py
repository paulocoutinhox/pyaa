from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.shop.admin import (
    CreditLogAdmin,
    EventLogAdmin,
    ShopEventLogInlineAdmin,
    SubscriptionAdmin,
)
from apps.shop.enums import ObjectType
from apps.shop.models import EventLog, Subscription

User = get_user_model()


class MockRequest:
    path = "/admin"


class ShopEventLogInlineAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ShopEventLogInlineAdmin(EventLog, self.site)

    def test_get_nonrelated_queryset(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
        )
        queryset = self.admin.get_nonrelated_queryset(event_log)
        self.assertIn(event_log, queryset)

    def test_get_form_queryset(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
        )
        queryset = self.admin.get_form_queryset(event_log)
        self.assertIn(event_log, queryset)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))

    def test_description_modal(self):
        event_log = EventLog.objects.create(
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
            status="completed",
            currency="USD",
            amount=100.0,
            description="Test event log",
            customer=None,
        )
        modal_html = self.admin.description_modal(event_log)
        self.assertIn("Test event log", modal_html)


class SubscriptionAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = SubscriptionAdmin(Subscription, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))


class EventLogAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = EventLogAdmin(EventLog, self.site)

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(None))


class CreditLogAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = CreditLogAdmin(EventLog, self.site)
        self.user = User.objects.create_superuser(
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
