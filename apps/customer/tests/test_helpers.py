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
        customer, _ = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            add_log=True,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

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
        customer, _ = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            add_log=True,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

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
        customer, _ = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            add_log=True,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify that the correct values were passed to CreditLog
        mock_create.assert_called_once_with(
            object_id=0,
            object_type=ObjectType.BONUS,
            customer=customer,
            amount=initial_credits,
            is_refund=False,
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
        customer, _ = CustomerHelper.add_credits(
            customer,
            0,
            is_refund=False,
            add_log=True,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

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
        customer, _ = CustomerHelper.add_credits(customer, -50, is_refund=False)

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
        customer, _ = CustomerHelper.add_credits(customer, -50, is_refund=False)

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
        customer, _ = CustomerHelper.add_credits(
            customer,
            -50,
            is_refund=False,
            add_log=True,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(
                customer=customer,
                amount=-50,
                object_type=ObjectType.SUBSCRIPTION,
            ).exists()
        )

    def test_add_credits_with_refund(self):
        # create a customer with 50 credits
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
            credits=50,  # starting credits
        )

        # refund 50 credits
        customer, _ = CustomerHelper.add_credits(
            customer,
            50,
            is_refund=True,
            add_log=True,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify the updated credits
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 100)

        # verify the log entry
        self.assertTrue(
            CreditLog.objects.filter(
                customer=customer,
                amount=50,
                object_type=ObjectType.SUBSCRIPTION,
            ).exists()
        )

    def test_modify_log_entry_after_creation(self):
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

        # add initial credits and capture the log entry
        initial_credits = 100
        customer, log_entry = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            add_log=True,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # modify the log entry
        log_entry.amount = 200
        log_entry.save()

        # verify the log entry was updated in the database
        updated_log = CreditLog.objects.get(id=log_entry.id)
        self.assertEqual(updated_log.amount, 200)
