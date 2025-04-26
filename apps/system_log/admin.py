from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.system_log import models
from pyaa.helpers.status import StatusHelper


class SystemLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "level_badge",
        "category",
        "customer",
        "created_at",
    )

    list_display_links = (
        "id",
        "level_badge",
        "category",
        "customer",
        "created_at",
    )

    list_filter = (
        "level",
        "category",
        "created_at",
    )

    search_fields = (
        "category",
        "description",
        "customer__user__email",
    )

    readonly_fields = (
        "site",
        "level",
        "category",
        "description",
        "customer",
        "created_at",
    )

    ordering = ("-id",)

    autocomplete_fields = ["customer"]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "level",
                    "category",
                    "description",
                )
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

    def has_delete_permission(self, request, obj=None):
        return False

    def level_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.level, "hex")
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.get_level_display().lower(),
        )

    level_badge.short_description = _("model.field.level")


admin.site.register(models.SystemLog, SystemLogAdmin)
