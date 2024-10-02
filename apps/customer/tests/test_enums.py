import unittest

from apps.customer.enums import CustomerGender


class CustomerEnumTest(unittest.TestCase):

    def test_customer_gender_choices(self):
        choices = CustomerGender.get_choices()

        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
            self.assertIsInstance(choice[0], str)
            self.assertIsInstance(choice[1], str)
