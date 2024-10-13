from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog

User = get_user_model()


class CustomerHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_post_save_customer_credits_updated(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        CustomerHelper.add_credits(customer, initial_credits, True, 0, ObjectType.BONUS)

        # verify the customer credits were updated
        customer.refresh_from_db()
        self.assertEqual(customer.credits, initial_credits)

    def test_post_save_creates_credit_log(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        CustomerHelper.add_credits(customer, initial_credits, True, 0, ObjectType.BONUS)

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(customer=customer, amount=initial_credits).exists()
        )

    @patch("apps.shop.models.CreditLog.objects.create")
    def test_post_save_creates_credit_log_with_correct_values(self, mock_create):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        CustomerHelper.add_credits(customer, initial_credits, True, 0, ObjectType.BONUS)

        # verify that the correct values were passed to CreditLog
        mock_create.assert_called_once_with(
            object_id=0,
            object_type=ObjectType.BONUS,
            customer=customer,
            amount=initial_credits,
        )

    def test_post_save_no_credit_log_created_when_no_credits(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=0,  # starting credits
        )

        # call post_save with zero credits to avoid creating a log
        CustomerHelper.add_credits(customer, 0, True, 0, ObjectType.BONUS)

        # verify no credit log was created
        self.assertFalse(CreditLog.objects.filter(customer=customer).exists())

    def test_add_credits_deducts_correctly(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=100,  # starting credits
        )

        # deduct 50 credits
        CustomerHelper.add_credits(customer, -50)

        # verify the updated credits
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 50)

    def test_add_credits_does_not_deduct_if_insufficient_credits(self):
        # create a customer with 30 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=30,  # starting credits
        )

        # try to deduct more credits than available
        CustomerHelper.add_credits(customer, -50)

        # verify that credits were not deducted
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 30)

    def test_add_credits_logs_when_deducting(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
            credits=100,  # starting credits
        )

        # deduct 50 credits and log the transaction
        CustomerHelper.add_credits(
            customer,
            -50,
            add_log=True,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(
                customer=customer, amount=-50, object_type=ObjectType.SUBSCRIPTION
            ).exists()
        )
