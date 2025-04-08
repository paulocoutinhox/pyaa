from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserManagerTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_create_user_success_email(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_success_cpf(self):
        user = User.objects.create_user(cpf="12345678901", password="password123")
        self.assertEqual(user.cpf, "12345678901")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_success_mobile_phone(self):
        user = User.objects.create_user(
            mobile_phone="11999999999", password="password123"
        )
        self.assertEqual(user.mobile_phone, "11999999999")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_login_provided(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(email="", password="password123")
        error = context.exception
        self.assertEqual(error.message, "error.at-least-one-login-provider-is-required")

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password="password123",
        )
        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_no_is_staff(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_superuser(
                username="superuser",
                email="superuser@example.com",
                password="password123",
                is_staff=False,
            )
        error = context.exception
        self.assertIn("is_staff", error.message_dict)

    def test_create_superuser_no_is_superuser(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_superuser(
                username="superuser",
                email="superuser@example.com",
                password="password123",
                is_superuser=False,
            )
        error = context.exception
        self.assertIn("is_superuser", error.message_dict)

    def test_create_user_duplicate_email(self):
        User.objects.create_user(email="duplicate@example.com", password="password123")
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="duplicate@example.com", password="password123"
            )
        error = context.exception
        self.assertIn("email", error.message_dict)

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
