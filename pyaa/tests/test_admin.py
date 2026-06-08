from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.banner.models import Banner
from apps.content.models import Content
from pyaa.admin import AppAdmin, site
from pyaa.forms import AdminAuthenticationFormWithCaptcha

User = get_user_model()


class AppAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AppAdmin()
        # register a grouped app model (content -> site-content group) and an
        # ungrouped one (banner) so both branches of get_app_list run
        self.admin_site.register(Content)
        self.admin_site.register(Banner)
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="secret",
            email="admin@example.com",
        )

    def _request(self):
        request = self.factory.get("/admin/")
        request.user = self.superuser
        return request

    def test_grouped_apps_appear_first(self):
        request = self._request()
        app_list = self.admin_site.get_app_list(request)

        self.assertTrue(len(app_list) > 0)

        # the site-content group should be present and ordered before
        # ungrouped apps
        group_labels = [app["app_label"] for app in app_list]
        self.assertIn("site-content", group_labels)
        self.assertEqual(app_list[0]["app_label"], "site-content")

    def test_grouped_app_labels_removed_from_general_list(self):
        request = self._request()
        app_list = self.admin_site.get_app_list(request)

        # grouped app labels should not appear as standalone top-level apps
        labels = [app["app_label"] for app in app_list]
        for grouped in ["content", "gallery", "language"]:
            self.assertNotIn(grouped, labels)

    def test_group_collects_models_from_member_apps(self):
        request = self._request()
        app_list = self.admin_site.get_app_list(request)

        group = next(app for app in app_list if app["app_label"] == "site-content")
        self.assertIsInstance(group["models"], list)
        # content is registered and belongs to the site-content group
        model_names = [m["object_name"] for m in group["models"]]
        self.assertIn("Content", model_names)

    def test_filter_by_group_label(self):
        request = self._request()
        app_list = self.admin_site.get_app_list(request, app_label="site-content")

        self.assertEqual(len(app_list), 1)
        self.assertEqual(app_list[0]["app_label"], "site-content")

    def test_filter_by_specific_app_label(self):
        request = self._request()
        app_list = self.admin_site.get_app_list(request, app_label="banner")

        # only banner app should be returned, no groups
        labels = [app["app_label"] for app in app_list]
        self.assertNotIn("site-content", labels)
        for app in app_list:
            self.assertEqual(app["app_label"].lower(), "banner")


class AdminSiteConfigTest(TestCase):
    def test_module_site_is_app_admin_instance(self):
        self.assertIsInstance(site, AppAdmin)

    def test_default_admin_site_uses_captcha_login_form(self):
        self.assertIs(admin.AdminSite.login_form, AdminAuthenticationFormWithCaptcha)
