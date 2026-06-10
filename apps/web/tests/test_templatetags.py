import datetime
from decimal import Decimal
from unittest.mock import Mock

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from apps.newsletter.forms import NewsletterForm
from apps.web.templatetags import (
    pyaa,
    pyaa_customer,
    pyaa_format,
    pyaa_http,
    pyaa_status,
    pyaa_system,
)


class PyaaFormatTagsTest(TestCase):
    def test_format_currency_removes_cents(self):
        result = pyaa_format.format_currency(10, "USD")
        self.assertNotIn(".00", result)

    def test_format_percentage(self):
        self.assertEqual(pyaa_format.format_percentage(Decimal("12.5")), "12.50%")

    def test_to_timestamp_with_datetime(self):
        moment = timezone.now()
        self.assertEqual(pyaa_format.to_timestamp(moment), int(moment.timestamp()))

    def test_to_timestamp_with_non_datetime(self):
        self.assertEqual(pyaa_format.to_timestamp("value"), "value")

    def test_raw_value_with_decimal(self):
        self.assertEqual(pyaa_format.raw_value(Decimal("19.90")), "19.90")

    def test_raw_value_with_string(self):
        self.assertEqual(pyaa_format.raw_value("text"), "text")

    def test_widget_type_returns_lowercase_class_name(self):
        field = NewsletterForm()["email"]
        self.assertEqual(pyaa_format.widget_type(field), "emailinput")


class PyaaHttpTagsTest(TestCase):
    def test_force_https_upgrades_http(self):
        self.assertEqual(
            pyaa_http.force_https("http://example.com"), "https://example.com"
        )

    def test_force_https_keeps_https(self):
        self.assertEqual(
            pyaa_http.force_https("https://example.com"), "https://example.com"
        )

    def test_force_https_with_non_string(self):
        self.assertIsNone(pyaa_http.force_https(None))


class PyaaStatusTagsTest(TestCase):
    def test_status_bg_color_hex(self):
        self.assertEqual(pyaa_status.status_bg_color_hex("success"), "#28a745")

    def test_status_text_color_hex(self):
        self.assertEqual(pyaa_status.status_text_color_hex("warning"), "#000000")

    def test_status_bg_color_frontend(self):
        self.assertEqual(pyaa_status.status_bg_color_frontend("success"), "success")

    def test_status_text_color_frontend(self):
        self.assertEqual(pyaa_status.status_text_color_frontend("success"), "#ffffff")


class PyaaSystemTagsTest(TestCase):
    @override_settings(LANGUAGE_CODE="pt-br")
    def test_get_currency(self):
        self.assertEqual(pyaa_system.get_currency(), "BRL")


class PyaaCustomerTagsTest(TestCase):
    def test_has_purchased_product_without_customer(self):
        self.assertFalse(pyaa_customer.has_purchased_product(None, 1))

    def test_has_purchased_product_delegates_to_customer(self):
        customer = Mock()
        customer.has_purchased_product.return_value = True

        self.assertTrue(pyaa_customer.has_purchased_product(customer, 5))
        customer.has_purchased_product.assert_called_once_with(5)


class NavActiveTagTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_nav_active_returns_active_for_matching_path(self):
        request = self.factory.get("/")
        context = {"request": request}

        self.assertEqual(pyaa.nav_active(context, "home"), "active")

    def test_nav_active_returns_empty_for_other_path(self):
        request = self.factory.get("/other")
        context = {"request": request}

        self.assertEqual(pyaa.nav_active(context, "home"), "")

    def test_nav_active_falls_back_to_raw_pattern(self):
        request = self.factory.get("/custom/path")
        context = {"request": request}

        self.assertEqual(pyaa.nav_active(context, "/custom/path"), "active")
