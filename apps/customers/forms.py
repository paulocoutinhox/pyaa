from django import forms
from django.utils.translation import gettext_lazy as _

from apps.customers import models
from pyaa.fields import OnlyNumberCharField


class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = models.Customer

        fields = [
            "user",
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

    def is_adding(self):
        if self.instance.pk is None:
            return True
        else:
            return False

    def validate_required_field(
        self, cleaned_data, field_name, message="This field is required."
    ):
        if field_name in cleaned_data and (
            cleaned_data[field_name] is None or cleaned_data[field_name] == ""
        ):
            self.add_error(field_name, self.error_class([message]))
