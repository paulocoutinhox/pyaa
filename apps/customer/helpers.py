from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.shop.enums import ObjectType
from apps.shop.models import CreditLog, Plan
from pyaa.helpers.mail import MailHelper


class CustomerHelper:
    @staticmethod
    @transaction.atomic
    def post_save(customer: Customer):
        # send email
        CustomerHelper.send_signup_mail(customer)

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
    ):
        """
        add credits to a customer based on either a plan or a direct amount value

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
            credit_amount = plan.credits

            if credit_amount <= 0:
                return False

            # update customer's credit balance
            Customer.objects.filter(id=customer.id).update(
                credits=F("credits") + credit_amount,
            )

            # refresh the customer instance to reflect the updated credits
            customer.refresh_from_db()

            # create customer credit
            customer_credit = CreditLog.objects.create(
                customer=customer,
                object_id=object_id,
                object_type=object_type,
                amount=credit_amount,
                is_refund=is_refund,
                site=customer.site,
            )

            # send email for plan credits
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
                object_id=object_id,
                object_type=object_type,
                amount=amount,
                is_refund=is_refund,
                site=customer.site,
            )

            # send email for direct credit additions
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

        if user and hasattr(user, "customer"):
            return getattr(user.customer, "id", 0)

        return 0

    @staticmethod
    def send_signup_mail(customer):
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

        MailHelper.send_mail_async(
            subject=subject,
            to=recipient_list,
            template="emails/site/signup.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
        )

    @staticmethod
    def send_credits_email(customer, amount, object_type=None, plan=None):
        """
        send email notification for credits added to a customer

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

        template = "emails/credits/credits_added.html"

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
            plan_image_url = (
                f"https://{current_site.domain}{settings.STATIC_URL}images/no-image.png"
            )

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

        MailHelper.send_mail_async(
            subject=subject,
            to=recipient_list,
            template=template,
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
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

        MailHelper.send_mail_async(
            subject=subject,
            to=recipient_list,
            template="emails/credits/credit_purchase_paid.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
        )

    @staticmethod
    @transaction.atomic
    def update_customer_credits(customer_id, amount):
        """
        update customer credits without creating any log entries
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
