from django.contrib import admin
from django.db import models, transaction
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from nonrelated_inlines.admin import NonrelatedStackedInline

from apps.customer.helpers import CustomerHelper
from apps.shop import filters, models
from apps.shop.enums import ObjectType


class ShopEventLogInlineAdmin(NonrelatedStackedInline):
    model = models.EventLog
    extra = 0
    can_delete = False
    ordering = ["-id"]
    exclude = ["id", "object_type", "object_id", "customer", "description"]

    def get_nonrelated_queryset(self, obj):
        return models.EventLog.objects.filter(
            object_type=ObjectType.SUBSCRIPTION, object_id=obj.id
        ).order_by("-id")

    def get_form_queryset(self, obj):
        return self.get_nonrelated_queryset(obj)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def description_modal(self, obj):
        copy_button_text = _("button.copy")
        close_button_text = _("button.close")
        open_button_text = _("button.open")
        modal_title = _("modal.title.message")

        return format_html(
            """
            <a href="#" class="button" onclick="openAdminModal_{0}(); return false;">{4}</a>
            <div id="admin-modal-{0}" class="admin-modal" title="{5}" style="display:none;">
                <div class="admin-modal-body">
                    <p id="description-content-{0}">{1}</p>
                </div>
            </div>
            <script>
                function openAdminModal_{0}() {{
                    $("#admin-modal-{0}").dialog({{
                        modal: true,
                        width: "90%",
                        height: "auto",
                        maxHeight: $(window).height() - 60,
                        buttons: {{
                            "{2}": function() {{
                                var content = document.getElementById("description-content-{0}").innerText;
                                navigator.clipboard.writeText(content);
                            }},
                            "{3}": function() {{
                                $(this).dialog("close");
                            }}
                        }}
                    }});
                }}
            </script>
            """,
            obj.id,
            obj.description,
            copy_button_text,
            close_button_text,
            open_button_text,
            modal_title,
        )

    description_modal.short_description = _("model.field.description")

    readonly_fields = ["description_modal"] + [
        field.name
        for field in models.EventLog._meta.fields
        if field.name != "description"
    ]

    readonly_fields = (
        "status",
        "currency",
        "amount",
        "description_modal",
        "created_at",
    )


class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "gateway",
        "currency",
        "price",
        "credits",
        "sort_order",
        "featured",
        "active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
        "gateway",
        "currency",
        "price",
        "credits",
        "sort_order",
        "featured",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
        "gateway",
    )

    search_fields = ("name", "tag", "gateway")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-id",)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token",
        "customer",
        "plan",
        "status",
        "created_at",
    )

    list_display_links = (
        "id",
        "token",
        "customer",
        "plan",
        "status",
        "created_at",
    )

    list_filter = (
        filters.TokenFilter,
        "status",
        "created_at",
    )

    readonly_fields = [
        field.name
        for field in models.Subscription._meta.fields
        if field.name not in ["status"]
    ]

    search_fields = ("token",)
    ordering = ("-id",)

    inlines = [ShopEventLogInlineAdmin]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EventLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "status",
        "created_at",
    )

    list_display_links = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "status",
        "created_at",
    )

    list_filter = (
        "object_type",
        "status",
        "created_at",
    )

    search_fields = ("object_id", "object_type", "customer__user__email")
    readonly_fields = [field.name for field in models.EventLog._meta.fields]
    ordering = ("-id",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CreditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "amount",
        "created_at",
    )

    list_display_links = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "amount",
        "created_at",
    )

    list_filter = (
        "object_type",
        "created_at",
    )

    search_fields = ("object_id", "object_type", "customer__user__email")
    ordering = ("-id",)
    autocomplete_fields = ["customer"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            CustomerHelper.add_credits(obj.customer, obj.amount)


admin.site.register(models.Plan, PlanAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.EventLog, EventLogAdmin)
admin.site.register(models.CreditLog, CreditLogAdmin)
