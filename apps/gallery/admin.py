from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.gallery import filters, models
from apps.language.models import Language


class GalleryPhotoInlineAdmin(admin.TabularInline):
    model = models.GalleryPhoto
    extra = 1
    fields = ("image", "preview", "caption", "main")
    readonly_fields = ("preview",)


class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryPhotoInlineAdmin]

    list_display = (
        "id",
        "title",
        "tag",
        "site_name",
        "language",
        "published_at",
        "photos_count",
        "active",
        "created_at",
    )

    list_display_links = (
        "id",
        "title",
        "tag",
        "site_name",
        "language",
        "published_at",
        "photos_count",
        "active",
        "created_at",
    )

    list_filter = [
        filters.TitleFilter,
    ]

    list_per_page = 10

    ordering = ("-id",)

    search_fields = ["title"]

    autocomplete_fields = ["language", "site"]

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "title",
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

    def get_queryset(self, request):
        qs = super(GalleryAdmin, self).get_queryset(request)
        return qs

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

    @admin.display(
        ordering="site__name",
        description=_("model.field.site"),
    )
    def site_name(self, obj):
        if obj.site:
            return obj.site.name

        return None


admin.site.register(models.Gallery, GalleryAdmin)
