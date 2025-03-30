from django import forms
from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer
from apps.shop.enums import CheckoutStep, ObjectType, PaymentGateway
from apps.shop.models import Plan


class CheckoutForm(forms.Form):

    checkout_step = CheckoutStep.CHECKOUT

    gateway = ""
    gateway_key = ""
    gateway_code = ""

    object_type = ""
    object_id = 0

    description = ""
    title = ""
    photo_url = ""
    price = 0.0
    discount = 0.0
    shipping_price = 0.0
    total_price = 0.0

    shipping_description = ""
    address_description = ""
    delivery_description = ""

    show_shipping_data = False
    show_delivery_data = False
    show_address_data = False
    show_discount_data = False
    show_price_data = False

    back_url = None

    customer: Customer = None

    options = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={"input_type": "select"}),
        label="",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_for_subscription(self, plan: Plan, customer: Customer):
        self.gateway = PaymentGateway.MERCADO_PAGO
        self.title = _("checkout.description.subscription")
        self.description = plan.name
        self.object_type = ObjectType.SUBSCRIPTION
        self.object_id = plan.id

        self.customer = customer

        self.photo_url = plan.get_image_url()
        self.price = plan.price
        self.discount = 0.0
        self.shipping_price = 0.0
        self.total_price = plan.price

        self.show_shipping_data = False
        self.show_delivery_data = False
        self.show_address_data = False
        self.show_discount_data = False
        self.show_price_data = False

    def create_for_credit_purchase(self, plan: Plan, customer: Customer):
        self.gateway = PaymentGateway.MERCADO_PAGO
        self.description = _("checkout.description.credit-purchase")
        self.object_type = ObjectType.CREDIT_PURCHASE
        self.object_id = plan.id

        self.customer = customer

        self.title = plan.name
        self.photo_url = plan.get_image_url()
        self.price = plan.price
        self.discount = 0.0
        self.shipping_price = 0.0
        self.total_price = plan.price

        self.show_shipping_data = False
        self.show_delivery_data = False
        self.show_address_data = False
        self.show_discount_data = False
        self.show_price_data = False

    def clean(self):
        cleaned_data = super().clean()

        if self.checkout_step == CheckoutStep.CHECKOUT:
            object_type = self.object_type

            if object_type == ObjectType.SUBSCRIPTION:
                # validate subscription if needed
                pass
            elif object_type == ObjectType.CREDIT_PURCHASE:
                # validate credit purchase if needed
                pass

        return cleaned_data
