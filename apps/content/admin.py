from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.content import filters, models


class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "tag",
        "language",
        "active",
    )

    list_display_links = (
        "id",
        "title",
        "tag",
        "language",
        "active",
    )

    list_filter = [
        filters.TitleFilter,
    ]

    list_per_page = 10

    ordering = ("-id",)

    search_fields = ["title"]

    autocomplete_fields = ["language"]

    def get_queryset(self, request):
        qs = super(ContentAdmin, self).get_queryset(request)
        return qs


admin.site.register(models.Content, ContentAdmin)
