from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
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
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.factory = RequestFactory()

    def add_session_to_request(self, request):
        # add session middleware to the request
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_customer_admin_form_valid(self):
        # create a user for the form
        user = User.objects.create_user(
            email="testuser1@example.com", password="testpassword"
        )

        # valid form data
        form_data = {
            "user": user.id,
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        # create form with valid data and check if it's valid
        form = CustomerAdminForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_customer_admin_form_invalid(self):
        # create a user for the form
        user = User.objects.create_user(
            email="testuser2@example.com", password="testpassword"
        )

        # invalid form data
        form_data = {
            "user": user.id,
            "language": 1,
            "mobile_phone": "invalid_phone_big_number",
            "home_phone": "invalid_phone_big_number",
            "gender": "abcxyz",
            "timezone": "America/Sao_Paulo",
        }

        # create form with invalid data and check if it's invalid
        form = CustomerAdminForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_customer_signup_form(self):
        # create a post request for signup
        request = self.factory.post("/signup/")
        self.add_session_to_request(request)

        # valid signup form data
        form_data = {
            "email": "testuser3@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        # create signup form with valid data, check if it's valid, and save the user
        form = CustomerSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(request)

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "testuser3@example.com")

    def test_customer_update_profile_form_success(self):
        user = User.objects.create_user(
            email="testuser4@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
        )

        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "mobile_phone": "0987654321",
            "home_phone": "1234567890",
            "gender": "female",
            "language": 1,
            "timezone": "America/New_York",
        }

        form = CustomerUpdateProfileForm(data=form_data, user=user)
        self.assertTrue(form.is_valid())

        form.save(user)
        user.refresh_from_db()
        customer.refresh_from_db()

        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(customer.mobile_phone, "0987654321")
        self.assertEqual(customer.home_phone, "1234567890")
        self.assertEqual(customer.gender, "female")
        self.assertEqual(str(customer.timezone), "America/New_York")

    def test_customer_update_profile_form_error(self):
        user = User.objects.create_user(
            email="testuser5@example.com", password="testpassword"
        )

        form_data = {
            "first_name": "",
            "last_name": "",
            "gender": "invalid_gender",
            "language": 999,
            "timezone": "Invalid/Timezone",
        }

        form = CustomerUpdateProfileForm(data=form_data, user=user)

        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)
        self.assertIn("language", form.errors)
        self.assertIn("timezone", form.errors)

    def test_customer_update_avatar_form_success(self):
        user = User.objects.create_user(
            email="testuser6@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
        )

        with open("extras/images/python.png", "rb") as avatar_file:
            avatar = SimpleUploadedFile(
                "python.png", avatar_file.read(), content_type="image/png"
            )

            form_data = {"avatar": avatar}

            form = CustomerUpdateAvatarForm(
                data=form_data, user=user, files={"avatar": avatar}
            )

            self.assertTrue(form.is_valid())
            form.save(user)
            customer.refresh_from_db()

            self.assertTrue(customer.avatar.name.endswith(".png"))

    def test_is_adding(self):
        form_data = {
            "user": 1,
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        form = CustomerAdminForm(data=form_data)
        self.assertTrue(form.is_adding())

        form.instance.pk = 1
        self.assertFalse(form.is_adding())

    def test_validate_required_field(self):
        form = CustomerAdminForm(data={})
        form.validate_required_field({"user": None}, "user")
        self.assertIn("user", form.errors)

    def test_user_field_disabled_when_instance_exists(self):
        user = User.objects.create(
            email="testuser7@example.com", password="testpassword"
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
        )

        form = CustomerAdminForm(instance=customer)
        self.assertTrue(form.fields["user"].disabled)

    def test_user_field_enabled_when_adding(self):
        form = CustomerAdminForm()
        self.assertFalse(form.fields["user"].disabled)
