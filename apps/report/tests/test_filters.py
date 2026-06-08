from django.test import RequestFactory, TestCase

from apps.banner.models import Banner
from apps.report.filters import ExportDataFilter


class ExportDataFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_filter(self, request):
        return ExportDataFilter(request, dict(request.GET.items()), Banner, None)

    def test_lookups_reflects_request_value(self):
        request = self.factory.get("/admin", {"export-data": "pdf"})
        filter_instance = self._build_filter(request)

        lookups = filter_instance.lookups(request, None)

        self.assertEqual(lookups, (("pdf", ""),))

    def test_queryset_is_returned_unchanged(self):
        request = self.factory.get("/admin", {"export-data": "pdf"})
        filter_instance = self._build_filter(request)

        queryset = Banner.objects.all()
        result = filter_instance.queryset(request, queryset)

        self.assertIs(result, queryset)
