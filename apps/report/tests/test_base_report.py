from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.customer.enums import CustomerGender
from apps.customer.models import Customer
from apps.report.admin.base_report import BaseReportAdmin
from apps.report.mixins import DateParserMixin
from apps.report.models import CustomerGenderSummary

User = get_user_model()


class BaseReportChangelistViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()

        # create a superuser to access the admin
        self.admin_user = User.objects.create_superuser(
            username=None,
            password="adminpass",
            email="admin@example.com",
            site=self.site,
        )

        # create some customers so the reports have data
        for email, gender in [
            ("m1@example.com", CustomerGender.MALE),
            ("m2@example.com", CustomerGender.MALE),
            ("f1@example.com", CustomerGender.FEMALE),
        ]:
            user = User.objects.create_user(
                email=email, password="pass", site=self.site
            )
            Customer.objects.create(
                user=user, site=self.site, language_id=1, gender=gender
            )

        self.client.force_login(self.admin_user)

    def test_customer_gender_changelist_view(self):
        # exercises changelist_view -> generate_report_data -> generate_chart_data
        url = reverse("admin:report_customergendersummary_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context_data["has_data"])
        self.assertTrue(response.context_data["has_chart"])
        self.assertIsNotNone(response.context_data["chart_image"])
        self.assertIn("report_title", response.context_data)

    def test_customer_gender_export_to_pdf(self):
        # exercises export_to_pdf with a real weasyprint render
        url = reverse("admin:report_customergendersummary_changelist")
        response = self.client.get(url, {"export-data": "pdf"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])

    def test_banner_access_changelist_view(self):
        # banner access report has no chart
        url = reverse("admin:report_banneraccesssummary_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context_data["has_chart"])
        self.assertIsNone(response.context_data["chart_image"])

    def test_banner_access_export_to_pdf(self):
        url = reverse("admin:report_banneraccesssummary_changelist")
        response = self.client.get(url, {"export-data": "pdf"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class BaseReportAdminDefaultsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = BaseReportAdmin(CustomerGenderSummary, AdminSite())

    def test_default_has_chart_is_false(self):
        self.assertFalse(self.admin.has_chart())

    def test_default_report_title_is_empty(self):
        self.assertEqual(self.admin.get_report_title(), "")

    def test_default_generate_report_data_is_empty(self):
        self.assertEqual(self.admin.generate_report_data(self.factory.get("/")), {})

    def test_default_generate_chart_data_is_none(self):
        self.assertIsNone(self.admin.generate_chart_data({}))

    def test_default_permissions(self):
        request = self.factory.get("/")
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))


class DateParserMixinBranchTest(TestCase):
    def setUp(self):
        self.mixin = DateParserMixin()

    def test_parse_date_with_invalid_datetime_returns_none(self):
        # a date-like string that parse_datetime rejects hits the except branch
        self.assertIsNone(self.mixin.parse_date("2025-13-45T00:00:00"))

    def test_parse_date_empty_returns_none(self):
        self.assertIsNone(self.mixin.parse_date(""))
