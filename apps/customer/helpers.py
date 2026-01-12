import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.language.helpers import LanguageHelper
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog, Plan
from pyaa.helpers.email import EmailHelper


class CustomerHelper:
    @staticmethod
    @transaction.atomic
    def post_save(customer: Customer):
        # check if account activation is required
        if settings.CUSTOMER_ACTIVATION_REQUIRED:
            # send activation email
            CustomerHelper.send_activation_email(customer)
        else:
            # send welcome email
            CustomerHelper.send_signup_email(customer)

        # add initial credits
        plan_id = settings.CUSTOMER_SIGNUP_PLAN

        if plan_id:
            plan = Plan.objects.filter(id=plan_id).first()

            if plan:
                success = CustomerHelper.add_credits(
                    customer,
                    plan=plan,
                    object_type=ObjectType.VOUCHER,
                    object_id=plan.id,
                )

                # refresh customer if credits were added successfully
                if success:
                    customer.refresh_from_db()

        return customer

    @staticmethod
    @transaction.atomic
    def add_credits(
        customer,
        amount=None,
        plan=None,
        is_refund=False,
        object_id=0,
        object_type=None,
        send_email=True,
    ):
        """
        Add credits to a customer based on either a plan or a direct amount value

        :param customer: the customer to add credits to
        :param amount: the direct amount of credits to add (used if plan is None)
        :param plan: the plan object containing credits information (takes precedence over amount)
        :param is_refund: whether this is a refund operation
        :param object_id: the ID of the related object (for logging)
        :param object_type: the type of the related object (for logging)
        :return: boolean indicating whether credits were successfully added
        """
        # if a plan is provided, use its credits value
        if plan:
            # determine credit amount based on the plan
            credit_amount = plan.credits or 0

            if credit_amount <= 0:
                return False

            # update customer's credit balance
            Customer.objects.filter(id=customer.id).update(
                credits=F("credits") + credit_amount,
            )

            # refresh the customer instance to reflect the updated credits
            customer.refresh_from_db()

            # create customer credit
            CreditLog.objects.create(
                customer=customer,
                object_type=object_type,
                object_id=object_id,
                amount=credit_amount,
                is_refund=is_refund,
                site=customer.site,
            )

            # send email for plan credits
            if send_email:
                CustomerHelper.send_credits_email(
                    customer,
                    credit_amount,
                    object_type=object_type,
                    plan=plan,
                )

            # if the plan includes bonus, add extra bonus credits
            if plan.bonus and plan.bonus > 0:
                bonus_amount = plan.bonus

                # update customer's credit balance with bonus
                Customer.objects.filter(id=customer.id).update(
                    credits=F("credits") + bonus_amount,
                )

                # refresh the customer instance to reflect the updated credits
                customer.refresh_from_db()

                # add bonus log
                CreditLog.objects.create(
                    customer=customer,
                    object_id=object_id,
                    object_type=ObjectType.BONUS,
                    amount=bonus_amount,
                    is_refund=False,
                    site=customer.site,
                )

                # send email notification for bonus
                if send_email:
                    CustomerHelper.send_credits_email(
                        customer,
                        bonus_amount,
                        object_type=ObjectType.BONUS,
                    )

            return True

        # if direct amount is provided
        elif amount is not None:
            if amount == 0:
                return False

            # ensure credits is treated as 0 if it's null
            current_credits = Coalesce(F("credits"), Value(0))

            # atomically check and update credits
            if amount < 0:
                # attempt to deduct credits only if sufficient credits are available
                updated_rows = Customer.objects.filter(
                    id=customer.id,
                    credits__gte=abs(amount),
                ).update(
                    credits=current_credits + amount,
                )

                if updated_rows == 0:
                    # not enough credits to deduct
                    return False
            else:
                # add credits without any condition
                Customer.objects.filter(id=customer.id).update(
                    credits=current_credits + amount,
                )

            # refresh the customer instance to reflect the updated credits
            customer.refresh_from_db()

            # create log entry
            CreditLog.objects.create(
                customer=customer,
                object_type=object_type,
                object_id=object_id,
                amount=amount,
                is_refund=is_refund,
                site=customer.site,
            )

            # send email for direct credit additions
            if send_email:
                CustomerHelper.send_credits_email(
                    customer,
                    amount,
                    object_type=object_type,
                )

            return True

        # if neither plan nor amount is provided
        return False

    @staticmethod
    def validate_unique_nickname(
        nickname, site_id, exclude_pk=None, error_class=ValidationError
    ):
        if (
            Customer.objects.filter(nickname=nickname, site_id=site_id)
            .exclude(pk=exclude_pk)
            .exists()
        ):
            raise error_class({"nickname": _("error.nickname-already-used-by-other")})

    @staticmethod
    def get_customer_id_from_request(request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated and user.has_customer():
            return user.customer.id

        return 0

    @staticmethod
    def send_signup_email(customer):
        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = Site.objects.get_current()

        # set the subject with site name for translation
        subject = _("email.signup.subject") % {"site_name": current_site.name}

        # set recipient to customer's email
        recipient_list = [customer_email]

        # set context
        profile_path = reverse("account_profile")
        profile_url = f"https://{current_site.domain}{profile_path}"

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "profile_url": profile_url,
        }

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template="emails/account/signup.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

    @staticmethod
    def send_credits_email(customer, amount, object_type=None, plan=None):
        """
        Send email notification for credits added to a customer

        :param customer: the customer who received the credits
        :param amount: the number of credits added
        :param object_type: the type of object related to this credit operation
        :param plan: the plan used to add credits (optional)
        """
        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = customer.site

        # determine the subject and template based on credit type
        if object_type == ObjectType.BONUS:
            subject = _("email.bonus-credits-added.subject")
        else:
            subject = _("email.credits-added.subject")

        template = "emails/credit/credit_added.html"

        # set recipient
        recipient_list = [customer_email]

        # set context
        profile_path = reverse("account_credits")
        profile_url = f"https://{current_site.domain}{profile_path}"

        # determine image URL
        plan_image_url = None

        if plan and plan.image:
            # if plan has image, use it
            plan_image = str(plan.image)
            if plan_image.startswith(("http://", "https://")):
                plan_image_url = plan_image
            else:
                plan_image_url = f"https://{current_site.domain}{plan.image.url}"
        elif object_type == ObjectType.BONUS:
            # use bonus image
            plan_image_url = f"https://{current_site.domain}{settings.STATIC_URL}images/credit-bonus.png"
        else:
            # use standard credit image
            plan_image_url = f"https://{current_site.domain}{settings.STATIC_URL}images/no-image-s.png"

        # build context with all possible parameters
        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "profile_url": profile_url,
            "credits_amount": amount,
            "plan_image_url": plan_image_url,
            "object_type": object_type,
        }

        # add plan-specific context if available
        if plan:
            context.update(
                {
                    "plan": plan,
                    "bonus_amount": plan.bonus,
                    "total_credits": (plan.credits or 0) + (plan.bonus or 0),
                }
            )

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template=template,
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

    @staticmethod
    def send_credit_purchase_paid_email(purchase):
        """
        Send confirmation email for a credit purchase

        :param purchase: the credit purchase object
        """
        # get the customer's email
        customer = purchase.customer
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = customer.site

        # set the subject
        subject = _("email.credit-purchase-paid.subject")

        # set recipient
        recipient_list = [customer_email]

        # set context
        plan = purchase.plan

        profile_path = reverse("account_credits")
        profile_url = f"https://{current_site.domain}{profile_path}"

        total_credits = (plan.credits or 0) + (plan.bonus or 0)

        # ensure plan_image_url is absolute
        plan_image_url = None

        if plan and plan.image:
            plan_image = str(plan.image)

            if plan_image.startswith(("http://", "https://")):
                plan_image_url = plan_image
            else:
                plan_image_url = f"https://{current_site.domain}{plan_image.url}"

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "profile_url": profile_url,
            "plan": plan,
            "credits_amount": plan.credits,
            "bonus_amount": plan.bonus,
            "total_credits": total_credits,
            "plan_image_url": plan_image_url,
            "purchase": purchase,
        }

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template="emails/credit/credit_purchase_paid.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

    @staticmethod
    def send_product_purchase_paid_email(purchase):
        """
        Send confirmation email for a product purchase

        :param purchase: the product purchase object
        """
        # get the customer's email
        customer = purchase.customer
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = customer.site

        # set the subject
        subject = _("email.product-purchase-paid.subject")

        # set recipient
        recipient_list = [customer_email]

        # set context
        profile_path = reverse("account_product_purchases")
        profile_url = f"https://{current_site.domain}{profile_path}"

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "profile_url": profile_url,
            "purchase": purchase,
        }

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template="emails/product/product_purchase_paid.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

    @staticmethod
    @transaction.atomic
    def update_customer_credits(customer_id, amount):
        """
        Update customer credits without creating any log entries
        used specifically by admin interfaces to avoid duplicate logs

        :param customer: the customer whose credits to update
        :param amount: the amount to add (positive) or remove (negative)
        """
        if amount == 0:
            return False

        # ensure credits is treated as 0 if it's null
        current_credits = Coalesce(F("credits"), Value(0))

        # update credits
        Customer.objects.filter(id=customer_id).update(
            credits=current_credits + amount,
        )

    @staticmethod
    @transaction.atomic
    def generate_recovery_token(customer):
        """
        Generate a new recovery token for a customer

        :param customer: the customer object
        :return: the new recovery token UUID
        """
        # create a new recovery token
        new_token = uuid.uuid4()

        # save it to the customer
        customer.recovery_token = new_token
        customer.save(update_fields=["recovery_token"])

        return new_token

    @staticmethod
    def reset_recovery_token(customer):
        """
        Reset the recovery token to null after it's been used

        :param customer: the customer object
        """
        customer.recovery_token = None
        customer.save(update_fields=["recovery_token"])

    @staticmethod
    def send_password_recovery_email(customer):
        """
        Send password recovery email to a customer

        :param customer: the customer who requested password recovery
        """
        # generate a new recovery token
        recovery_token = CustomerHelper.generate_recovery_token(customer)

        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return False

        # get the current site
        current_site = customer.site

        # set the subject
        subject = _("email.password-recovery.subject")

        # set recipient
        recipient_list = [customer_email]

        # build the recovery URL
        recovery_path = reverse(
            "account_reset_password", kwargs={"token": recovery_token}
        )
        recovery_url = f"https://{current_site.domain}{recovery_path}"

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "recovery_url": recovery_url,
            "token": recovery_token,
        }

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template="emails/account/password_recovery.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

        return True

    @staticmethod
    def send_activation_email(customer):
        """
        Send account activation email to a customer

        :param customer: the customer who just signed up
        """
        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = Site.objects.get_current()

        # set the subject
        subject = _("email.activation.subject")

        # set recipient to customer's email
        recipient_list = [customer_email]

        # build the activation URL
        activation_path = reverse(
            "account_activate", kwargs={"token": customer.activate_token}
        )
        activation_url = f"https://{current_site.domain}{activation_path}"

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "activation_url": activation_url,
            "token": customer.activate_token,
        }

        language = LanguageHelper.get_language_code(customer)

        EmailHelper.send_email_async(
            subject=subject,
            to=recipient_list,
            template="emails/account/activation.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
            language=language,
        )

        return True

    @staticmethod
    @transaction.atomic
    def activate_account(token):
        """
        Activate a customer account using an activation token

        :param token: the activation token (UUID)
        :return: the customer object if found and activated, None otherwise
        """
        try:
            # find customer with matching activation token
            customer = Customer.objects.select_for_update().get(activate_token=token)

            # activate the user
            user = customer.user
            user.is_active = True
            user.save(update_fields=["is_active"])

            # clear the activation token
            customer.activate_token = None
            customer.save(update_fields=["activate_token"])

            # send the welcome email
            CustomerHelper.send_signup_email(customer)

            return customer
        except (Customer.DoesNotExist, ValueError):
            return None
