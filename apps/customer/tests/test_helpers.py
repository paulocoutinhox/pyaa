from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog

User = get_user_model()


class CustomerHelperTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def test_post_save_customer_credits_updated(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com",
            password="testpassword",
            mobile_phone="1234567890",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        success = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify the operation was successful
        self.assertTrue(success)

        # verify the customer credits were updated
        customer.refresh_from_db()
        self.assertEqual(customer.credits, initial_credits)

    def test_post_save_creates_credit_log(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser2@example.com",
            password="testpassword",
            mobile_phone="1234567891",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        success = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify the operation was successful
        self.assertTrue(success)

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(customer=customer, amount=initial_credits).exists()
        )

    @patch("apps.shop.models.CreditLog.objects.create")
    def test_post_save_creates_credit_log_with_correct_values(self, mock_create):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser3@example.com",
            password="testpassword",
            mobile_phone="1234567892",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify that the correct values were passed to CreditLog
        mock_create.assert_called_once_with(
            customer=customer,
            object_type=ObjectType.BONUS,
            object_id=0,
            amount=initial_credits,
            is_refund=False,
            site=customer.site,
        )

    def test_post_save_no_credit_log_created_when_no_credits(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser4@example.com",
            password="testpassword",
            mobile_phone="1234567893",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # call post_save with zero credits to avoid creating a log
        success = CustomerHelper.add_credits(
            customer,
            0,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify operation was not successful
        self.assertFalse(success)

        # verify no credit log was created
        self.assertFalse(CreditLog.objects.filter(customer=customer).exists())

    def test_add_credits_deducts_correctly(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser5@example.com",
            password="testpassword",
            mobile_phone="1234567894",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=100,  # starting credits
        )

        # deduct 50 credits
        success = CustomerHelper.add_credits(customer, -50, is_refund=False)

        # verify operation was successful
        self.assertTrue(success)

        # verify the updated credits
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 50)

    def test_add_credits_does_not_deduct_if_insufficient_credits(self):
        # create a customer with 30 credits
        user = User.objects.create(
            email="testuser6@example.com",
            password="testpassword",
            mobile_phone="1234567895",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=30,  # starting credits
        )

        # try to deduct more credits than available
        success = CustomerHelper.add_credits(customer, -50, is_refund=False)

        # verify operation was not successful
        self.assertFalse(success)

        # verify that credits were not deducted
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 30)

    def test_add_credits_logs_when_deducting(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser7@example.com",
            password="testpassword",
            mobile_phone="1234567896",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=100,  # starting credits
        )

        # deduct 50 credits and log the transaction
        success = CustomerHelper.add_credits(
            customer,
            -50,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

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
            email="testuser8@example.com",
            password="testpassword",
            mobile_phone="1234567897",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=50,  # starting credits
        )

        # refund 50 credits
        success = CustomerHelper.add_credits(
            customer,
            50,
            is_refund=True,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

        # verify credits were added and marked as refund
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 100)

        # verify the credit log entry has is_refund=True
        credit_log = CreditLog.objects.get(
            customer=customer, amount=50, object_type=ObjectType.SUBSCRIPTION
        )
        self.assertTrue(credit_log.is_refund)

    def test_modify_log_entry_after_creation(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser9@example.com",
            password="testpassword",
            mobile_phone="1234567898",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add 100 credits
        success = CustomerHelper.add_credits(
            customer,
            100,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

        # find the log entry
        credit_log = CreditLog.objects.get(
            customer=customer, amount=100, object_type=ObjectType.SUBSCRIPTION
        )

        # set initial description
        credit_log.description = "Initial entry"
        credit_log.save()

        # verify initial description
        self.assertEqual(credit_log.description, "Initial entry")

        # update the log entry description
        credit_log.description = "Updated description"
        credit_log.save()

        # verify the description was updated
        credit_log.refresh_from_db()
        self.assertEqual(credit_log.description, "Updated description")

    def test_no_log_created_when_insufficient_credits(self):
        # create a customer with only 10 credits
        user = User.objects.create(
            email="testuser10@example.com",
            password="testpassword",
            mobile_phone="1234567899",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=10,  # starting credits
        )

        # try to deduct 20 credits
        success = CustomerHelper.add_credits(
            customer,
            -20,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation failed
        self.assertFalse(success)

        # verify no log entry was created
        self.assertFalse(
            CreditLog.objects.filter(
                customer=customer, amount=-20, object_type=ObjectType.SUBSCRIPTION
            ).exists()
        )
