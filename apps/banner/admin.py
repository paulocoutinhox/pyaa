from django.contrib import admin
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _

from apps.banner import models
from apps.banner.enums import BannerAccessType


class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "zone",
        "site",
        "language",
        "sort_order",
        "active",
        "total_views",
        "total_clicks",
        "created_at",
    )

    list_display_links = (
        "id",
        "title",
        "zone",
        "site",
        "language",
        "sort_order",
        "active",
        "total_views",
        "total_clicks",
        "created_at",
    )

    list_filter = ["zone", "active"]
    list_per_page = 20
    ordering = ["-id"]
    search_fields = ["title"]
    autocomplete_fields = ["language", "site"]
    readonly_fields = (
        "token",
        "created_at",
        "updated_at",
        "total_views",
        "total_clicks",
    )

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "title",
                    "image",
                    "link",
                    "target_blank",
                    "zone",
                    "sort_order",
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
            _("admin.fieldsets.additional-info"),
            {
                "fields": (
                    "token",
                    "total_views",
                    "total_clicks",
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_views=Count(
                "accesses",
                filter=Q(accesses__access_type=BannerAccessType.VIEW),
            ),
            total_clicks=Count(
                "accesses",
                filter=Q(accesses__access_type=BannerAccessType.CLICK),
            ),
        )
        return qs

    def total_views(self, obj):
        return obj.total_views if hasattr(obj, "total_views") else 0

    def total_clicks(self, obj):
        return obj.total_clicks if hasattr(obj, "total_clicks") else 0

    total_views.short_description = _("model.field.total-views")
    total_clicks.short_description = _("model.field.total-clicks")


class BannerAccessAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "banner",
        "access_type",
        "customer",
        "ip_address",
        "country_code",
        "created_at",
    )

    list_display_links = (
        "id",
        "banner",
        "access_type",
        "customer",
        "ip_address",
        "country_code",
        "created_at",
    )

    list_filter = ["access_type", "country_code", "created_at"]
    list_per_page = 20
    ordering = ["-id"]
    search_fields = ["banner__title", "customer__user__email"]
    autocomplete_fields = ["banner", "customer"]
    readonly_fields = ("created_at", "ip_address", "country_code")

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "banner",
                    "access_type",
                    "customer",
                    "ip_address",
                    "country_code",
                ),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at",),
            },
        ),
    )

    def ip_address(self, obj):
        return obj.get_ip_address()

    ip_address.short_description = _("model.field.ip")
    ip_address.admin_order_field = "ip_number"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(models.Banner, BannerAdmin)
admin.site.register(models.BannerAccess, BannerAccessAdmin)
