from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pyaa.mixins import ReadonlyLinksMixin

from .models import SiteProfile


class SiteProfileAdmin(ReadonlyLinksMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "site__domain",
    )

    list_display_links = (
        "id",
        "title",
        "site__domain",
    )

    search_fields = ["title"]

    readonly_fields = ("created_at", "updated_at")

    readonly_fields_links = ["site"]

    list_per_page = 10

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": ("site", "title"),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


admin.site.register(SiteProfile, SiteProfileAdmin)
