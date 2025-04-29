import csv

from django.contrib import admin
from django.http import HttpResponse
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

    actions = ["export_as_csv"]

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

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ["id", "email", "created_at"]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment; filename={meta.verbose_name_plural}.csv"
        )

        # bom for excel
        response.write("\ufeff".encode("utf-8"))

        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = _("admin.action.export-as-csv")


admin.site.register(NewsletterEntry, NewsletterEntryAdmin)
