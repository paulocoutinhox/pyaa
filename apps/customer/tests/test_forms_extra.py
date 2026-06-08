from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.customer.enums import CustomerAddressType
from apps.customer.forms import (
    CustomerAddressAdminForm,
    CustomerChangePasswordForm,
    CustomerLoginForm,
    CustomerPasswordRecoveryForm,
    CustomerResetPasswordForm,
    CustomerSignupForm,
    CustomerUpdateAddressForm,
    CustomerUpdateAvatarForm,
    CustomerUpdateProfileForm,
)
from apps.customer.models import Customer, CustomerAddress

User = get_user_model()


class CustomerFormsExtraTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def setUp(self):
        self.site = Site.objects.get_current()

    def make_customer(self, email, **user_kwargs):
        user = User.objects.create_user(
            email=email,
            password="testpassword",
            site=self.site,
            **user_kwargs,
        )
        customer = Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
        )
        return user, customer

    def test_login_form_valid(self):
        form = CustomerLoginForm(
            data={"username": "user@example.com", "password": "secret"}
        )
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.ReCaptchaField.clean")
    def test_signup_form_clean_with_existing_errors(self, mock_clean):
        mock_clean.return_value = "PASSED"
        # missing required fields produce errors so clean should early return
        form = CustomerSignupForm(data={"captcha": "PASSED"})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    @patch("django_recaptcha.fields.ReCaptchaField.clean")
    def test_signup_form_clean_validation_error(self, mock_clean):
        mock_clean.return_value = "PASSED"

        # create a user already using this email to trigger full_clean error
        User.objects.create_user(email="dup@example.com", password="x", site=self.site)

        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "gender": "male",
            "email": "dup@example.com",
            "password": "testpassword",
            "accept_terms": True,
            "captcha": "PASSED",
        }
        form = CustomerSignupForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_update_profile_form_no_user_initial(self):
        # form built without a user does not populate initials
        form = CustomerUpdateProfileForm()
        self.assertIsNone(form.user)

    def test_update_profile_form_initial_from_customer(self):
        user, customer = self.make_customer(
            "prof@example.com", first_name="A", last_name="B"
        )
        customer.nickname = "nick"
        customer.save()

        form = CustomerUpdateProfileForm(user=user)
        self.assertEqual(form.fields["first_name"].initial, "A")
        self.assertEqual(form.fields["nickname"].initial, "nick")

    def test_update_profile_form_user_without_customer(self):
        # user has no customer, nickname/gender initials are not set
        user = User.objects.create_user(
            email="nocust@example.com",
            password="testpassword",
            first_name="No",
            last_name="Cust",
            site=self.site,
        )
        form = CustomerUpdateProfileForm(user=user)
        self.assertEqual(form.fields["first_name"].initial, "No")
        self.assertFalse(user.has_customer())

    def test_update_avatar_form_initial(self):
        user, customer = self.make_customer("av@example.com")
        form = CustomerUpdateAvatarForm(user=user)
        self.assertIn("avatar", form.fields)

    def test_update_avatar_form_no_user(self):
        form = CustomerUpdateAvatarForm()
        self.assertIn("avatar", form.fields)

    def test_address_admin_form_init_placeholders(self):
        form = CustomerAddressAdminForm()
        self.assertEqual(form.fields["country_code"].widget.attrs["placeholder"], "BR")
        self.assertEqual(
            form.fields["postal_code"].widget.attrs["placeholder"], "00000-000"
        )
        self.assertEqual(form.fields["state"].widget.attrs["placeholder"], "SP")

    def test_update_address_form_creates_new(self):
        user, customer = self.make_customer("addr1@example.com")

        form_data = {
            "address_line1": "Main St",
            "address_line2": "",
            "street_number": "100",
            "complement": "",
            "city": "Sao Paulo",
            "state": "SP",
            "postal_code": "01000-000",
            "country_code": "BR",
        }
        form = CustomerUpdateAddressForm(data=form_data, customer=customer)
        self.assertTrue(form.is_valid())
        address = form.save()
        self.assertEqual(address.customer, customer)
        self.assertEqual(address.address_type, CustomerAddressType.MAIN)

    def test_update_address_form_updates_existing(self):
        user, customer = self.make_customer("addr2@example.com")

        existing = CustomerAddress.objects.create(
            customer=customer,
            address_type=CustomerAddressType.MAIN,
            address_line1="Old",
            street_number="1",
            city="Old City",
            state="SP",
            postal_code="01000000",
            country_code="BR",
        )

        form_data = {
            "address_line1": "New Street",
            "address_line2": "Apt",
            "street_number": "200",
            "complement": "C",
            "city": "Rio",
            "state": "RJ",
            "postal_code": "20000-000",
            "country_code": "BR",
        }
        form = CustomerUpdateAddressForm(data=form_data, customer=customer)
        self.assertTrue(form.is_valid())
        address = form.save()
        self.assertEqual(address.pk, existing.pk)
        self.assertEqual(address.address_line1, "New Street")
        self.assertEqual(address.city, "Rio")

    def test_update_address_form_no_customer(self):
        form_data = {
            "address_line1": "Main St",
            "address_line2": "",
            "street_number": "100",
            "complement": "",
            "city": "Sao Paulo",
            "state": "SP",
            "postal_code": "01000-000",
            "country_code": "BR",
        }
        form = CustomerUpdateAddressForm(data=form_data)
        self.assertTrue(form.is_valid())
        address = form.save(commit=False)
        self.assertIsNone(address.pk)

    def test_password_recovery_form_finds_user(self):
        self.make_customer("rec@example.com")
        form = CustomerPasswordRecoveryForm()
        form.cleaned_data = {"identifier": "rec@example.com"}
        cleaned = form.clean()
        self.assertIn("user", cleaned)
        self.assertEqual(cleaned["user"].email, "rec@example.com")

    def test_password_recovery_form_user_not_found(self):
        form = CustomerPasswordRecoveryForm()
        form.cleaned_data = {"identifier": "missing@example.com"}
        cleaned = form.clean()
        self.assertNotIn("user", cleaned)

    def test_password_recovery_form_no_identifier(self):
        form = CustomerPasswordRecoveryForm()
        form.cleaned_data = {}
        cleaned = form.clean()
        self.assertNotIn("user", cleaned)

    def test_reset_password_form_match(self):
        form = CustomerResetPasswordForm(
            data={
                "password": "Str0ngP@ssw0rd!",
                "password_confirmation": "Str0ngP@ssw0rd!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_reset_password_form_rejects_weak_password(self):
        # short and numeric passwords must fail the strength validators
        form = CustomerResetPasswordForm(
            data={"password": "123", "password_confirmation": "123"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_reset_password_form_mismatch(self):
        form = CustomerResetPasswordForm(
            data={"password": "abc12345", "password_confirmation": "different"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password_confirmation", form.errors)

    def test_change_password_form_incorrect_current(self):
        user, _ = self.make_customer("cpw1@example.com")
        form = CustomerChangePasswordForm(
            data={
                "current_password": "wrongpassword",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            user=user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("current_password", form.errors)

    def test_change_password_form_mismatch(self):
        user, _ = self.make_customer("cpw2@example.com")
        form = CustomerChangePasswordForm(
            data={
                "current_password": "testpassword",
                "new_password": "newpass123",
                "confirm_password": "other123",
            },
            user=user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_change_password_form_save(self):
        user, _ = self.make_customer("cpw3@example.com")
        form = CustomerChangePasswordForm(
            data={
                "current_password": "testpassword",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            user=user,
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpass123"))

    def test_change_password_form_save_no_user(self):
        form = CustomerChangePasswordForm()
        form.cleaned_data = {"new_password": "x"}
        self.assertFalse(form.save())

    def test_change_password_clean_current_no_user(self):
        form = CustomerChangePasswordForm()
        form.cleaned_data = {"current_password": "abc"}
        self.assertEqual(form.clean_current_password(), "abc")

    def test_reset_password_form_only_one_password(self):
        # only password set, no confirmation, exercises the partial branch
        form = CustomerResetPasswordForm()
        form.cleaned_data = {"password": "abc12345", "password_confirmation": ""}
        self.assertEqual(form.clean(), form.cleaned_data)

    def test_change_password_form_only_one_new(self):
        user, _ = self.make_customer("cpw4@example.com")
        form = CustomerChangePasswordForm(user=user)
        form.cleaned_data = {"new_password": "abc12345", "confirm_password": ""}
        self.assertEqual(form.clean(), form.cleaned_data)

    def test_update_address_form_create_no_commit(self):
        user, customer = self.make_customer("addr3@example.com")

        form_data = {
            "address_line1": "Main St",
            "address_line2": "",
            "street_number": "100",
            "complement": "",
            "city": "Sao Paulo",
            "state": "SP",
            "postal_code": "01000-000",
            "country_code": "BR",
        }
        form = CustomerUpdateAddressForm(data=form_data, customer=customer)
        self.assertTrue(form.is_valid())
        address = form.save(commit=False)
        self.assertIsNone(address.pk)

    def test_update_address_form_update_no_commit(self):
        user, customer = self.make_customer("addr4@example.com")

        existing = CustomerAddress.objects.create(
            customer=customer,
            address_type=CustomerAddressType.MAIN,
            address_line1="Old",
            street_number="1",
            city="Old City",
            state="SP",
            postal_code="01000000",
            country_code="BR",
        )

        form_data = {
            "address_line1": "Changed",
            "address_line2": "",
            "street_number": "9",
            "complement": "",
            "city": "Niteroi",
            "state": "RJ",
            "postal_code": "24000-000",
            "country_code": "BR",
        }
        form = CustomerUpdateAddressForm(data=form_data, customer=customer)
        self.assertTrue(form.is_valid())
        address = form.save(commit=False)
        self.assertEqual(address.pk, existing.pk)
        existing.refresh_from_db()
        # not committed, db value unchanged
        self.assertEqual(existing.address_line1, "Old")
