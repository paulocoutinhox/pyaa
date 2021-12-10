from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from language import filters, models


class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = [
        filters.NameFilter,
    ]

    list_per_page = 10

    def get_queryset(self, request):
        qs = super(LanguageAdmin, self).get_queryset(request)
        return qs


admin.site.register(models.Language, LanguageAdmin)
