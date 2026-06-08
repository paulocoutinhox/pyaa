from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.banner.admin import BannerAccessAdmin, BannerAdmin
from apps.banner.enums import BannerAccessType, BannerZone
from apps.banner.models import Banner, BannerAccess
from apps.language import models as language_models


class MockRequest:
    path = "/admin"


class BannerAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = BannerAdmin(Banner, self.admin_site)
        self.request = self.factory.get("/admin")

        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.language = language_models.Language.objects.first()

        self.banner = Banner.objects.create(
            site=self.site,
            language=self.language,
            title="Test Banner",
            image="banner.jpg",
            zone=BannerZone.HOME,
            sort_order=1,
            active=True,
        )

    def _create_access(self, access_type):
        return BannerAccess.objects.create(
            banner=self.banner,
            access_type=access_type,
            ip_address="192.168.1.1",
        )

    def test_get_queryset_annotates_counts(self):
        self._create_access(BannerAccessType.VIEW)
        self._create_access(BannerAccessType.CLICK)

        qs = self.admin.get_queryset(MockRequest())
        obj = qs.get(id=self.banner.id)

        self.assertEqual(obj.total_views, 1)
        self.assertEqual(obj.total_clicks, 1)

    def test_total_views_with_annotation(self):
        self._create_access(BannerAccessType.VIEW)
        obj = self.admin.get_queryset(MockRequest()).get(id=self.banner.id)
        self.assertEqual(self.admin.total_views(obj), 1)

    def test_total_clicks_with_annotation(self):
        self._create_access(BannerAccessType.CLICK)
        obj = self.admin.get_queryset(MockRequest()).get(id=self.banner.id)
        self.assertEqual(self.admin.total_clicks(obj), 1)

    def test_total_views_without_annotation_returns_zero(self):
        # a raw instance with no annotation falls back to 0
        self.assertEqual(self.admin.total_views(self.banner), 0)

    def test_total_clicks_without_annotation_returns_zero(self):
        self.assertEqual(self.admin.total_clicks(self.banner), 0)


class BannerAccessAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = BannerAccessAdmin(BannerAccess, self.admin_site)
        self.request = self.factory.get("/admin")

        Site.objects.clear_cache()
        self.site = Site.objects.get_current()
        self.banner = Banner.objects.create(
            site=self.site,
            title="Access Banner",
            image="banner.jpg",
            zone=BannerZone.HOME,
        )
        self.access = BannerAccess.objects.create(
            banner=self.banner,
            access_type=BannerAccessType.VIEW,
            ip_address="10.0.0.1",
        )

    def test_ip_address_display(self):
        self.assertEqual(self.admin.ip_address(self.access), "10.0.0.1")

    def test_has_add_permission_disabled(self):
        self.assertFalse(self.admin.has_add_permission(MockRequest()))

    def test_has_change_permission_disabled(self):
        self.assertFalse(self.admin.has_change_permission(MockRequest()))
        self.assertFalse(self.admin.has_change_permission(MockRequest(), self.access))
