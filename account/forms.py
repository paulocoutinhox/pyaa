from django import forms
from django.utils.translation import gettext_lazy as _

from account import models
from main.fields import OnlyNumberCharField


class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = models.Customer

        fields = [
            "name",
            "email",
            "password",
            "confirm_password",
            "language",
            "mobile_phone",
            "home_phone",
            "status",
            "gender",
            "avatar",
            "obs",
            "timezone",
        ]

    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label=_("form.label.password"),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label=_("form.label.confirm-password"),
    )

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

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if self.is_adding():
            if password and confirm_password:
                if not password == confirm_password:
                    self.add_error(
                        "confirm_password",
                        _("validation.password-not-match"),
                    )
            else:
                self.validate_required_field(cleaned_data, "password")
                self.validate_required_field(cleaned_data, "confirm_password")
        else:
            if not password == confirm_password:
                self.add_error(
                    "confirm_password",
                    _("validation.password-not-match"),
                )

        return cleaned_data

    def is_adding(self):
        if self.instance.pk is None:
            return True
        else:
            return False

    def validate_required_field(
        self, cleaned_data, field_name, message=_("This field is required.")
    ):
        if field_name in cleaned_data and (
            cleaned_data[field_name] is None or cleaned_data[field_name] == ""
        ):
            self.add_error(field_name, self.error_class([message]))

    def save(self, commit=False):
        instance: models.Customer = super(CustomerAdminForm, self).save(commit=commit)

        # setup initial data
        instance.setup_initial_data()

        # verify if need create password hash
        password = self.cleaned_data["password"]

        if password:
            instance.setup_password_data(
                password=self.cleaned_data["password"],
            )

        # save
        instance.save()
        return instance
