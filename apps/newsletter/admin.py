from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.newsletter.models import NewsletterEntry


class NewsletterEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "created_at",
    )

    list_display_links = (
        "id",
        "email",
        "created_at",
    )

    list_filter = [
        "created_at",
    ]

    list_per_page = 20

    ordering = ("-id",)

    readonly_fields = ("created_at",)

    search_fields = [
        "email",
    ]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": ("email",),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at",),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(NewsletterEntry, NewsletterEntryAdmin)
