from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer, CustomerCredit
from apps.shop.enums import CreditType, ObjectType, PlanType
from apps.shop.models import CreditPurchase, Plan
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
                CustomerHelper.add_credits(customer, plan)

    @staticmethod
    @transaction.atomic
    def add_credits(customer, plan, object_id=0, object_type=None):
        # determine credit amount based on the plan
        amount = plan.credits

        if amount <= 0:
            return None

        # calculate expiration date for the credits
        if plan.expire_after:
            expire_at = datetime.now(timezone.utc) + timedelta(
                seconds=plan.expire_after
            )
        else:
            expire_at = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        # set credit type based on plan type
        credit_type = CreditType.PAID

        if plan.plan_type == PlanType.VOUCHER:
            credit_type = CreditType.BONUS

        # create customer credit record
        customer_credit = CustomerCredit.objects.create(
            site=Site.objects.get_current(),
            customer=customer,
            object_id=object_id,
            object_type=object_type,
            credit_type=credit_type,
            amount=amount,
            price=plan.price,
            expire_at=expire_at,
            plan_id=plan.id,
        )

        Customer.objects.filter(id=customer.id).update(
            credits=F("credits") + amount,
        )

        # if the plan includes bonus, add extra bonus credits
        if plan.bonus:
            bonus_amount = plan.bonus

            if plan.bonus_expire_after:
                bonus_expire_at = datetime.now(timezone.utc) + timedelta(
                    seconds=plan.bonus_expire_after
                )

                # make extra bonus expire 1 second earlier if it shares the same validity as the credit
                if bonus_expire_at.replace(microsecond=0) == expire_at.replace(
                    microsecond=0
                ):
                    bonus_expire_at -= timedelta(seconds=1)
            else:
                bonus_expire_at = datetime(
                    9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc
                )

            CustomerCredit.objects.create(
                site=Site.objects.get_current(),
                customer=customer,
                object_id=object_id,
                object_type=object_type,
                credit_type=CreditType.BONUS,
                amount=bonus_amount,
                price=0,
                expire_at=bonus_expire_at,
                plan_id=plan.id,
            )

            Customer.objects.filter(id=customer.id).update(
                credits=F("credits") + bonus_amount,
            )

        # link customer credit with the transaction, if applicable
        if object_type == ObjectType.CREDIT_PURCHASE:
            CreditPurchase.objects.filter(id=object_id).update(
                customer_credit=customer_credit
            )

        # send email
        CustomerHelper.send_credits_mail(customer, plan)

        return customer_credit

    @staticmethod
    @transaction.atomic
    def add_bonus_credits(customer, amount, expire_after=None):
        """
        Add bonus credits to a customer without requiring a plan

        :param customer: the customer to add credits to
        :param amount: the number of bonus credits to add
        :param expire_after: seconds until expiration (optional)
        :return: the created customer credit object
        """
        if amount <= 0:
            return None

        # calculate expiration date for the credits
        if expire_after:
            expire_at = datetime.now(timezone.utc) + timedelta(seconds=expire_after)
        else:
            expire_at = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        # create customer credit record
        customer_credit = CustomerCredit.objects.create(
            site=Site.objects.get_current(),
            customer=customer,
            object_id=None,
            object_type=ObjectType.BONUS,
            credit_type=CreditType.BONUS,
            amount=amount,
            price=0,
            expire_at=expire_at,
            plan_id=None,
        )

        Customer.objects.filter(id=customer.id).update(
            credits=F("credits") + amount,
        )

        # send email notification
        CustomerHelper.send_bonus_credits_mail(customer, amount)

        return customer_credit

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
    def send_credits_mail(customer, plan):
        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = customer.site

        # set the subject
        subject = _("email.credits.subject")

        # set recipient
        recipient_list = [customer_email]

        # set context
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
                plan_image_url = f"https://{current_site.domain}{plan.image.url}"

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
        }

        MailHelper.send_mail_async(
            subject=subject,
            to=recipient_list,
            template="emails/credits/credits_added.html",
            context=context,
            reply_to=[settings.DEFAULT_TO_EMAIL],
        )

    @staticmethod
    def send_bonus_credits_mail(customer, credits_amount):
        """
        Send email notification for bonus credits added to a customer

        :param customer: the customer who received the bonus credits
        :param credits_amount: the number of bonus credits added
        """
        # get the customer's email
        customer_email = customer.user.email

        if not customer_email:
            return

        # get the current site
        current_site = customer.site

        # set the subject
        subject = _("email.bonus-credits.subject")

        # set recipient
        recipient_list = [customer_email]

        # set context
        profile_path = reverse("account_credits")
        profile_url = f"https://{current_site.domain}{profile_path}"

        # absolute image url for bonus credits
        plan_image_url = (
            f"https://{current_site.domain}{settings.STATIC_URL}images/credit-bonus.png"
        )

        context = {
            "subject": subject,
            "customer": customer,
            "site": current_site,
            "profile_url": profile_url,
            "credits_amount": credits_amount,
            "plan_image_url": plan_image_url,
        }

        MailHelper.send_mail_async(
            subject=subject,
            to=recipient_list,
            template="emails/credits/bonus_credits_added.html",
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
