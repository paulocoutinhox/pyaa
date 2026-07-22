from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from apps.content import filters, models


class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "tag",
        "site_name",
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
        "site_name",
        "language",
        "published_at",
        "active",
        "created_at",
    )

    list_filter = [
        filters.TitleFilter,
        ("category", RelatedDropdownFilter),
    ]

    list_per_page = 10

    ordering = ("-id",)

    search_fields = ["title"]

    autocomplete_fields = ["language", "category", "site"]

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "title",
                    "content",
                    "category",
                    "tag",
                    "published_at",
                    "active",
                ),
            },
        ),
        (
            _("admin.fieldsets.site-language"),
            {
                "fields": ("site", "language"),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(
        ordering="site__name",
        description=_("model.field.site"),
    )
    def site_name(self, obj):
        if obj.site:
            return obj.site.name

        return None


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

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "name",
                    "tag",
                ),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


admin.site.register(models.Content, ContentAdmin)
admin.site.register(models.ContentCategory, ContentCategoryAdmin)
