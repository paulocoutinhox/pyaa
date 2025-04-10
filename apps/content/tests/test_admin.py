from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from apps.content.admin import ContentAdmin
from apps.content.models import Content


class MockRequest:
    path = "/admin"


class MockRequestAutoComplete:
    path = "/admin/autocomplete"


class ContentAdminTest(TestCase):
    fixtures = ["apps/content/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ContentAdmin(Content, self.site)
        self.request = self.factory.get("/admin")

    def test_get_queryset(self):
        request = MockRequest()
        queryset = self.admin.get_queryset(request)
        expected_tags = ["terms-and-conditions", "privacy-policy"]
        actual_tags = list(queryset.values_list("tag", flat=True))

        self.assertCountEqual(actual_tags, expected_tags)

    def test_get_search_results(self):
        request = MockRequest()
        queryset = Content.objects.all()
        search_term = "Test"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)

    def test_get_search_results_autocomplete(self):
        request = MockRequestAutoComplete()
        queryset = Content.objects.all()
        search_term = "Test"
        queryset, use_distinct = self.admin.get_search_results(
            request, queryset, search_term
        )

        self.assertIsNotNone(queryset)
        self.assertFalse(use_distinct)
        self.assertEqual(queryset.query.order_by, ("name",))
