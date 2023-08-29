from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from account import filters, forms, models


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "status",
        "logged_at",
    )

    list_display_links = (
        "id",
        "name",
        "email",
        "status",
        "logged_at",
    )

    list_filter = [
        filters.NameFilter,
        "status",
    ]

    list_per_page = 10

    form = forms.CustomerAdminForm

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        return qs


admin.site.register(models.Customer, CustomerAdmin)
