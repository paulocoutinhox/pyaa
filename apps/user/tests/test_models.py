from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserManagerTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.site = Site.objects.create(name="Test Site", domain="test.com")

    def test_create_user_success_email(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="password123", site=self.site
        )

        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.site, self.site)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_success_cpf(self):
        user = User.objects.create_user(
            cpf="52998224725", password="password123", site=self.site
        )

        self.assertEqual(user.cpf, "52998224725")
        self.assertEqual(user.site, self.site)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_success_mobile_phone(self):
        user = User.objects.create_user(
            mobile_phone="11999999999", password="password123", site=self.site
        )

        self.assertEqual(user.mobile_phone, "11999999999")
        self.assertEqual(user.site, self.site)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_login_provided(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(email="", password="password123", site=self.site)

        error = context.exception

        self.assertEqual(error.message, "At least one login method is required.")

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password="password123",
            site=self.site,
        )

        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertEqual(superuser.site, self.site)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_no_is_staff(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_superuser(
                username="superuser",
                email="superuser@example.com",
                password="password123",
                is_staff=False,
                site=self.site,
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
                site=self.site,
            )

        error = context.exception

        self.assertIn("is_superuser", error.message_dict)

    def test_create_user_duplicate_email(self):
        User.objects.create_user(
            email="duplicate@example.com", password="password123", site=self.site
        )

        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="duplicate@example.com", password="password123", site=self.site
            )

        error = context.exception

        self.assertIn("email", error.message_dict)

    def test_create_user_duplicate_cpf(self):
        User.objects.create_user(
            cpf="52998224725", password="password123", site=self.site
        )

        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                cpf="52998224725", password="password123", site=self.site
            )

        error = context.exception

        self.assertIn("cpf", error.message_dict)

    def test_create_user_duplicate_mobile_phone(self):
        User.objects.create_user(
            mobile_phone="11999999999", password="password123", site=self.site
        )

        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                mobile_phone="11999999999", password="password123", site=self.site
            )

        error = context.exception

        self.assertIn("mobile_phone", error.message_dict)

    def test_get_customer_authenticated(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        self.client.force_login(user)
        self.assertIsNone(user.get_customer())

    def test_get_customer_not_authenticated(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        with patch.object(User, "is_authenticated", False):
            self.assertIsNone(user.get_customer())

    def test_has_customer(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        self.assertFalse(user.has_customer())

    def test_get_full_name(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            site=self.site,
        )
        self.assertEqual(user.get_full_name(), "Test User")

    def test_str_representation(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="testpassword",
            site=self.site,
        )

        self.assertEqual(str(user), "Test User - testuser@example.com - Test Site")

    def test_str_representation_email_only(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            site=self.site,
        )
        self.assertEqual(str(user), "testuser@example.com - Test Site")

    def test_str_representation_no_email_or_name_with_site(self):
        user = User.objects.create_user(
            cpf="52998224725",
            password="testpassword",
            site=self.site,
        )
        self.assertEqual(str(user), "Test Site")

    def test_has_customer_with_customer(self):
        from apps.customer.models import Customer
        from apps.language.models import Language

        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        language = Language.objects.get(id=1)
        Customer.objects.create(user=user, language=language, gender="male")

        self.assertTrue(user.has_customer())

    def test_has_customer_not_authenticated(self):
        user = User.objects.create_user(
            email="testuser@example.com", password="testpassword", site=self.site
        )
        with patch.object(User, "is_authenticated", False):
            self.assertFalse(user.has_customer())

    def test_clean_validation_no_login_provider(self):
        user = User(site=self.site)
        user.set_password("testpassword")

        with self.assertRaises(ValidationError) as context:
            user.clean()

        error = context.exception
        self.assertEqual(error.message, "At least one login method is required.")

    def test_create_superuser_no_login_provider(self):
        with self.assertRaises(ValidationError) as context:
            User.objects.create_superuser(
                username="superuser",
                password="password123",
                site=self.site,
            )

        error = context.exception
        self.assertEqual(error.message, "At least one login method is required.")
