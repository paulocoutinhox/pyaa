from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.site.admin import SiteProfileAdmin
from apps.site.models import SiteProfile


class SiteProfileAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = SiteProfileAdmin(SiteProfile, self.admin_site)
        self.request = self.factory.get("/admin")
        self.site = Site.objects.create(name="Example", domain="profile.example.com")
        self.profile = SiteProfile.objects.create(site=self.site, title="Title")

    def test_readonly_fields_without_object(self):
        readonly = self.admin.get_readonly_fields(self.request)
        self.assertIn("site", readonly)
        self.assertIn("created_at", readonly)
        self.assertIn("updated_at", readonly)

    def test_readonly_fields_with_object(self):
        admin = SiteProfileAdmin(SiteProfile, AdminSite())
        readonly = admin.get_readonly_fields(self.request, self.profile)
        link_field = readonly[-1]

        self.assertTrue(callable(link_field))
        self.assertEqual(
            link_field.short_description,
            SiteProfile._meta.get_field("site").verbose_name,
        )

    def test_get_form_removes_link_field(self):
        form = self.admin.get_form(self.request, self.profile)
        self.assertNotIn("site", form.base_fields)
