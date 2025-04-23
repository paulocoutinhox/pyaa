from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from localflavor.br.forms import BRCPFField

from pyaa.fields import OnlyNumberCharField
from pyaa.mixins import SanitizeDigitFieldsMixin

User = get_user_model()


class UserAdminForm(SanitizeDigitFieldsMixin, UserChangeForm):
    digit_only_fields = ["cpf"]

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

    class Meta:
        model = User
        fields = "__all__"


class UserAdminAddForm(SanitizeDigitFieldsMixin, AdminUserCreationForm):
    digit_only_fields = ["cpf"]

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

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminForm
    add_form = UserAdminAddForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "site",
                    "email",
                    "cpf",
                    "mobile_phone",
                    "password",
                )
            },
        ),
        (
            _("admin.fieldsets.personal-info"),
            {
                "fields": ("first_name", "last_name"),
            },
        ),
        (
            _("admin.fieldsets.permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "site",
                    "first_name",
                    "last_name",
                    "email",
                    "cpf",
                    "mobile_phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    list_display = (
        "id",
        "site",
        "first_name",
        "last_name",
        "email",
        "cpf",
        "mobile_phone",
        "is_staff",
    )

    list_display_links = (
        "id",
        "site",
        "first_name",
        "last_name",
        "email",
        "cpf",
        "mobile_phone",
        "is_staff",
    )

    search_fields = ("first_name", "last_name", "email", "cpf", "mobile_phone")
    list_filter = ("site", "is_staff", "is_active")

    ordering = ("-id",)
