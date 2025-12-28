from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from apps.customer.models import Customer
from apps.system_log.enums import LogLevel
from apps.system_log.helpers import SystemLogHelper
from apps.system_log.models import SystemLog

User = get_user_model()


class SystemLogHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.get_current()

    def test_create_log_basic(self):
        log = SystemLogHelper.create(
            level=LogLevel.INFO,
            description="Test log entry",
            category="test",
        )

        self.assertIsInstance(log, SystemLog)
        self.assertEqual(log.level, LogLevel.INFO)
        self.assertEqual(log.description, "Test log entry")
        self.assertEqual(log.category, "test")
        self.assertEqual(log.site, self.site)
        self.assertIsNone(log.customer)

    def test_create_log_with_customer(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        customer = Customer.objects.create(
            user=user, site=self.site, language_id=1, gender="male"
        )

        log = SystemLogHelper.create(
            level=LogLevel.ERROR,
            description="Error log with customer",
            category="error",
            customer=customer,
        )

        self.assertEqual(log.customer, customer)
        self.assertEqual(log.level, LogLevel.ERROR)

    def test_create_log_with_specific_site(self):
        other_site = Site.objects.create(name="Other Site", domain="other.com")

        log = SystemLogHelper.create(
            level=LogLevel.WARNING,
            description="Log for specific site",
            site=other_site,
        )

        self.assertEqual(log.site, other_site)
        self.assertEqual(log.level, LogLevel.WARNING)

    def test_create_log_without_category(self):
        log = SystemLogHelper.create(
            level=LogLevel.DEBUG,
            description="Debug log without category",
        )

        self.assertIsNone(log.category)
        self.assertEqual(log.level, LogLevel.DEBUG)
