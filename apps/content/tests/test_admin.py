from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.content import filters
from apps.content.admin import ContentAdmin, ContentCategoryAdmin
from apps.content.models import Content, ContentCategory


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


class ContentAdminSiteNameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ContentAdmin(Content, AdminSite())
        Site.objects.clear_cache()
        self.site = Site.objects.get_current()

    def test_site_name_with_site(self):
        content = Content.objects.create(
            site=self.site,
            title="With Site",
            content="body",
            tag="with-site",
        )
        self.assertEqual(self.admin.site_name(content), self.site.name)

    def test_site_name_without_site(self):
        content = Content.objects.create(
            site=None,
            title="No Site",
            content="body",
            tag="no-site",
        )
        self.assertIsNone(self.admin.site_name(content))


class ContentCategoryAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ContentCategoryAdmin(ContentCategory, AdminSite())

    def test_admin_registered_fields(self):
        # smoke check that the admin exposes the expected display config
        self.assertIn("name", self.admin.list_display)
        self.assertIn("name", self.admin.search_fields)


class ContentFiltersTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.content_admin = ContentAdmin(Content, AdminSite())
        self.category_admin = ContentCategoryAdmin(ContentCategory, AdminSite())

        self.match = Content.objects.create(
            title="Hello World", content="body", tag="hello"
        )
        self.other = Content.objects.create(
            title="Something Else", content="body", tag="else"
        )
        self.category = ContentCategory.objects.create(name="News", tag="news")

    def _build_filter(self, filter_cls, model_admin, model, param, value):
        request = self.factory.get("/admin")
        params = {param: [value]} if value is not None else {}
        return filter_cls(request, params, model, model_admin)

    def test_title_filter_matches(self):
        f = self._build_filter(
            filters.TitleFilter, self.content_admin, Content, "title", "Hello"
        )
        result = f.queryset(self.factory.get("/admin"), Content.objects.all())
        self.assertIn(self.match, result)
        self.assertNotIn(self.other, result)

    def test_title_filter_no_value_returns_none(self):
        f = self._build_filter(
            filters.TitleFilter, self.content_admin, Content, "title", None
        )
        self.assertIsNone(f.queryset(self.factory.get("/admin"), Content.objects.all()))

    def test_name_filter_matches(self):
        f = self._build_filter(
            filters.NameFilter, self.category_admin, ContentCategory, "name", "News"
        )
        result = f.queryset(self.factory.get("/admin"), ContentCategory.objects.all())
        self.assertIn(self.category, result)

    def test_name_filter_no_value_returns_none(self):
        f = self._build_filter(
            filters.NameFilter, self.category_admin, ContentCategory, "name", None
        )
        self.assertIsNone(
            f.queryset(self.factory.get("/admin"), ContentCategory.objects.all())
        )
