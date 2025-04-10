from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from apps.customer.forms import (
    CustomerAdminForm,
    CustomerSignupForm,
    CustomerUpdateAvatarForm,
    CustomerUpdateProfileForm,
)
from apps.customer.models import Customer

User = get_user_model()


class CustomerFormTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()

    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    @patch("apps.customer.forms.CustomerAdminForm.is_valid")
    def test_customer_admin_form_valid(self, mock_is_valid):
        user = User.objects.create_user(
            email="testuser1@example.com", password="testpassword"
        )

        mock_is_valid.return_value = True

        form_data = {
            "user": user.id,
            "language": 1,
            "gender": "male",
            "timezone": "America/Sao_Paulo",
            "site": 1,
        }

        form = CustomerAdminForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_customer_admin_form_invalid(self):
        user = User.objects.create_user(
            email="testuser2@example.com", password="testpassword"
        )

        form_data = {
            "user": user.id,
            "gender": "abcxyz",
            "timezone": "America/Sao_Paulo",
        }

        form = CustomerAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    @patch("django_recaptcha.fields.ReCaptchaField.clean")
    def test_customer_signup_form(self, mock_clean):
        mock_clean.return_value = "PASSED"

        request = self.factory.post("/signup/")
        self.add_session_to_request(request)

        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "gender": "male",
            "email": "testuser3@example.com",
            "password": "testpassword",
            "accept_terms": True,
            "captcha": "PASSED",
        }

        form = CustomerSignupForm(data=form_data)

        self.assertTrue(form.is_valid())

        customer = form.save()

        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.user.email, "testuser3@example.com")

    @patch("apps.customer.helpers.CustomerHelper.validate_unique_nickname")
    def test_customer_update_profile_form_success(self, mock_validate):
        mock_validate.return_value = None

        user = User.objects.create_user(
            email="testuser4@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
        )

        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "testuser4@example.com",
            "gender": "female",
            "nickname": "nickname",
        }

        form = CustomerUpdateProfileForm(data=form_data, user=user)
        self.assertTrue(form.is_valid())

        form.save()
        user.refresh_from_db()
        customer.refresh_from_db()

        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(customer.gender, "female")
        self.assertEqual(customer.nickname, "nickname")

    def test_customer_update_profile_form_error(self):
        user = User.objects.create_user(
            email="testuser5@example.com", password="testpassword"
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
        )

        form_data = {
            "first_name": "",
            "last_name": "",
            "gender": "invalid_gender",
        }

        form = CustomerUpdateProfileForm(data=form_data, user=user)

        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)

    @patch("apps.customer.forms.CustomerUpdateAvatarForm.is_valid")
    def test_customer_update_avatar_form_success(self, mock_is_valid):
        mock_is_valid.return_value = True

        user = User.objects.create_user(
            email="testuser6@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
        )

        with open("extras/images/python.png", "rb") as avatar_file:
            avatar = SimpleUploadedFile(
                "python.png", avatar_file.read(), content_type="image/png"
            )

            form_data = {"avatar": avatar}

            form = CustomerUpdateAvatarForm(
                data=form_data, user=user, files={"avatar": avatar}
            )

            form.cleaned_data = {"avatar": avatar}

            form.save(user)
            customer.refresh_from_db()

            self.assertTrue(customer.avatar.name.endswith(".png"))

    @patch("django_recaptcha.fields.ReCaptchaField.clean")
    def test_recaptcha_client_success(self, mock_clean):
        mock_clean.return_value = "PASSED"

        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "gender": "male",
            "email": "recaptcha@example.com",
            "password": "testpassword",
            "accept_terms": True,
            "captcha": "PASSED",
        }

        form = CustomerSignupForm(form_data)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.ReCaptchaField.clean")
    def test_recaptcha_client_failure(self, mock_clean):
        mock_clean.side_effect = ValidationError("Invalid reCAPTCHA")

        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "gender": "male",
            "email": "recaptcha@example.com",
            "password": "testpassword",
            "accept_terms": True,
            "captcha": "PASSED",
        }

        form = CustomerSignupForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)
