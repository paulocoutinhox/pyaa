from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField, ReCaptchaV3
from localflavor.br.forms import BRCPFField

from apps.customer import enums, models
from apps.customer.enums import CustomerGender
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
        try:
            with transaction.atomic():
                # update User fields
                self.user.first_name = self.cleaned_data["first_name"]
                self.user.last_name = self.cleaned_data["last_name"]
                self.user.email = self.cleaned_data["email"]
                self.user.cpf = self.cleaned_data["cpf"]
                self.user.mobile_phone = self.cleaned_data["mobile_phone"]
                self.user.save()

                # update Customer fields
                customer = self.user.customer
                customer.nickname = self.cleaned_data["nickname"]
                customer.gender = self.cleaned_data["gender"]
                customer.save()

            return True
        except IntegrityError as e:
            error_message = str(e)

            # Mapear erros de constraint para campos específicos
            if "user_unique_email" in error_message:
                self.add_error("email", _("error.email-already-used-by-other"))
            elif "user_unique_cpf" in error_message:
                self.add_error("cpf", _("error.cpf-already-used-by-other"))
            elif "user_unique_mobile_phone" in error_message:
                self.add_error(
                    "mobile_phone", _("error.mobile-phone-already-used-by-other")
                )
            else:
                # Erro genérico
                self.add_error(None, _("error.database-constraint-error"))

            return False
        except ProtectedError:
            self.add_error(None, _("error.protected-object-cannot-be-deleted"))
            return False
        except Exception as e:
            self.add_error(None, str(e))
            return False


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
