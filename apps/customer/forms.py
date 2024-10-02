from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneFormField

from apps.customer import models
from apps.customer.enums import CustomerGender
from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.language.helpers import LanguageHelper
from apps.language.models import Language
from pyaa.fields import OnlyNumberCharField

User = get_user_model()


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
            "credits",
            "timezone",
            "obs",
        ]

    mobile_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("model.field.mobile-phone"),
    )

    home_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("model.field.home-phone"),
    )

    def __init__(self, *args, **kwargs):
        super(CustomerAdminForm, self).__init__(*args, **kwargs)

        # disable user field if it is not adding
        if self.instance and self.instance.pk:
            self.fields["user"].disabled = True

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


class CustomerDeleteForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = []


class CustomerSignupForm(SignupForm):
    def save(self, request):
        user = super(CustomerSignupForm, self).save(request)

        language = LanguageHelper.get_current()
        timezone = settings.DEFAULT_TIME_ZONE

        customer = Customer.objects.create(
            user=user,
            language=language,
            timezone=timezone,
        )

        CustomerHelper.post_save(customer)

        return user


class CustomerUpdateProfileForm(forms.Form):
    first_name = forms.CharField(
        label=_("model.field.first-name"),
        max_length=150,
        required=False,
    )

    last_name = forms.CharField(
        label=_("model.field.last-name"),
        max_length=150,
        required=False,
    )

    mobile_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("model.field.mobile-phone"),
    )

    home_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-0000"}),
        required=False,
        label=_("model.field.home-phone"),
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
        initial=settings.DEFAULT_TIME_ZONE,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(CustomerUpdateProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name

            if hasattr(user, "customer"):
                customer = user.customer
                self.fields["language"].initial = customer.language
                self.fields["mobile_phone"].initial = customer.mobile_phone
                self.fields["home_phone"].initial = customer.home_phone
                self.fields["gender"].initial = customer.gender
                self.fields["timezone"].initial = customer.timezone

    def save(self, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        customer = user.customer
        customer.language = self.cleaned_data["language"]
        customer.mobile_phone = self.cleaned_data["mobile_phone"]
        customer.home_phone = self.cleaned_data["home_phone"]
        customer.gender = self.cleaned_data["gender"]
        customer.timezone = self.cleaned_data["timezone"]
        customer.save()


class CustomerUpdateAvatarForm(forms.Form):
    avatar = forms.ImageField(required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(CustomerUpdateAvatarForm, self).__init__(*args, **kwargs)

        if user:
            if hasattr(user, "customer"):
                customer = user.customer
                self.fields["avatar"].initial = customer.avatar

    def save(self, user):
        customer = user.customer
        customer.avatar = self.cleaned_data["avatar"]
        customer.save()
