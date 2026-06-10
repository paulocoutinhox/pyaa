from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from apps.newsletter.admin import NewsletterEntryAdmin
from apps.newsletter.models import NewsletterEntry


class NewsletterEntryAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = NewsletterEntryAdmin(NewsletterEntry, self.admin_site)
        self.request = self.factory.get("/admin")

    def test_add_permission_is_denied(self):
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_change_permission_is_denied(self):
        self.assertFalse(self.admin.has_change_permission(self.request))

    def test_export_as_csv_returns_csv_response(self):
        NewsletterEntry.objects.create(email="first@example.com")
        NewsletterEntry.objects.create(email="second@example.com")

        queryset = NewsletterEntry.objects.all()
        response = self.admin.export_as_csv(self.request, queryset)

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])

        content = response.content.decode("utf-8")
        self.assertIn("first@example.com", content)
        self.assertIn("second@example.com", content)
        self.assertIn("id,email,created_at", content)
