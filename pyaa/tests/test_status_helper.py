from django.test import TestCase

from pyaa.helpers.status import StatusHelper


class StatusHelperTest(TestCase):
    def test_exact_match_hex(self):
        result = StatusHelper.get_status_color("success", "hex")
        self.assertEqual(result["bg"], "#28a745")
        self.assertEqual(result["text"], "#ffffff")

    def test_exact_match_frontend(self):
        result = StatusHelper.get_status_color("warning", "frontend")
        self.assertEqual(result["bg"], "warning")
        self.assertEqual(result["text"], "#000000")

    def test_match_is_case_insensitive(self):
        result = StatusHelper.get_status_color("ACTIVE", "hex")
        self.assertEqual(result["bg"], "#28a745")

    def test_pattern_match(self):
        result = StatusHelper.get_status_color("payment_completed", "hex")
        self.assertEqual(result["bg"], "#28a745")
        self.assertEqual(result["text"], "#ffffff")

    def test_pattern_match_refunded(self):
        result = StatusHelper.get_status_color("order-refunded", "frontend")
        self.assertEqual(result["bg"], "purple")

    def test_unknown_status_falls_back_to_hex(self):
        result = StatusHelper.get_status_color("something-weird", "hex")
        self.assertEqual(result["bg"], "#000000")
        self.assertEqual(result["text"], "#ffffff")

    def test_unknown_status_falls_back_to_frontend(self):
        result = StatusHelper.get_status_color("something-weird", "frontend")
        self.assertEqual(result["bg"], "dark")

    def test_empty_status_falls_back(self):
        result = StatusHelper.get_status_color("", "hex")
        self.assertEqual(result["bg"], "#000000")
