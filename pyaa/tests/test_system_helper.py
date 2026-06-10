from django.test import TestCase, override_settings

from pyaa.helpers.system import SystemHelper


class SystemHelperTest(TestCase):
    @override_settings(LANGUAGE_CODE="pt-br")
    def test_get_currency_for_brazilian_portuguese(self):
        self.assertEqual(SystemHelper.get_currency(), "BRL")

    @override_settings(LANGUAGE_CODE="en-us")
    def test_get_currency_for_english(self):
        self.assertEqual(SystemHelper.get_currency(), "USD")

    @override_settings(LANGUAGE_CODE="es-es")
    def test_get_currency_for_spanish(self):
        self.assertEqual(SystemHelper.get_currency(), "EUR")

    @override_settings(LANGUAGE_CODE="fr-fr")
    def test_get_currency_for_unmapped_language(self):
        self.assertIsNone(SystemHelper.get_currency())

    @override_settings(LANGUAGE_CODE="EN-US")
    def test_get_currency_is_case_insensitive(self):
        self.assertEqual(SystemHelper.get_currency(), "USD")
