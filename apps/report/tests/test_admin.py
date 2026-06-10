from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner, BannerAccess
from apps.customer.enums import CustomerGender
from apps.customer.models import Customer
from apps.report.admin.banner_access import BannerAccessSummaryAdmin
from apps.report.admin.customer_gender import CustomerGendeSummaryAdmin
from apps.report.models import BannerAccessSummary, CustomerGenderSummary

User = get_user_model()


class CustomerGenderSummaryAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = CustomerGendeSummaryAdmin(CustomerGenderSummary, AdminSite())
        self.request = self.factory.get("/admin")
        self.site = Site.objects.get_current()
        self._create_customer("male1@example.com", CustomerGender.MALE)
        self._create_customer("male2@example.com", CustomerGender.MALE)
        self._create_customer("female1@example.com", CustomerGender.FEMALE)

    def _create_customer(self, email, gender):
        user = User.objects.create_user(email=email, password="pass", site=self.site)
        return Customer.objects.create(
            user=user, site=self.site, language_id=1, gender=gender
        )

    def test_report_title(self):
        self.assertTrue(self.admin.get_report_title())

    def test_has_chart(self):
        self.assertTrue(self.admin.has_chart())

    def test_generate_report_data_groups_by_gender(self):
        data = self.admin.generate_report_data(self.request)

        self.assertTrue(data["has_data"])

        totals = {item["gender"]: item["total"] for item in data["data"]}
        self.assertEqual(totals[CustomerGender.MALE], 2)
        self.assertEqual(totals[CustomerGender.FEMALE], 1)
        self.assertEqual(data["data_footer"]["total"], 3)

    def test_generate_report_data_includes_gender_display(self):
        data = self.admin.generate_report_data(self.request)
        self.assertIn("gender_display", data["data"][0])

    def test_generate_chart_data_returns_base64(self):
        self.admin.init_chart_lib()
        report_data = self.admin.generate_report_data(self.request)
        chart = self.admin.generate_chart_data(report_data)

        self.assertTrue(chart.startswith("data:image/png;base64,"))

    def test_generate_chart_data_without_data_returns_none(self):
        self.assertIsNone(self.admin.generate_chart_data({"data": []}))

    def test_has_pdf_export_enabled_by_default(self):
        self.assertTrue(self.admin.has_pdf_export())

    def test_get_date_range_defaults_to_current_month(self):
        start, end = self.admin.get_date_range("created_at", self.request)

        from django.utils import timezone

        now = timezone.now()
        self.assertEqual(start.day, 1)
        self.assertEqual(start.month, now.month)
        self.assertEqual(end.month, now.month)

    def test_get_date_range_uses_request_values(self):
        request = self.factory.get(
            "/admin",
            {
                "created_at__range__gte": "01/01/2025",
                "created_at__range__lte": "01/31/2025",
            },
        )

        start, end = self.admin.get_date_range("created_at", request)

        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.day, 31)

    def test_apply_date_filter_limits_queryset(self):
        from django.utils import timezone

        start = timezone.now().replace(day=1)
        end = timezone.now()

        queryset = self.admin.apply_date_filter(
            Customer.objects.all(), "created_at", start, end
        )

        self.assertEqual(queryset.count(), 3)


class BannerAccessSummaryAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = BannerAccessSummaryAdmin(BannerAccessSummary, AdminSite())
        self.request = self.factory.get("/admin")

        # clear the global site cache so the current site reflects this test database
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.banner = Banner.objects.create(
            site=self.site,
            title="Tracked Banner",
            image="banner.jpg",
            zone=BannerZone.HOME,
        )

    def _create_access(self, access_type):
        return BannerAccess.objects.create(
            banner=self.banner,
            access_type=access_type,
            ip_address="192.168.1.1",
        )

    def test_report_title(self):
        self.assertTrue(self.admin.get_report_title())

    def test_has_no_chart(self):
        self.assertFalse(self.admin.has_chart())

    def test_get_queryset_returns_banners(self):
        self.assertIn(self.banner, self.admin.get_queryset(self.request))

    def test_generate_report_data_counts_views_and_clicks(self):
        self._create_access(BannerAccessType.VIEW)
        self._create_access(BannerAccessType.CLICK)

        data = self.admin.generate_report_data(self.request)

        self.assertTrue(data["has_data"])

        item = next(item for item in data["data"] if item["id"] == self.banner.id)
        self.assertEqual(item["total_views"], 1)
        self.assertEqual(item["total_clicks"], 1)
        self.assertEqual(item["site"], self.site.name)
        self.assertEqual(item["language"], "-")

    def test_generate_report_data_footer_totals(self):
        self._create_access(BannerAccessType.VIEW)

        data = self.admin.generate_report_data(self.request)

        self.assertEqual(data["data_footer"]["total_views"], 1)
        self.assertEqual(data["data_footer"]["total_clicks"], 0)

    def test_generate_report_data_without_accesses_is_empty(self):
        data = self.admin.generate_report_data(self.request)
        self.assertFalse(data["has_data"])
