from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.site.admin import SiteProfileAdmin
from apps.site.models import SiteProfile
from pyaa.mixins import ReadonlyLinksMixin, SanitizeDigitFieldsMixin


class SanitizeForm(SanitizeDigitFieldsMixin, forms.Form):
    digit_only_fields = ["phone"]

    phone = forms.CharField(required=False)
    name = forms.CharField(required=False)


class SanitizeDigitFieldsMixinTest(TestCase):
    def test_strips_non_digits_from_configured_fields(self):
        form = SanitizeForm(data={"phone": "(11) 98765-4321", "name": "John"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone"], "11987654321")
        self.assertEqual(form.cleaned_data["name"], "John")

    def test_keeps_empty_value_untouched(self):
        form = SanitizeForm(data={"phone": "", "name": "John"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone"], "")


class ReadonlyLinksMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = SiteProfileAdmin(SiteProfile, AdminSite())
        self.request = self.factory.get("/admin")
        self.site = Site.objects.create(name="Example", domain="mixin.example.com")
        self.profile = SiteProfile.objects.create(site=self.site, title="Title")

    def test_link_widget_renders_anchor_for_related_object(self):
        widget = ReadonlyLinksMixin._make_link_widget("site", "admin:sites_site_change")

        html = widget(self.profile)

        self.assertIn("<a href=", html)
        self.assertIn(str(self.site), html)

    def test_link_widget_returns_none_label_when_field_is_empty(self):
        widget = ReadonlyLinksMixin._make_link_widget(
            "missing", "admin:sites_site_change"
        )

        self.assertEqual(widget(self.profile), "None")

    def test_readonly_fields_are_cached(self):
        first = self.admin.get_readonly_fields(self.request, self.profile)
        second = self.admin.get_readonly_fields(self.request, self.profile)

        self.assertIs(first, second)
