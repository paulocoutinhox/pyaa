from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.content import filters, models
from apps.language.models import Language


class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "tag",
        "language",
        "published_at",
        "active",
        "created_at",
    )

    list_display_links = (
        "id",
        "title",
        "category",
        "tag",
        "language",
        "published_at",
        "active",
        "created_at",
    )

    list_filter = [
        filters.TitleFilter,
    ]

    list_per_page = 10

    ordering = ("-id",)

    search_fields = ["title"]

    autocomplete_fields = ["language", "category"]

    readonly_fields = ("created_at", "updated_at")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if "autocomplete" in request.path:
            language_queryset = Language.objects.filter(
                name__icontains=search_term
            ).order_by("name")

            return language_queryset, use_distinct

        return queryset, use_distinct


class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "tag",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
        "tag",
        "created_at",
        "updated_at",
    )

    list_filter = [
        filters.NameFilter,
    ]

    search_fields = ["name"]

    ordering = ("-id",)

    readonly_fields = ("created_at", "updated_at")


admin.site.register(models.Content, ContentAdmin)
admin.site.register(models.ContentCategory, ContentCategoryAdmin)
