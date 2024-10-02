from django.contrib.admin import ModelAdmin
from django.test import RequestFactory, TestCase

from apps.language.filters import NameFilter
from apps.language.models import Language


# mock model admin class to simulate the admin interface
class MockModelAdmin(ModelAdmin):
    pass


# test case for the language filter
class LanguageFilterTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    # test the name filter when a value is provided
    def test_name_filter_with_value(self):
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Language, admin_site=None)
        filter_instance = NameFilter(request, {}, Language, model_admin)

        filter_instance.value = lambda: "English"
        queryset = Language.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)
        self.assertTrue(filtered_queryset.filter(name__contains="English").exists())

    # test the name filter when no value is provided
    def test_name_filter_without_value(self):
        factory = RequestFactory()
        request = factory.get("/admin")
        model_admin = MockModelAdmin(Language, admin_site=None)
        filter_instance = NameFilter(request, {}, Language, model_admin)

        filter_instance.value = lambda: None
        queryset = Language.objects.all()
        filtered_queryset = filter_instance.queryset(request, queryset)
        if filtered_queryset is None:
            filtered_queryset = queryset
        self.assertEqual(filtered_queryset.count(), queryset.count())
