import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.customer.enums import CustomerGender
from apps.customer.models import Customer
from apps.language import models as language_models
from apps.shop.enums import (
    PaymentGatewayCancelAction,
    SubscriptionStatus,
)
from apps.shop.models import Subscription

User = get_user_model()


def create_customer(email="user@example.com", password="StrongPass123", site=None):
    site = site or Site.objects.get_current()
    language = language_models.Language.objects.first()
    user = User.objects.create_user(email=email, password=password, site=site)
    customer = Customer.objects.create(
        user=user,
        site=site,
        language=language,
        gender=CustomerGender.MALE,
    )
    return user, customer


class AccountAuthRequiredTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_profile_requires_login(self):
        response = self.client.get(reverse("account_profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_subscriptions_requires_login(self):
        response = self.client.get(reverse("account_subscriptions"))
        self.assertEqual(response.status_code, 302)

    def test_customer_required_redirects_home_without_customer(self):
        user = User.objects.create_user(
            email="nocustomer@example.com",
            password="StrongPass123",
            site=Site.objects.get_current(),
        )
        self.client.force_login(user)

        response = self.client.get(reverse("account_profile"))
        self.assertRedirects(response, reverse("home"))


class AccountLoginViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()

    def test_get_renders_form(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/login.html")

    def test_post_valid_credentials_redirects_profile(self):
        response = self.client.post(
            reverse("account_login"),
            {"username": "user@example.com", "password": "StrongPass123"},
        )
        self.assertRedirects(response, reverse("account_profile"))

    def test_post_valid_credentials_with_next(self):
        response = self.client.post(
            reverse("account_login") + "?next=/contact/",
            {"username": "user@example.com", "password": "StrongPass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/contact/")

    def test_post_invalid_credentials_shows_error(self):
        response = self.client.post(
            reverse("account_login"),
            {"username": "user@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/login.html")

    @override_settings(
        CACHES={
            "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
        },
        LOGIN_RATELIMIT_MAX_ATTEMPTS=3,
    )
    def test_login_is_throttled_after_repeated_failures(self):
        cache.clear()

        for _attempt in range(3):
            self.client.post(
                reverse("account_login"),
                {"username": "user@example.com", "password": "wrong"},
            )

        # once the limit is reached even valid credentials are blocked
        response = self.client.post(
            reverse("account_login"),
            {"username": "user@example.com", "password": "StrongPass123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/login.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AccountSignupViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_get_renders_form(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/signup.html")

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=False)
    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.customer.helpers.CustomerHelper.post_save")
    def test_post_valid_signup_logs_in_and_redirects(
        self, mock_post_save, mock_captcha
    ):
        response = self.client.post(
            reverse("account_signup"),
            {
                "first_name": "John",
                "last_name": "Doe",
                "gender": CustomerGender.MALE,
                "email": "new@example.com",
                "password": "StrongPass123",
                "accept_terms": "on",
                "g-recaptcha-response": "PASSED",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_signup_success"), response.url)
        self.assertTrue(Customer.objects.filter(user__email="new@example.com").exists())

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=True)
    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.customer.helpers.CustomerHelper.post_save")
    def test_post_valid_signup_with_activation_required(
        self, mock_post_save, mock_captcha
    ):
        response = self.client.post(
            reverse("account_signup"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "gender": CustomerGender.FEMALE,
                "email": "jane@example.com",
                "password": "StrongPass123",
                "accept_terms": "on",
                "g-recaptcha-response": "PASSED",
            },
        )
        self.assertRedirects(response, reverse("account_activation_pending"))

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_post_invalid_signup_rerenders(self, mock_captcha):
        response = self.client.post(
            reverse("account_signup"),
            {
                "first_name": "",
                "email": "not-an-email",
                "g-recaptcha-response": "PASSED",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class AccountLogoutViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_logout_redirects_to_success(self):
        user, _ = create_customer()
        self.client.force_login(user)

        response = self.client.get(reverse("account_logout"))
        self.assertRedirects(response, reverse("account_logout_success"))

    def test_logout_success_renders(self):
        response = self.client.get(reverse("account_logout_success"))
        self.assertEqual(response.status_code, 200)


class AccountProfileViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_profile_renders(self):
        response = self.client.get(reverse("account_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/profile.html")
        self.assertEqual(response.context["customer"], self.customer)


class AccountUpdateProfileViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_get_renders(self):
        response = self.client.get(reverse("account_update_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/update_profile.html")

    def test_post_valid_updates_and_redirects(self):
        response = self.client.post(
            reverse("account_update_profile"),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "user@example.com",
                "cpf": "",
                "mobile_phone": "",
                "nickname": "nick",
                "gender": CustomerGender.MALE,
            },
        )
        self.assertRedirects(response, reverse("account_profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_post_invalid_rerenders(self):
        response = self.client.post(
            reverse("account_update_profile"),
            {
                "first_name": "Updated",
                "email": "not-an-email",
                "gender": CustomerGender.MALE,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class AccountUpdateAvatarViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_get_renders(self):
        response = self.client.get(reverse("account_update_avatar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/update_avatar.html")
        self.assertEqual(response.context["customer"], self.customer)

    @patch("apps.customer.forms.CustomerUpdateAvatarForm.save")
    def test_post_valid_updates_avatar(self, mock_save):
        image = _make_image()
        response = self.client.post(
            reverse("account_update_avatar"),
            {"avatar": image},
        )
        self.assertRedirects(response, reverse("account_profile"))
        mock_save.assert_called_once()


class AccountChangePasswordViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_get_renders(self):
        response = self.client.get(reverse("account_change_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/change_password.html")

    def test_post_valid_changes_password(self):
        response = self.client.post(
            reverse("account_change_password"),
            {
                "current_password": "StrongPass123",
                "new_password": "NewStrongPass456",
                "confirm_password": "NewStrongPass456",
            },
        )
        # do not follow the redirect, changing the password invalidates the session
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("account_profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456"))

    def test_post_invalid_rerenders(self):
        response = self.client.post(
            reverse("account_change_password"),
            {
                "current_password": "wrong",
                "new_password": "NewStrongPass456",
                "confirm_password": "different",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class AccountDeleteViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_get_renders(self):
        response = self.client.get(reverse("account_delete"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/delete.html")

    def test_post_deletes_account(self):
        response = self.client.post(reverse("account_delete"), {})
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_active_subscription_blocks_delete(self):
        plan = _create_plan()
        Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=self.customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
        )

        response = self.client.get(reverse("account_delete"))
        self.assertRedirects(response, reverse("account_profile"))
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())


class AccountListViewsTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_subscriptions_renders(self):
        response = self.client.get(reverse("account_subscriptions"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/subscriptions.html")

    def test_credits_renders(self):
        response = self.client.get(reverse("account_credits"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/credits.html")

    def test_credit_purchases_renders(self):
        response = self.client.get(reverse("account_credit_purchases"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/credit_purchases.html")

    def test_product_purchases_renders(self):
        response = self.client.get(reverse("account_product_purchases"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/product_purchases.html")


class AccountSubscriptionCancelViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_cancel_unknown_token_redirects_home(self):
        response = self.client.get(
            reverse(
                "account_subscription_cancel",
                kwargs={"token": "subscription.unknown"},
            )
        )
        self.assertRedirects(response, reverse("home"))

    @patch("apps.web.views.account.ShopHelper.process_cancel_for_subscription")
    def test_cancel_redirect_action(self, mock_cancel):
        plan = _create_plan()
        subscription = Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=self.customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
        )
        mock_cancel.return_value = {
            "action": PaymentGatewayCancelAction.REDIRECT,
            "url": "/account/subscriptions/",
        }

        response = self.client.get(
            reverse(
                "account_subscription_cancel",
                kwargs={"token": str(subscription.token)},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/subscriptions/")

    @patch("apps.web.views.account.ShopHelper.process_cancel_for_subscription")
    def test_cancel_invalid_action_redirects_home(self, mock_cancel):
        plan = _create_plan()
        subscription = Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=self.customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
        )
        mock_cancel.return_value = {"action": "invalid"}

        response = self.client.get(
            reverse(
                "account_subscription_cancel",
                kwargs={"token": str(subscription.token)},
            )
        )
        self.assertRedirects(response, reverse("home"))

    @patch("apps.web.views.account.ShopHelper.process_cancel_for_subscription")
    def test_cannot_cancel_another_customers_subscription(self, mock_cancel):
        # subscription owned by a different customer must not be cancelable
        other_user, other_customer = create_customer(email="other@example.com")
        plan = _create_plan()
        subscription = Subscription.objects.create(
            site=Site.objects.get_current(),
            customer=other_customer,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
        )

        response = self.client.get(
            reverse(
                "account_subscription_cancel",
                kwargs={"token": str(subscription.token)},
            )
        )

        self.assertRedirects(response, reverse("home"))
        mock_cancel.assert_not_called()


class AccountStaticPagesTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_signup_success(self):
        response = self.client.get(reverse("account_signup_success"))
        self.assertEqual(response.status_code, 200)

    def test_password_recovery_success(self):
        response = self.client.get(reverse("account_password_recovery_success"))
        self.assertEqual(response.status_code, 200)

    def test_reset_password_success(self):
        response = self.client.get(reverse("account_reset_password_success"))
        self.assertEqual(response.status_code, 200)

    def test_activation_pending(self):
        response = self.client.get(reverse("account_activation_pending"))
        self.assertEqual(response.status_code, 200)

    def test_activation_success(self):
        response = self.client.get(reverse("account_activation_success"))
        self.assertEqual(response.status_code, 200)


class AccountPasswordRecoveryViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()

    def test_get_renders(self):
        response = self.client.get(reverse("account_password_recovery"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/password_recovery.html")

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.customer.helpers.CustomerHelper.send_password_recovery_email")
    def test_post_existing_user_sends_email(self, mock_send, mock_captcha):
        response = self.client.post(
            reverse("account_password_recovery"),
            {"identifier": "user@example.com", "g-recaptcha-response": "PASSED"},
        )
        self.assertRedirects(response, reverse("account_password_recovery_success"))
        mock_send.assert_called_once()

    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    @patch("apps.customer.helpers.CustomerHelper.send_password_recovery_email")
    def test_post_unknown_user_still_redirects(self, mock_send, mock_captcha):
        response = self.client.post(
            reverse("account_password_recovery"),
            {"identifier": "missing@example.com", "g-recaptcha-response": "PASSED"},
        )
        self.assertRedirects(response, reverse("account_password_recovery_success"))
        mock_send.assert_not_called()


class AccountResetPasswordViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.token = uuid.uuid4()
        self.customer.recovery_token = self.token
        self.customer.recovery_token_created_at = timezone.now()
        self.customer.save(
            update_fields=["recovery_token", "recovery_token_created_at"]
        )

    def test_get_renders(self):
        response = self.client.get(
            reverse("account_reset_password", kwargs={"token": self.token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/reset_password.html")

    def test_get_invalid_token_404(self):
        response = self.client.get(
            reverse("account_reset_password", kwargs={"token": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_expired_token_404(self):
        # a token older than the configured ttl must be rejected
        self.customer.recovery_token_created_at = timezone.now() - timezone.timedelta(
            hours=2
        )
        self.customer.save(update_fields=["recovery_token_created_at"])

        response = self.client.get(
            reverse("account_reset_password", kwargs={"token": self.token})
        )
        self.assertEqual(response.status_code, 404)

    def test_post_valid_resets_password(self):
        response = self.client.post(
            reverse("account_reset_password", kwargs={"token": self.token}),
            {
                "password": "BrandNewPass789",
                "password_confirmation": "BrandNewPass789",
            },
        )
        self.assertRedirects(response, reverse("account_reset_password_success"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNewPass789"))
        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.recovery_token)

    def test_post_mismatched_passwords_rerenders(self):
        response = self.client.post(
            reverse("account_reset_password", kwargs={"token": self.token}),
            {
                "password": "BrandNewPass789",
                "password_confirmation": "different",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class AccountActivateViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()

    @patch("apps.web.views.account.CustomerHelper.activate_account")
    def test_activate_success(self, mock_activate):
        mock_activate.return_value = self.customer
        response = self.client.get(
            reverse("account_activate", kwargs={"token": uuid.uuid4()})
        )
        self.assertRedirects(response, reverse("account_activation_success"))

    @patch("apps.web.views.account.CustomerHelper.activate_account")
    def test_activate_invalid_token_redirects_home(self, mock_activate):
        mock_activate.return_value = None
        response = self.client.get(
            reverse("account_activate", kwargs={"token": uuid.uuid4()})
        )
        self.assertRedirects(response, reverse("home"))

    @patch("apps.web.views.account.CustomerHelper.activate_account")
    def test_activate_exception_redirects_home(self, mock_activate):
        mock_activate.side_effect = Exception("boom")
        response = self.client.get(
            reverse("account_activate", kwargs={"token": uuid.uuid4()})
        )
        self.assertRedirects(response, reverse("home"))


class AccountUpdateAddressViewTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.user, self.customer = create_customer()
        self.client.force_login(self.user)

    def test_get_renders(self):
        response = self.client.get(reverse("account_update_address"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/account/update_address.html")

    def test_post_valid_creates_address(self):
        response = self.client.post(
            reverse("account_update_address"),
            {
                "address_line1": "Main Street",
                "address_line2": "",
                "street_number": "100",
                "complement": "",
                "city": "Sao Paulo",
                "state": "SP",
                "postal_code": "01310-100",
                "country_code": "BR",
            },
        )
        self.assertRedirects(response, reverse("account_profile"))


def _make_image():
    import io

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile("avatar.png", buffer.read(), content_type="image/png")


def _create_plan():
    from apps.shop.enums import PaymentGateway, PlanType
    from apps.shop.models import Plan

    return Plan.objects.create(
        site=Site.objects.get_current(),
        name="Test Plan",
        plan_type=PlanType.SUBSCRIPTION,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price="10.00",
        active=True,
    )
