from django.contrib.sites.models import Site
from django.test import TestCase

from apps.system_log.enums import LogLevel
from apps.system_log.models import SystemLog


class SystemLogModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()

    def test_system_log_str_with_category(self):
        log = SystemLog.objects.create(
            site=self.site,
            level=LogLevel.INFO,
            description="Test log",
            category="test_category",
        )

        log_str = log.__str__()
        self.assertEqual(log_str, "info - test_category")
        self.assertEqual(str(log), "info - test_category")

    def test_system_log_str_without_category(self):
        log = SystemLog.objects.create(
            site=self.site,
            level=LogLevel.ERROR,
            description="Test error log",
            category="",
        )

        log_str = log.__str__()
        self.assertIn("No Category", log_str)
        self.assertEqual(str(log), "error - No Category")
