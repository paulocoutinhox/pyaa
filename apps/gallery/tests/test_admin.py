from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from apps.gallery.admin import GalleryAdmin
from apps.gallery.models import Gallery
from apps.language.models import Language


class MockRequest:
    path = "/admin"


class MockRequestAutoComplete:
    path = "/admin/autocomplete"


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

    def test_get_search_results_autocomplete(self):
        request = MockRequestAutoComplete()
        queryset = Gallery.objects.all()
        search_term = "Test"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)
        self.assertEqual(queryset.query.order_by, ("name",))
