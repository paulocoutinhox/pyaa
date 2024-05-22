from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.customer import filters, forms, models


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_name",
        "user_email",
        "user_is_active",
    )

    list_display_links = (
        "id",
        "user_name",
        "user_email",
    )

    list_filter = [
        filters.NameFilter,
        filters.EmailFilter,
        "user",
    ]

    list_per_page = 10

    ordering = ("-id",)

    autocomplete_fields = ["user", "language"]

    form = forms.CustomerAdminForm

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        return qs.select_related("user")

    @admin.display(
        ordering="user__first_name",
        description=_("model.field.name"),
    )
    def user_name(self, obj):
        full_name = "%s %s" % (obj.user.first_name, obj.user.last_name)
        full_name = full_name.strip()
        return full_name

    @admin.display(
        ordering="user__email",
        description=_("model.field.email"),
    )
    def user_email(self, obj):
        return obj.user.email

    @admin.display(
        boolean=True,
        ordering="user__is_active",
        description=_("model.field.is_active"),
    )
    def user_is_active(self, obj):
        return obj.user.is_active


admin.site.register(models.Customer, CustomerAdmin)
