from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, Q
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField, ReCaptchaV3
from localflavor.br.forms import BRCPFField, BRStateChoiceField, BRZipCodeField

from apps.customer import enums, models
from apps.customer.enums import CustomerAddressType, CustomerGender
from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.language.helpers import LanguageHelper
from apps.user.helpers import UserHelper
from apps.user.models import User
from pyaa.fields import OnlyNumberCharField
from pyaa.mixins import SanitizeDigitFieldsMixin

User = get_user_model()


class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = models.Customer

        fields = [
            "site",
            "user",
            "gender",
            "avatar",
            "obs",
        ]


class CustomerAddressAdminForm(forms.ModelForm):
    class Meta:
        model = models.CustomerAddress
        fields = [
            "address_type",
            "address_line1",
            "address_line2",
            "street_number",
            "complement",
            "city",
            "state",
            "postal_code",
            "country_code",
        ]

    state = BRStateChoiceField(
        label=_("model.field.state"),
        required=True,
    )

    postal_code = BRZipCodeField(
        widget=forms.TextInput(attrs={"data-mask": "00000-000"}),
        label=_("model.field.postal-code"),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country_code"].widget.attrs["placeholder"] = "BR"
        self.fields["postal_code"].widget.attrs["placeholder"] = "00000-000"
        self.fields["state"].widget.attrs["placeholder"] = "SP"


class CustomerDeleteForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = []


class CustomerLoginForm(forms.Form):
    username = forms.CharField(
        label=_("model.field.login-username"),
        max_length=255,
        required=True,
        widget=forms.TextInput(),
    )

    password = forms.CharField(
        label=_("model.field.login-password"),
        max_length=255,
        required=True,
        widget=forms.PasswordInput(),
    )


class CustomerSignupForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_("model.field.first-name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(),
    )

    last_name = forms.CharField(
        label=_("model.field.last-name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(),
    )

    gender = forms.ChoiceField(
        label=_("model.field.gender"),
        choices=enums.CustomerGender.choices,
        initial=enums.CustomerGender.NONE,
        required=True,
    )

    email = forms.EmailField(
        label=_("model.field.email"),
        max_length=255,
        required=True,
        widget=forms.EmailInput(),
    )

    password = forms.CharField(
        label=_("model.field.password"),
        required=True,
        widget=forms.PasswordInput(),
    )

    accept_terms = forms.BooleanField(
        label=_("model.field.accept-terms"),
        required=True,
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        label=_("model.field.captcha"),
    )

    class Meta:
        model = Customer
        fields = ["gender"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields = {
            "first_name": self.fields["first_name"],
            "last_name": self.fields["last_name"],
            "gender": self.fields["gender"],
            "email": self.fields["email"],
            "password": self.fields["password"],
            "accept_terms": self.fields["accept_terms"],
            "captcha": self.fields["captcha"],
        }

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        cpf = cleaned_data.get("cpf")
        mobile_phone = cleaned_data.get("mobile_phone")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            cpf=cpf,
            mobile_phone=mobile_phone,
            site_id=Site.objects.get_current().id,
        )

        try:
            user.full_clean(exclude=["password"])
        except ValidationError as e:
            raise ValidationError(e.message_dict)

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data

        # user creation
        user = User.objects.create_user(
            username=None,
            password=cleaned_data.get("password"),
            email=cleaned_data.get("email"),
            cpf=cleaned_data.get("cpf"),
            mobile_phone=cleaned_data.get("mobile_phone"),
            first_name=cleaned_data.get("first_name"),
            last_name=cleaned_data.get("last_name"),
            site_id=Site.objects.get_current().id,
        )

        # customer creation
        customer = super().save(commit=False)
        customer.user = user
        customer.language = LanguageHelper.get_current()
        customer.timezone = settings.DEFAULT_TIME_ZONE

        if commit:
            customer.save()

        CustomerHelper.post_save(customer)

        return customer


class CustomerUpdateProfileForm(SanitizeDigitFieldsMixin, forms.Form):
    digit_only_fields = ["cpf"]

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

    email = forms.EmailField(
        label=_("model.field.email"),
        max_length=255,
        required=False,
    )

    cpf = BRCPFField(
        widget=forms.TextInput(attrs={"data-mask": "000.000.000-00"}),
        label=_("model.field.cpf"),
        required=False,
    )

    mobile_phone = OnlyNumberCharField(
        widget=forms.TextInput(attrs={"data-mask": "(00)0000-00009"}),
        required=False,
        label=_("model.field.mobile-phone"),
    )

    nickname = forms.CharField(
        label=_("model.field.nickname"),
        max_length=255,
        required=False,
    )

    gender = forms.ChoiceField(
        label=_("model.field.gender"),
        choices=CustomerGender.choices,
        initial=CustomerGender.NONE,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email
            self.fields["cpf"].initial = self.user.cpf
            self.fields["mobile_phone"].initial = self.user.mobile_phone

            if hasattr(self.user, "customer"):
                customer = self.user.customer
                self.fields["nickname"].initial = customer.nickname
                self.fields["gender"].initial = customer.gender

    def clean(self):
        cleaned_data = super().clean()

        # validate user fields using helper
        UserHelper.validate_unique_email(
            email=cleaned_data.get("email"),
            site_id=self.user.site_id,
            pk=self.user.pk,
        )

        UserHelper.validate_unique_cpf(
            cpf=cleaned_data.get("cpf"),
            site_id=self.user.site_id,
            pk=self.user.pk,
        )

        UserHelper.validate_unique_mobile_phone(
            mobile_phone=cleaned_data.get("mobile_phone"),
            site_id=self.user.site_id,
            pk=self.user.pk,
        )

        return cleaned_data

    def save(self):
        # update user fields
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        self.user.cpf = self.cleaned_data["cpf"]
        self.user.mobile_phone = self.cleaned_data["mobile_phone"]
        self.user.save()

        # update customer fields
        customer = self.user.customer
        customer.nickname = self.cleaned_data["nickname"]
        customer.gender = self.cleaned_data["gender"]
        customer.save()

        return True


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


class CustomerUpdateAddressForm(SanitizeDigitFieldsMixin, forms.ModelForm):
    class Meta:
        model = models.CustomerAddress
        fields = [
            "address_line1",
            "address_line2",
            "street_number",
            "complement",
            "city",
            "state",
            "postal_code",
            "country_code",
        ]

    digit_only_fields = ["postal_code"]

    state = BRStateChoiceField(
        label=_("model.field.state"),
        required=True,
    )

    postal_code = BRZipCodeField(
        widget=forms.TextInput(attrs={"data-mask": "00000-000"}),
        label=_("model.field.postal-code"),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop("customer", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        address = super().save(commit=False)

        if self.customer:
            # try to find existing address for this customer and type
            existing_address = models.CustomerAddress.objects.filter(
                customer=self.customer, address_type=CustomerAddressType.MAIN
            ).first()

            if existing_address:
                # update existing address
                existing_address.address_line1 = self.cleaned_data["address_line1"]
                existing_address.address_line2 = self.cleaned_data["address_line2"]
                existing_address.street_number = self.cleaned_data["street_number"]
                existing_address.complement = self.cleaned_data["complement"]
                existing_address.city = self.cleaned_data["city"]
                existing_address.state = self.cleaned_data["state"]
                existing_address.postal_code = self.cleaned_data["postal_code"]
                existing_address.country_code = self.cleaned_data["country_code"]

                if commit:
                    existing_address.save()

                return existing_address
            else:
                # create new address
                address.customer = self.customer
                address.address_type = CustomerAddressType.MAIN

                if commit:
                    address.save()

                return address

        return address


class CustomerPasswordRecoveryForm(forms.Form):
    identifier = forms.CharField(
        label=_("model.field.recovery-identifier"),
        max_length=255,
        required=True,
        widget=forms.TextInput(),
        help_text=_("model.field.recovery-identifier.help"),
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        label=_("model.field.captcha"),
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")

        if identifier:
            # try to find user by
            user = User.objects.filter(
                Q(email=identifier) | Q(cpf=identifier) | Q(mobile_phone=identifier),
                site=Site.objects.get_current(),
            ).first()

            if user:
                cleaned_data["user"] = user

        return cleaned_data


class CustomerResetPasswordForm(forms.Form):
    password = forms.CharField(
        label=_("model.field.new-password"),
        max_length=255,
        required=True,
        widget=forms.PasswordInput(),
    )

    password_confirmation = forms.CharField(
        label=_("model.field.confirm-password"),
        max_length=255,
        required=True,
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation:
            if password != password_confirmation:
                raise ValidationError(
                    {"password_confirmation": _("error.passwords-do-not-match")}
                )

        return cleaned_data
