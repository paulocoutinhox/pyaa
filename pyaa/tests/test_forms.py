from django_recaptcha.fields import ReCaptchaField
from django.test import TestCase

from pyaa.forms import AdminAuthenticationFormWithCaptcha


class AdminAuthenticationFormWithCaptchaTest(TestCase):
    def test_captcha_field_is_added(self):
        form = AdminAuthenticationFormWithCaptcha()

        self.assertIn("captcha", form.fields)
        self.assertIsInstance(form.fields["captcha"], ReCaptchaField)

    def test_captcha_is_required_when_missing(self):
        form = AdminAuthenticationFormWithCaptcha(
            data={"username": "admin", "password": "secret"}
        )

        # without a captcha response the form must be invalid
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)
