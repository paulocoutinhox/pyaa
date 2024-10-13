from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.customer.models import Customer
from apps.user.models import on_user_signed_up

User = get_user_model()


class UserManagerTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_create_user_success(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )

        self.assertEqual(user.email, "testuser@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            email="superuser@example.com", password="password123"
        )

        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.first_name, "Super")
        self.assertEqual(superuser.last_name, "User")

    def test_create_superuser_no_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@example.com", password="password123", is_staff=False
            )

    def test_create_superuser_no_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="superuser@example.com",
                password="password123",
                is_superuser=False,
            )

    def test_create_user_duplicate_email(self):
        User.objects.create_user(email="duplicate@example.com", password="password123")

        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="duplicate@example.com", password="password123"
            )

        self.assertEqual(str(context.exception), "This email is already in use.")

    def test_get_customer_authenticated(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.client.force_login(user)
        self.assertIsNone(user.get_customer())

    def test_get_customer_not_authenticated(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        with patch.object(User, "is_authenticated", False):
            self.assertIsNone(user.get_customer())

    def test_on_user_signed_up_creates_customer(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        on_user_signed_up(None, user)

        customer = Customer.objects.get(user=user)

        self.assertIsNotNone(customer)
        self.assertEqual(customer.language.id, 1)
        self.assertEqual(str(customer.timezone), settings.DEFAULT_TIME_ZONE)
        self.assertEqual(customer.credits, 0)

    def test_on_user_signed_up_updates_existing_customer(self):
        user = User.objects.create_user(
            email="existinguser@example.com", password="password123"
        )

        Customer.objects.create(user=user)

        on_user_signed_up(None, user)

        customer = Customer.objects.get(user=user)

        self.assertEqual(customer.language.id, 1)
        self.assertEqual(str(customer.timezone), settings.DEFAULT_TIME_ZONE)
        self.assertEqual(customer.credits, 0)

    def test_clean_email_raises_validation_error(self):
        # create two users
        user1 = User.objects.create_user(
            email="existinguser@example.com", password="testpassword"
        )
        user2 = User.objects.create_user(
            email="anotheruser@example.com", password="testpassword"
        )

        # create an emailaddress object to simulate an existing email in the system
        EmailAddress.objects.create(user=user1, email=user1.email, verified=True)

        # set the email of user2 to an existing one (user1's email)
        user2.email = "existinguser@example.com"

        # validate the email and expect a validationerror
        with self.assertRaises(ValidationError) as context:
            user2.clean_email()

        # check if the error message is correct
        self.assertIn("email", context.exception.message_dict)
