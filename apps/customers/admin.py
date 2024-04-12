from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.customers import filters, forms, models


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_name",
        "user_email",
        # "get_user_email",
        # "user.email",
        # "user.status",
        # "logged_at",
    )

    list_display_links = (
        "id",
        "user_name",
        "user_email",
        # "email",
        # "status",
        # "logged_at",
    )

    list_filter = [
        filters.NameFilter,
        "user",
        # "status",
    ]

    list_per_page = 10

    form = forms.CustomerAdminForm

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        return qs.select_related("user")

    def user_name(self, obj):
        full_name = "%s %s" % (obj.user.first_name, obj.user.last_name)
        full_name = full_name.strip()
        return full_name

    def user_email(self, obj):
        return obj.user.email

    user_name.admin_order_field = "user__first_name"
    user_name.short_description = _("model.field.name")

    user_email.admin_order_field = "user__email"
    user_email.short_description = _("model.field.email")


admin.site.register(models.Customer, CustomerAdmin)
