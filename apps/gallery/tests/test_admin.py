from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.gallery.admin import GalleryAdmin
from apps.gallery.models import Gallery


class MockRequest:
    path = "/admin"


class GalleryAdminTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = GalleryAdmin(Gallery, self.site)
        self.request = self.factory.get("/admin")

    def test_get_queryset(self):
        request = MockRequest()
        queryset = self.admin.get_queryset(request)

        self.assertIsNotNone(queryset)

    def test_get_search_results(self):
        request = MockRequest()
        queryset = Gallery.objects.all()
        search_term = "Test"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)


class GalleryAdminSiteNameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = GalleryAdmin(Gallery, AdminSite())
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()

    def test_site_name_with_site(self):
        gallery = Gallery.objects.create(
            site=self.site,
            title="With Site",
            tag="with-site",
        )
        self.assertEqual(self.admin.site_name(gallery), self.site.name)

    def test_site_name_without_site(self):
        gallery = Gallery.objects.create(
            site=None,
            title="No Site",
            tag="no-site",
        )
        self.assertIsNone(self.admin.site_name(gallery))
