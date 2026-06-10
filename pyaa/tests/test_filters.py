from django.db.models import Q
from django.test import RequestFactory, TestCase

from apps.banner.models import Banner
from pyaa.filters import (
    DigitsOnlyFilter,
    MaskedInputFilter,
    StringSanitizingFilter,
)


class ConcreteMaskedFilter(MaskedInputFilter):
    title = "masked"
    parameter_name = "masked"
    input_mask = "999.999.999-99"


class ConcreteSanitizingFilter(StringSanitizingFilter):
    title = "sanitizing"
    parameter_name = "sanitizing"


class ConcreteDigitsOnlyFilter(DigitsOnlyFilter):
    title = "digits"
    parameter_name = "digits"
    input_mask = "999.999.999-99"

    def field_query(self, value):
        return Q(title__icontains=value)


class FakeChangeList:
    add_facets = False

    def __init__(self, params):
        self.params = params

    def get_filters_params(self, params=None):
        return dict(self.params)

    def get_query_string(self, new_params=None, remove=None):
        return "?changed"


class MaskedInputFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build(self, request, params):
        return ConcreteMaskedFilter(request, dict(params), Banner, None)

    def test_choices_yields_all_choice_with_mask(self):
        request = self.factory.get("/admin", {"masked": "123", "other": "x"})
        filter_instance = self._build(request, {"masked": "123", "other": "x"})
        changelist = FakeChangeList({"masked": "123", "other": "x"})

        choices = list(filter_instance.choices(changelist))

        self.assertEqual(len(choices), 1)
        all_choice = choices[0]
        self.assertEqual(all_choice["input_mask"], "999.999.999-99")

        # query_parts should exclude the filter's own parameter
        query_parts = list(all_choice["query_parts"])
        keys = [k for k, _ in query_parts]
        self.assertIn("other", keys)
        self.assertNotIn("masked", keys)


class StringSanitizingFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build(self, request, params):
        return ConcreteSanitizingFilter(request, dict(params), Banner, None)

    def test_only_digits_strips_non_numeric(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})
        self.assertEqual(filter_instance.only_digits("(11) 98765-4321"), "11987654321")

    def test_only_digits_returns_empty_value_unchanged(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})
        self.assertEqual(filter_instance.only_digits(""), "")
        self.assertIsNone(filter_instance.only_digits(None))

    def test_sanitize_value_default_is_identity(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})
        self.assertEqual(filter_instance.sanitize_value("abc"), "abc")

    def test_queryset_returns_unchanged_with_value(self):
        request = self.factory.get("/admin", {"sanitizing": "  hello  "})
        filter_instance = self._build(request, {"sanitizing": "  hello  "})

        queryset = Banner.objects.all()
        result = filter_instance.queryset(request, queryset)
        self.assertIs(result, queryset)

    def test_queryset_returns_unchanged_without_value(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})

        queryset = Banner.objects.all()
        result = filter_instance.queryset(request, queryset)
        self.assertIs(result, queryset)


class DigitsOnlyFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build(self, request, params):
        return ConcreteDigitsOnlyFilter(request, dict(params), Banner, None)

    def test_sanitize_value_keeps_only_digits(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})
        self.assertEqual(
            filter_instance.sanitize_value("123.456.789-00"), "12345678900"
        )

    def test_queryset_returns_unchanged_without_value(self):
        request = self.factory.get("/admin")
        filter_instance = self._build(request, {})

        queryset = Banner.objects.all()
        result = filter_instance.queryset(request, queryset)
        self.assertIs(result, queryset)

    def test_queryset_applies_field_query_with_value(self):
        request = self.factory.get("/admin", {"digits": "1.2.3"})
        filter_instance = self._build(request, {"digits": "1.2.3"})

        queryset = Banner.objects.all()
        result = filter_instance.queryset(request, queryset)

        # filter must have been applied (different queryset returned)
        self.assertIsNot(result, queryset)
        self.assertEqual(result.model, Banner)

    def test_field_query_not_implemented_by_base(self):
        class NoFieldQuery(DigitsOnlyFilter):
            title = "x"
            parameter_name = "x"

        request = self.factory.get("/admin", {"x": "123"})
        filter_instance = NoFieldQuery(request, {"x": "123"}, Banner, None)

        with self.assertRaises(NotImplementedError):
            filter_instance.queryset(request, Banner.objects.all())
