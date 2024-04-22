from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneFormField

from apps.customers.enums import CustomerGender
from apps.customers.models import Customer
from apps.languages.models import Language
from pyaa.fields import OnlyNumberCharField
from pyaa.settings import DEFAULT_TIME_ZONE


class CustomerSignupForm(SignupForm):
    mobile_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("model.field.mobile-phone"),
    )

    gender = forms.ChoiceField(
        label=_("model.field.gender"),
        choices=CustomerGender.choices,
        initial=CustomerGender.NONE,
        required=True,
    )

    language = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        required=True,
        label=_("model.field.language"),
        empty_label=None,
    )

    timezone = TimeZoneFormField(
        label=_("model.field.timezone"),
        required=True,
        initial=DEFAULT_TIME_ZONE,
    )

    def save(self, request):
        user = super(CustomerSignupForm, self).save(request)

        Customer.objects.create(
            user=user,
            mobile_phone=self.cleaned_data["mobile_phone"],
            gender=self.cleaned_data["gender"],
            language=self.cleaned_data["language"],
            timezone=self.cleaned_data["timezone"],
        )

        return user
