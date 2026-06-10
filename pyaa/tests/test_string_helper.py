from django.test import TestCase

from pyaa.helpers.string import StringHelper


class StringHelperTest(TestCase):
    def test_only_numbers_strips_non_digits(self):
        self.assertEqual(StringHelper.only_numbers("529.982.247-25"), "52998224725")

    def test_only_numbers_with_letters(self):
        self.assertEqual(StringHelper.only_numbers("abc123def456"), "123456")

    def test_only_numbers_empty_string(self):
        self.assertIsNone(StringHelper.only_numbers(""))

    def test_only_numbers_none(self):
        self.assertIsNone(StringHelper.only_numbers(None))

    def test_generate_subscription_token(self):
        token = StringHelper.generate_subscription_token()
        self.assertTrue(token.startswith("subscription."))

    def test_generate_credit_purchase_token(self):
        token = StringHelper.generate_credit_purchase_token()
        self.assertTrue(token.startswith("credit-purchase."))

    def test_generate_product_purchase_token(self):
        token = StringHelper.generate_product_purchase_token()
        self.assertTrue(token.startswith("product-purchase."))

    def test_generated_tokens_are_unique(self):
        first = StringHelper.generate_subscription_token()
        second = StringHelper.generate_subscription_token()
        self.assertNotEqual(first, second)
