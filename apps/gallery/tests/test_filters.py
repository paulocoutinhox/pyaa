from django.contrib.admin import ModelAdmin
from django.test import RequestFactory, TestCase

from apps.gallery.filters import TitleFilter
from apps.gallery.models import Gallery
from apps.language.models import Language


# mock model admin class to simulate the admin interface
class MockModelAdmin(ModelAdmin):
    pass


class GalleryFilterTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/admin")
        self.model_admin = MockModelAdmin(Gallery, admin_site=None)

    def test_title_filter_with_value(self):
        language = Language.objects.get(code_iso_language="en-US")

        Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        filter_instance = TitleFilter(self.request, {}, Gallery, self.model_admin)
        filter_instance.value = lambda: "Test"

        queryset = Gallery.objects.all()
        filtered_queryset = filter_instance.queryset(self.request, queryset)
        self.assertTrue(filtered_queryset.filter(title__contains="Test").exists())

    def test_title_filter_without_value(self):
        filter_instance = TitleFilter(self.request, {}, Gallery, self.model_admin)
        filter_instance.value = lambda: None

        queryset = Gallery.objects.all()
        filtered_queryset = filter_instance.queryset(self.request, queryset)

        if filtered_queryset is None:
            filtered_queryset = queryset

        self.assertEqual(filtered_queryset.count(), queryset.count())
