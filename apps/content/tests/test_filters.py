from django.contrib.admin import ModelAdmin
from django.test import RequestFactory, TestCase

from apps.content.filters import TitleFilter
from apps.content.models import Content


# mock model admin class to simulate the admin interface
class MockModelAdmin(ModelAdmin):
    pass


class ContentFilterTest(TestCase):
    fixtures = ["apps/content/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/admin")
        self.model_admin = MockModelAdmin(Content, admin_site=None)

    def test_title_filter_with_value(self):
        filter_instance = TitleFilter(self.request, {}, Content, self.model_admin)
        filter_instance.value = lambda: "Terms"

        queryset = Content.objects.all()
        filtered_queryset = filter_instance.queryset(self.request, queryset)

        self.assertTrue(filtered_queryset.filter(title__contains="Terms").exists())

    def test_title_filter_without_value(self):
        filter_instance = TitleFilter(self.request, {}, Content, self.model_admin)
        filter_instance.value = lambda: None

        queryset = Content.objects.all()
        filtered_queryset = filter_instance.queryset(self.request, queryset)

        if filtered_queryset is None:
            filtered_queryset = queryset

        self.assertEqual(filtered_queryset.count(), queryset.count())
