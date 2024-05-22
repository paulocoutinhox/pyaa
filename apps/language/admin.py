from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.language import filters, models


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

    ordering = ("-id",)

    search_fields = ["name"]

    def get_queryset(self, request):
        qs = super(LanguageAdmin, self).get_queryset(request)
        return qs

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if "autocomplete" in request.path:
            queryset = queryset.order_by("name")

        return queryset, use_distinct


admin.site.register(models.Language, LanguageAdmin)
