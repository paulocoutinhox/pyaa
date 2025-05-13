from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.user.helpers import UserHelper

User = get_user_model()


class UserHelperTest(TestCase):
    def setUp(self):
        self.site = Site.objects.create(name="Test Site", domain="test.com")
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            site=self.site,
        )

    def test_validate_unique_email_success(self):
        UserHelper.validate_unique_email("new@example.com", self.site.id)

    def test_validate_unique_email_existing(self):
        with self.assertRaises(ValidationError) as context:
            UserHelper.validate_unique_email("test@example.com", self.site.id)

        error = context.exception
        self.assertIn("email", error.message_dict)
        self.assertEqual(
            error.message_dict["email"][0], "This e-mail is already in use."
        )

    def test_validate_unique_email_same_user(self):
        UserHelper.validate_unique_email("test@example.com", self.site.id, self.user.pk)

    def test_validate_unique_email_different_site(self):
        other_site = Site.objects.create(name="Other Site", domain="other.com")
        UserHelper.validate_unique_email("test@example.com", other_site.id)

    def test_validate_unique_cpf_success(self):
        User.objects.create_user(
            cpf="52998224725",
            password="password123",
            site=self.site,
        )

        UserHelper.validate_unique_cpf("74119455919", self.site.id)

    def test_validate_unique_cpf_existing(self):
        User.objects.create_user(
            cpf="52998224725",
            password="password123",
            site=self.site,
        )

        with self.assertRaises(ValidationError) as context:
            UserHelper.validate_unique_cpf("52998224725", self.site.id)

        error = context.exception
        self.assertIn("cpf", error.message_dict)
        self.assertEqual(error.message_dict["cpf"][0], "This CPF is already in use.")

    def test_validate_unique_cpf_same_user(self):
        user_with_cpf = User.objects.create_user(
            cpf="52998224725",
            password="password123",
            site=self.site,
        )

        UserHelper.validate_unique_cpf("52998224725", self.site.id, user_with_cpf.pk)

    def test_validate_unique_cpf_different_site(self):
        User.objects.create_user(
            cpf="52998224725",
            password="password123",
            site=self.site,
        )

        other_site = Site.objects.create(name="Other Site", domain="other.com")
        UserHelper.validate_unique_cpf("52998224725", other_site.id)

    def test_validate_unique_mobile_phone_success(self):
        UserHelper.validate_unique_mobile_phone("11999999990", self.site.id)

    def test_validate_unique_mobile_phone_existing(self):
        User.objects.create_user(
            mobile_phone="11999999999",
            password="password123",
            site=self.site,
        )

        with self.assertRaises(ValidationError) as context:
            UserHelper.validate_unique_mobile_phone("11999999999", self.site.id)

        error = context.exception
        self.assertIn("mobile_phone", error.message_dict)
        self.assertEqual(
            error.message_dict["mobile_phone"][0],
            "This mobile phone is already in use.",
        )

    def test_validate_unique_mobile_phone_same_user(self):
        user_with_phone = User.objects.create_user(
            mobile_phone="11999999999",
            password="password123",
            site=self.site,
        )

        UserHelper.validate_unique_mobile_phone(
            "11999999999", self.site.id, user_with_phone.pk
        )

    def test_validate_unique_mobile_phone_different_site(self):
        User.objects.create_user(
            mobile_phone="11999999999",
            password="password123",
            site=self.site,
        )

        other_site = Site.objects.create(name="Other Site", domain="other.com")
        UserHelper.validate_unique_mobile_phone("11999999999", other_site.id)

    def test_validate_unique_fields(self):
        User.objects.create_user(
            email="email1@example.com",
            password="password123",
            site=self.site,
        )
        User.objects.create_user(
            email="email2@example.com",
            cpf="52998224725",
            password="password123",
            site=self.site,
        )
        User.objects.create_user(
            email="email3@example.com",
            mobile_phone="11999999999",
            password="password123",
            site=self.site,
        )

        with patch.object(
            UserHelper, "validate_unique_email"
        ) as mock_email, patch.object(
            UserHelper, "validate_unique_cpf"
        ) as mock_cpf, patch.object(
            UserHelper, "validate_unique_mobile_phone"
        ) as mock_phone:

            UserHelper.validate_unique_fields(
                email="test@example.com",
                cpf="52998224725",
                mobile_phone="11999999999",
                site_id=self.site.id,
                pk=123,
            )

            mock_email.assert_called_once_with(
                "test@example.com", self.site.id, 123, ValidationError
            )
            mock_cpf.assert_called_once_with(
                "52998224725", self.site.id, 123, ValidationError
            )
            mock_phone.assert_called_once_with(
                "11999999999", self.site.id, 123, ValidationError
            )

    def test_validate_cpf_valid(self):
        valid_cpfs = ["73265877019", "90211576085", "03830245017"]
        for cpf_value in valid_cpfs:
            result = UserHelper.validate_cpf(cpf_value)
            self.assertEqual(result, cpf_value)

    def test_validate_cpf_invalid(self):
        invalid_cpfs = ["12345678901", "11111111111", "123456"]
        for cpf_value in invalid_cpfs:
            with self.assertRaises(ValidationError) as context:
                UserHelper.validate_cpf(cpf_value)

            error = context.exception
            self.assertEqual(error.message, "Invalid CPF number.")

    def test_validate_cpf_empty(self):
        result = UserHelper.validate_cpf("")
        self.assertEqual(result, "")

        result = UserHelper.validate_cpf(None)
        self.assertEqual(result, None)
