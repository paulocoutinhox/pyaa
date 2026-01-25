from django.contrib import admin
from django.db import models, transaction
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from nonrelated_inlines.admin import NonrelatedTabularInline

from apps.customer.helpers import CustomerHelper
from apps.shop import filters, models
from apps.shop.enums import ObjectType
from pyaa.helpers.status import StatusHelper


class BaseEventLogInlineAdmin(NonrelatedTabularInline):
    model = models.EventLog
    extra = 0
    can_delete = False
    ordering = ["-id"]
    exclude = ["id", "object_type", "object_id", "customer", "description"]

    readonly_fields = ["description_modal"] + [
        field.name
        for field in models.EventLog._meta.fields
        if field.name != "description"
    ]

    readonly_fields = (
        "site",
        "status_badge",
        "currency",
        "amount",
        "description_modal",
        "created_at",
    )

    fields = (
        "site",
        "status_badge",
        "currency",
        "amount",
        "description_modal",
        "created_at",
    )

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

    def status_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.status, "hex")
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.status,
        )

    status_badge.short_description = _("model.field.status")


class ShopSubscriptionEventLogInlineAdmin(BaseEventLogInlineAdmin):
    def get_nonrelated_queryset(self, obj):
        return models.EventLog.objects.filter(
            object_type=ObjectType.SUBSCRIPTION, object_id=obj.id
        ).order_by("-id")

    def get_form_queryset(self, obj):
        return self.get_nonrelated_queryset(obj)


class ShopCreditPurchaseEventLogInlineAdmin(BaseEventLogInlineAdmin):
    def get_nonrelated_queryset(self, obj):
        return models.EventLog.objects.filter(
            object_type=ObjectType.CREDIT_PURCHASE, object_id=obj.id
        ).order_by("-id")

    def get_form_queryset(self, obj):
        return self.get_nonrelated_queryset(obj)


class ShopProductPurchaseEventLogInlineAdmin(BaseEventLogInlineAdmin):
    def get_nonrelated_queryset(self, obj):
        return models.EventLog.objects.filter(
            object_type=ObjectType.PRODUCT_PURCHASE, object_id=obj.id
        ).order_by("-id")

    def get_form_queryset(self, obj):
        return self.get_nonrelated_queryset(obj)


class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "gateway",
        "plan_type",
        "language",
        "credits",
        "active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
        "gateway",
        "plan_type",
        "language",
        "credits",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
        "gateway",
        "language",
    )

    search_fields = ("name", "token")
    readonly_fields = ("token", "created_at", "updated_at")
    ordering = ("-id",)

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "token",
                    "language",
                    "name",
                    "tag",
                    "gateway",
                    "external_id",
                    "plan_type",
                )
            },
        ),
        (
            _("admin.fieldsets.pricing"),
            {
                "fields": (
                    "currency",
                    "price",
                    "credits",
                    "bonus",
                )
            },
        ),
        (
            _("admin.fieldsets.frequency"),
            {
                "fields": (
                    "frequency_type",
                    "frequency_amount",
                )
            },
        ),
        (
            _("admin.fieldsets.features"),
            {
                "fields": (
                    "sort_order",
                    "featured",
                )
            },
        ),
        (
            _("admin.fieldsets.description"),
            {
                "fields": (
                    "description",
                    "image",
                )
            },
        ),
        (
            _("admin.fieldsets.status"),
            {
                "fields": ("active",),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token",
        "customer",
        "plan",
        "status_badge",
        "created_at",
    )

    list_display_links = (
        "id",
        "token",
        "customer",
        "plan",
        "status_badge",
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
        if field.name not in ["expire_at", "status"]
    ]

    search_fields = ("token",)
    ordering = ("-id",)

    inlines = [ShopSubscriptionEventLogInlineAdmin]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "plan",
                    "token",
                    "external_id",
                )
            },
        ),
        (
            _("admin.fieldsets.subscription"),
            {
                "fields": (
                    "status",
                    "expire_at",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.status, "hex")
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.get_status_display().lower(),
        )

    status_badge.short_description = _("model.field.status")


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
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "object_type",
                    "object_id",
                )
            },
        ),
        (
            _("admin.fieldsets.details"),
            {
                "fields": (
                    "amount",
                    "description",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {"fields": ("created_at",)},
        ),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)

            if not change:
                CustomerHelper.update_customer_credits(
                    obj.customer.id,
                    obj.amount,
                )


class EventLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "status_badge",
        "created_at",
    )

    list_display_links = (
        "id",
        "object_id",
        "object_type",
        "customer",
        "status_badge",
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

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "object_type",
                    "object_id",
                )
            },
        ),
        (
            _("admin.fieldsets.details"),
            {
                "fields": (
                    "currency",
                    "amount",
                    "status",
                    "description",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {"fields": ("created_at",)},
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.status)
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.status,
        )

    status_badge.short_description = _("model.field.status")


class CreditPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token",
        "customer",
        "plan",
        "price",
        "status_badge",
        "created_at",
    )

    list_display_links = (
        "id",
        "token",
        "customer",
        "plan",
        "price",
        "status_badge",
        "created_at",
    )

    list_filter = (
        "status",
        "invoice_generated",
        "created_at",
    )

    search_fields = (
        "token",
        "customer__user__email",
        "plan__name",
    )

    readonly_fields = (
        "site",
        "customer",
        "plan",
        "token",
        "price",
        "currency",
        "status",
        "invoice_generated",
        "created_at",
        "updated_at",
    )

    ordering = ("-id",)

    autocomplete_fields = ["customer", "plan"]

    inlines = [ShopCreditPurchaseEventLogInlineAdmin]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "plan",
                    "token",
                    "status",
                )
            },
        ),
        (
            _("admin.fieldsets.pricing"),
            {
                "fields": (
                    "price",
                    "currency",
                    "invoice_generated",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.status)
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.get_status_display().lower(),
        )

    status_badge.short_description = _("model.field.status")


class ProductFileInline(admin.TabularInline):
    model = models.ProductFile
    extra = 1
    fields = (
        "name",
        "file",
        "file_type",
        "file_size",
        "active",
        "sort_order",
    )
    readonly_fields = ("file_type", "file_size")

    def get_formset(self, request, obj=None, **kwargs):
        from django import forms

        class ProductFileForm(forms.ModelForm):
            class Meta:
                model = models.ProductFile
                fields = "__all__"

            def clean_file(self):
                file = self.cleaned_data.get("file", None)

                if file and hasattr(file, "content_type") and hasattr(file, "size"):
                    # only update if the file has changed
                    if self.instance.pk is None or "file" in self.changed_data:
                        self.instance.file_type = file.content_type
                        self.instance.file_size = file.size

                return file

        kwargs["form"] = ProductFileForm
        return super().get_formset(request, obj, **kwargs)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "currency",
        "active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
        "price",
        "currency",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
        "currency",
        "created_at",
    )

    search_fields = ("name", "token")
    readonly_fields = ("token", "created_at", "updated_at")
    ordering = ("-id",)
    inlines = [ProductFileInline]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "token",
                    "name",
                )
            },
        ),
        (
            _("admin.fieldsets.pricing"),
            {
                "fields": (
                    "currency",
                    "price",
                )
            },
        ),
        (
            _("admin.fieldsets.description"),
            {
                "fields": (
                    "description",
                    "image",
                )
            },
        ),
        (
            _("admin.fieldsets.status"),
            {
                "fields": ("active",),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "token",
        "customer",
        "product",
        "price",
        "status_badge",
        "created_at",
    )

    list_display_links = (
        "id",
        "token",
        "customer",
        "product",
        "price",
        "status_badge",
        "created_at",
    )

    list_filter = (
        "status",
        "invoice_generated",
        "created_at",
    )

    search_fields = (
        "token",
        "customer__user__email",
        "product__name",
    )

    readonly_fields = (
        "site",
        "customer",
        "product",
        "token",
        "price",
        "currency",
        "status",
        "invoice_generated",
        "created_at",
        "updated_at",
    )

    ordering = ("-id",)

    autocomplete_fields = ["customer", "product"]

    inlines = [ShopProductPurchaseEventLogInlineAdmin]

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "site",
                    "customer",
                    "product",
                    "token",
                    "status",
                )
            },
        ),
        (
            _("admin.fieldsets.pricing"),
            {
                "fields": (
                    "price",
                    "currency",
                    "invoice_generated",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status_badge(self, obj):
        colors = StatusHelper.get_status_color(obj.status)
        bg_color = colors["bg"]
        text_color = colors["text"]

        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            text_color,
            bg_color,
            obj.get_status_display().lower(),
        )

    status_badge.short_description = _("model.field.status")


admin.site.register(models.Plan, PlanAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.CreditLog, CreditLogAdmin)
admin.site.register(models.EventLog, EventLogAdmin)
admin.site.register(models.CreditPurchase, CreditPurchaseAdmin)
admin.site.register(models.ProductPurchase, ProductPurchaseAdmin)
admin.site.register(models.Product, ProductAdmin)
