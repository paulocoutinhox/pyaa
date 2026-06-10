import uuid
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.shop.enums import ObjectType, PaymentGateway, PlanType
from apps.shop.models import CreditLog, Plan

User = get_user_model()


def make_plan(credits=100, bonus=0, image=None):
    return Plan.objects.create(
        site_id=1,
        name="Test Plan",
        plan_type=PlanType.VOUCHER,
        gateway=PaymentGateway.STRIPE,
        currency="USD",
        price=10,
        credits=credits,
        bonus=bonus,
        image=image,
        active=True,
    )


class CustomerHelperTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def test_post_save_customer_credits_updated(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser@example.com",
            password="testpassword",
            mobile_phone="1234567890",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        success = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify the operation was successful
        self.assertTrue(success)

        # verify the customer credits were updated
        customer.refresh_from_db()
        self.assertEqual(customer.credits, initial_credits)

    def test_post_save_creates_credit_log(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser2@example.com",
            password="testpassword",
            mobile_phone="1234567891",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        success = CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify the operation was successful
        self.assertTrue(success)

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(customer=customer, amount=initial_credits).exists()
        )

    @patch("apps.shop.models.CreditLog.objects.create")
    def test_post_save_creates_credit_log_with_correct_values(self, mock_create):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser3@example.com",
            password="testpassword",
            mobile_phone="1234567892",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add initial credits via post_save
        initial_credits = 100
        CustomerHelper.add_credits(
            customer,
            initial_credits,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify that the correct values were passed to CreditLog
        mock_create.assert_called_once_with(
            customer=customer,
            object_type=ObjectType.BONUS,
            object_id=0,
            amount=initial_credits,
            is_refund=False,
            site=customer.site,
        )

    def test_post_save_no_credit_log_created_when_no_credits(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser4@example.com",
            password="testpassword",
            mobile_phone="1234567893",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # call post_save with zero credits to avoid creating a log
        success = CustomerHelper.add_credits(
            customer,
            0,
            is_refund=False,
            object_id=0,
            object_type=ObjectType.BONUS,
        )

        # verify operation was not successful
        self.assertFalse(success)

        # verify no credit log was created
        self.assertFalse(CreditLog.objects.filter(customer=customer).exists())

    def test_add_credits_deducts_correctly(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser5@example.com",
            password="testpassword",
            mobile_phone="1234567894",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=100,  # starting credits
        )

        # deduct 50 credits
        success = CustomerHelper.add_credits(customer, -50, is_refund=False)

        # verify operation was successful
        self.assertTrue(success)

        # verify the updated credits
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 50)

    def test_add_credits_does_not_deduct_if_insufficient_credits(self):
        # create a customer with 30 credits
        user = User.objects.create(
            email="testuser6@example.com",
            password="testpassword",
            mobile_phone="1234567895",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=30,  # starting credits
        )

        # try to deduct more credits than available
        success = CustomerHelper.add_credits(customer, -50, is_refund=False)

        # verify operation was not successful
        self.assertFalse(success)

        # verify that credits were not deducted
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 30)

    def test_add_credits_logs_when_deducting(self):
        # create a customer with 100 credits
        user = User.objects.create(
            email="testuser7@example.com",
            password="testpassword",
            mobile_phone="1234567896",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=100,  # starting credits
        )

        # deduct 50 credits and log the transaction
        success = CustomerHelper.add_credits(
            customer,
            -50,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

        # verify the credit log was created
        self.assertTrue(
            CreditLog.objects.filter(
                customer=customer,
                amount=-50,
                object_type=ObjectType.SUBSCRIPTION,
            ).exists()
        )

    def test_add_credits_with_refund(self):
        # create a customer with 50 credits
        user = User.objects.create(
            email="testuser8@example.com",
            password="testpassword",
            mobile_phone="1234567897",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=50,  # starting credits
        )

        # refund 50 credits
        success = CustomerHelper.add_credits(
            customer,
            50,
            is_refund=True,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

        # verify credits were added and marked as refund
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 100)

        # verify the credit log entry has is_refund=True
        credit_log = CreditLog.objects.get(
            customer=customer, amount=50, object_type=ObjectType.SUBSCRIPTION
        )
        self.assertTrue(credit_log.is_refund)

    def test_modify_log_entry_after_creation(self):
        # create a customer with 0 credits
        user = User.objects.create(
            email="testuser9@example.com",
            password="testpassword",
            mobile_phone="1234567898",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=0,  # starting credits
        )

        # add 100 credits
        success = CustomerHelper.add_credits(
            customer,
            100,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation was successful
        self.assertTrue(success)

        # find the log entry
        credit_log = CreditLog.objects.get(
            customer=customer, amount=100, object_type=ObjectType.SUBSCRIPTION
        )

        # set initial description
        credit_log.description = "Initial entry"
        credit_log.save()

        # verify initial description
        self.assertEqual(credit_log.description, "Initial entry")

        # update the log entry description
        credit_log.description = "Updated description"
        credit_log.save()

        # verify the description was updated
        credit_log.refresh_from_db()
        self.assertEqual(credit_log.description, "Updated description")

    def test_no_log_created_when_insufficient_credits(self):
        # create a customer with only 10 credits
        user = User.objects.create(
            email="testuser10@example.com",
            password="testpassword",
            mobile_phone="1234567899",
            site_id=1,
        )
        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            site_id=1,
            credits=10,  # starting credits
        )

        # try to deduct 20 credits
        success = CustomerHelper.add_credits(
            customer,
            -20,
            is_refund=False,
            object_id=1,
            object_type=ObjectType.SUBSCRIPTION,
        )

        # verify operation failed
        self.assertFalse(success)

        # verify no log entry was created
        self.assertFalse(
            CreditLog.objects.filter(
                customer=customer, amount=-20, object_type=ObjectType.SUBSCRIPTION
            ).exists()
        )


class CustomerHelperExtraTest(TestCase):
    fixtures = [
        "apps/language/fixtures/initial.json",
        "apps/site/fixtures/initial.json",
    ]

    def setUp(self):
        self.site = Site.objects.get_current()

    def make_customer(self, email, credits=0, mobile_phone="11999999999"):
        user = User.objects.create_user(
            email=email,
            password="testpassword",
            mobile_phone=mobile_phone,
            first_name="John",
            last_name="Doe",
            site=self.site,
        )
        return Customer.objects.create(
            user=user,
            site=self.site,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
            credits=credits,
        )

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=False, CUSTOMER_SIGNUP_PLAN=None)
    @patch("apps.customer.helpers.CustomerHelper.send_signup_email")
    def test_post_save_no_plan_sends_signup_email(self, mock_signup):
        customer = self.make_customer("post1@example.com")
        result = CustomerHelper.post_save(customer)
        mock_signup.assert_called_once_with(customer)
        self.assertEqual(result, customer)

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=True, CUSTOMER_SIGNUP_PLAN=None)
    @patch("apps.customer.helpers.CustomerHelper.send_activation_email")
    def test_post_save_activation_required(self, mock_activation):
        customer = self.make_customer("post2@example.com")
        CustomerHelper.post_save(customer)
        mock_activation.assert_called_once_with(customer)

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=False)
    @patch("apps.customer.helpers.CustomerHelper.send_signup_email")
    def test_post_save_with_plan_adds_credits(self, mock_signup):
        plan = make_plan(credits=50)
        customer = self.make_customer("post3@example.com")

        with override_settings(CUSTOMER_SIGNUP_PLAN=plan.id):
            with patch("apps.customer.helpers.CustomerHelper.send_credits_email"):
                CustomerHelper.post_save(customer)

        customer.refresh_from_db()
        self.assertEqual(customer.credits, 50)

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=False)
    @patch("apps.customer.helpers.CustomerHelper.send_signup_email")
    def test_post_save_with_plan_zero_credits_no_refresh(self, mock_signup):
        # plan exists but has zero credits, add_credits returns False
        plan = make_plan(credits=0)
        customer = self.make_customer("post5@example.com")

        with override_settings(CUSTOMER_SIGNUP_PLAN=plan.id):
            CustomerHelper.post_save(customer)

        customer.refresh_from_db()
        self.assertEqual(customer.credits, 0)

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=False)
    @patch("apps.customer.helpers.CustomerHelper.send_signup_email")
    def test_post_save_with_missing_plan_id(self, mock_signup):
        customer = self.make_customer("post4@example.com")
        with override_settings(CUSTOMER_SIGNUP_PLAN=999999):
            CustomerHelper.post_save(customer)
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 0)

    @patch("apps.customer.helpers.CustomerHelper.send_credits_email")
    def test_add_credits_with_plan_and_bonus(self, mock_email):
        plan = make_plan(credits=100, bonus=20)
        customer = self.make_customer("plan1@example.com")

        success = CustomerHelper.add_credits(
            customer,
            plan=plan,
            object_type=ObjectType.VOUCHER,
            object_id=plan.id,
        )

        self.assertTrue(success)
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 120)

        # bonus log was created
        self.assertTrue(
            CreditLog.objects.filter(
                customer=customer, amount=20, object_type=ObjectType.BONUS
            ).exists()
        )
        # bonus email also sent
        self.assertEqual(mock_email.call_count, 2)

    @patch("apps.customer.helpers.CustomerHelper.send_credits_email")
    def test_add_credits_with_plan_no_bonus(self, mock_email):
        plan = make_plan(credits=100, bonus=0)
        customer = self.make_customer("plan2@example.com")

        success = CustomerHelper.add_credits(customer, plan=plan)

        self.assertTrue(success)
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 100)
        mock_email.assert_called_once()

    def test_add_credits_plan_zero_credits_returns_false(self):
        plan = make_plan(credits=0)
        customer = self.make_customer("plan3@example.com")
        success = CustomerHelper.add_credits(customer, plan=plan)
        self.assertFalse(success)

    @patch("apps.customer.helpers.CustomerHelper.send_credits_email")
    def test_add_credits_plan_no_email(self, mock_email):
        plan = make_plan(credits=100, bonus=20)
        customer = self.make_customer("plan4@example.com")
        CustomerHelper.add_credits(customer, plan=plan, send_email=False)
        mock_email.assert_not_called()

    @patch("apps.customer.helpers.CustomerHelper.send_credits_email")
    def test_add_credits_amount_positive_email(self, mock_email):
        customer = self.make_customer("amt1@example.com")
        success = CustomerHelper.add_credits(customer, amount=30)
        self.assertTrue(success)
        mock_email.assert_called_once()

    def test_add_credits_amount_zero_returns_false(self):
        customer = self.make_customer("amt2@example.com")
        self.assertFalse(CustomerHelper.add_credits(customer, amount=0))

    def test_add_credits_no_plan_no_amount_returns_false(self):
        customer = self.make_customer("amt3@example.com")
        self.assertFalse(CustomerHelper.add_credits(customer))

    @patch("apps.customer.helpers.CustomerHelper.send_credits_email")
    def test_add_credits_amount_no_email(self, mock_email):
        customer = self.make_customer("amt4@example.com")
        CustomerHelper.add_credits(customer, amount=30, send_email=False)
        mock_email.assert_not_called()

    def test_validate_unique_nickname_raises(self):
        customer = self.make_customer("nick1@example.com")
        customer.nickname = "taken"
        customer.save()

        with self.assertRaises(ValidationError):
            CustomerHelper.validate_unique_nickname("taken", self.site.id)

    def test_validate_unique_nickname_excludes_pk(self):
        customer = self.make_customer("nick2@example.com")
        customer.nickname = "mine"
        customer.save()

        # should not raise when excluding the owner pk
        CustomerHelper.validate_unique_nickname(
            "mine", self.site.id, exclude_pk=customer.pk
        )

    def test_get_customer_id_from_request_authenticated(self):
        customer = self.make_customer("req1@example.com")
        request = Mock()
        request.user = customer.user

        self.assertEqual(
            CustomerHelper.get_customer_id_from_request(request), customer.id
        )

    def test_get_customer_id_from_request_no_user(self):
        request = Mock(spec=[])
        self.assertEqual(CustomerHelper.get_customer_id_from_request(request), 0)

    def test_get_customer_id_from_request_not_authenticated(self):
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        self.assertEqual(CustomerHelper.get_customer_id_from_request(request), 0)

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_signup_email(self, mock_send):
        customer = self.make_customer("signup@example.com")
        CustomerHelper.send_signup_email(customer)
        mock_send.assert_called_once()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_signup_email_no_email(self, mock_send):
        customer = self.make_customer("noemail1@example.com")
        customer.user.email = ""
        CustomerHelper.send_signup_email(customer)
        mock_send.assert_not_called()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credits_email_bonus(self, mock_send):
        customer = self.make_customer("ce1@example.com")
        CustomerHelper.send_credits_email(customer, 10, object_type=ObjectType.BONUS)
        mock_send.assert_called_once()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credits_email_standard(self, mock_send):
        customer = self.make_customer("ce2@example.com")
        CustomerHelper.send_credits_email(customer, 10, object_type=ObjectType.VOUCHER)
        mock_send.assert_called_once()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credits_email_with_plan_relative_image(self, mock_send):
        customer = self.make_customer("ce3@example.com")
        plan = make_plan(credits=100, image="images/plan/test.png")
        CustomerHelper.send_credits_email(
            customer, 100, object_type=ObjectType.VOUCHER, plan=plan
        )
        context = mock_send.call_args.kwargs["context"]
        self.assertTrue(context["plan_image_url"].startswith("https://"))
        self.assertIn("plan", context)

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credits_email_with_plan_absolute_image(self, mock_send):
        customer = self.make_customer("ce4@example.com")
        plan = make_plan(credits=100, image="https://cdn.example.com/a.png")
        CustomerHelper.send_credits_email(
            customer, 100, object_type=ObjectType.VOUCHER, plan=plan
        )
        context = mock_send.call_args.kwargs["context"]
        self.assertEqual(context["plan_image_url"], "https://cdn.example.com/a.png")

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credits_email_no_email(self, mock_send):
        customer = self.make_customer("ce5@example.com")
        customer.user.email = ""
        CustomerHelper.send_credits_email(customer, 10)
        mock_send.assert_not_called()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credit_purchase_paid_email(self, mock_send):
        # plan without image, so plan_image_url stays None
        customer = self.make_customer("cp1@example.com")
        plan = make_plan(credits=100, bonus=10)
        purchase = Mock()
        purchase.customer = customer
        purchase.plan = plan
        CustomerHelper.send_credit_purchase_paid_email(purchase)
        mock_send.assert_called_once()
        context = mock_send.call_args.kwargs["context"]
        self.assertEqual(context["total_credits"], 110)
        self.assertIsNone(context["plan_image_url"])

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credit_purchase_paid_email_absolute_image(self, mock_send):
        customer = self.make_customer("cp2@example.com")
        plan = make_plan(credits=100, image="https://cdn.example.com/x.png")
        purchase = Mock()
        purchase.customer = customer
        purchase.plan = plan
        CustomerHelper.send_credit_purchase_paid_email(purchase)
        context = mock_send.call_args.kwargs["context"]
        self.assertEqual(context["plan_image_url"], "https://cdn.example.com/x.png")

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credit_purchase_paid_email_relative_image(self, mock_send):
        customer = self.make_customer("cp4@example.com")
        plan = make_plan(credits=100, image="images/plan/test.png")
        purchase = Mock()
        purchase.customer = customer
        purchase.plan = plan
        CustomerHelper.send_credit_purchase_paid_email(purchase)
        context = mock_send.call_args.kwargs["context"]
        self.assertTrue(context["plan_image_url"].startswith("https://"))
        self.assertIn("images/plan/test.png", context["plan_image_url"])

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_credit_purchase_paid_email_no_email(self, mock_send):
        customer = self.make_customer("cp3@example.com")
        customer.user.email = ""
        purchase = Mock()
        purchase.customer = customer
        CustomerHelper.send_credit_purchase_paid_email(purchase)
        mock_send.assert_not_called()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_product_purchase_paid_email(self, mock_send):
        customer = self.make_customer("pp1@example.com")
        purchase = Mock()
        purchase.customer = customer
        CustomerHelper.send_product_purchase_paid_email(purchase)
        mock_send.assert_called_once()

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_product_purchase_paid_email_no_email(self, mock_send):
        customer = self.make_customer("pp2@example.com")
        customer.user.email = ""
        purchase = Mock()
        purchase.customer = customer
        CustomerHelper.send_product_purchase_paid_email(purchase)
        mock_send.assert_not_called()

    def test_update_customer_credits(self):
        customer = self.make_customer("uc1@example.com", credits=10)
        CustomerHelper.update_customer_credits(customer.id, 5)
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 15)

    def test_update_customer_credits_zero_returns_false(self):
        customer = self.make_customer("uc2@example.com", credits=10)
        result = CustomerHelper.update_customer_credits(customer.id, 0)
        self.assertFalse(result)
        customer.refresh_from_db()
        self.assertEqual(customer.credits, 10)

    def test_generate_and_reset_recovery_token(self):
        customer = self.make_customer("rt1@example.com")
        token = CustomerHelper.generate_recovery_token(customer)
        customer.refresh_from_db()
        self.assertEqual(customer.recovery_token, token)

        CustomerHelper.reset_recovery_token(customer)
        customer.refresh_from_db()
        self.assertIsNone(customer.recovery_token)

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_password_recovery_email(self, mock_send):
        customer = self.make_customer("pr1@example.com")
        result = CustomerHelper.send_password_recovery_email(customer)
        self.assertTrue(result)
        mock_send.assert_called_once()
        customer.refresh_from_db()
        self.assertIsNotNone(customer.recovery_token)

    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_password_recovery_email_no_email(self, mock_send):
        customer = self.make_customer("pr2@example.com")
        customer.recovery_token = None
        # blank the email after token gets generated
        with patch.object(type(customer.user), "email", ""):
            pass
        customer.user.email = ""
        result = CustomerHelper.send_password_recovery_email(customer)
        self.assertFalse(result)
        mock_send.assert_not_called()

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=True)
    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_activation_email(self, mock_send):
        customer = self.make_customer("ae1@example.com")
        result = CustomerHelper.send_activation_email(customer)
        self.assertTrue(result)
        mock_send.assert_called_once()

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=True)
    @patch("apps.customer.helpers.EmailHelper.send_email_async")
    def test_send_activation_email_no_email(self, mock_send):
        customer = self.make_customer("ae2@example.com")
        customer.user.email = ""
        result = CustomerHelper.send_activation_email(customer)
        self.assertIsNone(result)
        mock_send.assert_not_called()

    @override_settings(CUSTOMER_ACTIVATION_REQUIRED=True)
    @patch("apps.customer.helpers.CustomerHelper.send_signup_email")
    def test_activate_account_success(self, mock_signup):
        customer = self.make_customer("act1@example.com")
        customer.user.is_active = False
        customer.user.save()
        token = customer.activate_token

        result = CustomerHelper.activate_account(token)
        self.assertIsNotNone(result)
        customer.refresh_from_db()
        customer.user.refresh_from_db()
        self.assertTrue(customer.user.is_active)
        self.assertIsNone(customer.activate_token)
        mock_signup.assert_called_once()

    def test_activate_account_not_found(self):
        self.assertIsNone(CustomerHelper.activate_account(uuid.uuid4()))
