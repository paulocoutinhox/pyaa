from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.system_log.admin import SystemLogAdmin
from apps.system_log.enums import LogLevel
from apps.system_log.models import SystemLog


class MockRequest:
    path = "/admin"


class SystemLogAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = SystemLogAdmin(SystemLog, AdminSite())
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.log = SystemLog.objects.create(
            site=self.site,
            level=LogLevel.ERROR,
            category="payment",
            description="something failed",
        )

    def test_has_add_permission_disabled(self):
        self.assertFalse(self.admin.has_add_permission(MockRequest()))

    def test_has_delete_permission_disabled(self):
        self.assertFalse(self.admin.has_delete_permission(MockRequest()))
        self.assertFalse(self.admin.has_delete_permission(MockRequest(), self.log))

    def test_level_badge_renders_span_with_level(self):
        html = self.admin.level_badge(self.log)
        self.assertIn("<span", html)
        self.assertIn("error", html)
        # the error level uses a red foreground color
        self.assertIn("#dc3545", html)

    def test_level_badge_for_debug_level(self):
        log = SystemLog.objects.create(
            site=self.site,
            level=LogLevel.DEBUG,
            category="general",
            description="debug message",
        )
        html = self.admin.level_badge(log)
        self.assertIn("debug", html)
