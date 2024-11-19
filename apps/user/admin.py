from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
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
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = ("id", "email", "first_name", "last_name", "is_staff")
    list_display_links = ("id", "email", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-id",)
