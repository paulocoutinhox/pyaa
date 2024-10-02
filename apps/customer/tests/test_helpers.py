from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog

User = get_user_model()


class CustomerHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com", password="testpassword"
        )

        self.customer = Customer.objects.create(
            user=self.user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
        )

        self.initial_credits = 100

        settings.CUSTOMER_INITIAL_CREDITS = self.initial_credits

    def test_post_save_customer_credits_updated(self):
        CustomerHelper.post_save(self.customer)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.credits, self.initial_credits)

    def test_post_save_creates_credit_log(self):
        CustomerHelper.post_save(self.customer)

        self.assertTrue(
            CreditLog.objects.filter(
                customer=self.customer, amount=self.initial_credits
            ).exists()
        )

    @patch("apps.shop.models.CreditLog.objects.create")
    def test_post_save_creates_credit_log_with_correct_values(self, mock_create):
        CustomerHelper.post_save(self.customer)

        mock_create.assert_called_once_with(
            object_id=0,
            object_type=ObjectType.BONUS,
            customer=self.customer,
            amount=self.initial_credits,
        )

    def test_post_save_no_credit_log_created_when_no_credits(self):
        settings.CUSTOMER_INITIAL_CREDITS = 0
        CustomerHelper.post_save(self.customer)

        self.assertFalse(CreditLog.objects.filter(customer=self.customer).exists())
