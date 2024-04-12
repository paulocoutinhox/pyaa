from django import forms
from django.utils.translation import gettext_lazy as _

from apps.customers import models
from pyaa.fields import OnlyNumberCharField


class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = models.Customer

        fields = [
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "avatar",
            "obs",
            "timezone",
        ]

    mobile_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("form.label.mobile-phone"),
    )

    home_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("form.label.home-phone"),
    )
