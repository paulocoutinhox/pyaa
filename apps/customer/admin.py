from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.customer import filters, forms, models
from apps.customer.helpers import CustomerHelper
from pyaa.helpers.status import StatusHelper
from pyaa.mixins import ReadonlyLinksMixin


class CustomerAdmin(ReadonlyLinksMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user_name",
        "user_email",
        "user_cpf",
        "nickname",
        "gender",
        "user_is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "user_name",
        "user_email",
        "user_cpf",
        "nickname",
        "gender",
        "user_is_active",
        "created_at",
    )

    list_filter = [
        filters.NameFilter,
        filters.EmailFilter,
        "gender",
    ]

    list_per_page = 20

    ordering = ("-id",)

    autocomplete_fields = ["language", "site"]

    readonly_fields = (
        "created_at",
        "updated_at",
        "user_email",
        "user_cpf",
        "user_mobile_phone",
        "activate_token",
        "recovery_token",
    )

    readonly_fields_links = ["site", "user"]

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__cpf",
        "user__mobile_phone",
        "nickname",
    ]

    form = forms.CustomerAdminForm

    fieldsets = (
        (
            _("admin.fieldsets.user"),
            {
                "fields": (
                    "user",
                    "site",
                    "user_email",
                    "user_cpf",
                    "user_mobile_phone",
                ),
            },
        ),
        (
            _("admin.fieldsets.profile"),
            {
                "fields": ("nickname", "gender", "avatar", "is_new_winner"),
            },
        ),
        (
            _("admin.fieldsets.additional-info"),
            {
                "fields": ("activate_token", "recovery_token", "obs"),
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "site", "language")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if search_term:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_term)
                | Q(user__last_name__icontains=search_term)
                | Q(user__email__icontains=search_term)
                | Q(user__cpf__icontains=search_term)
                | Q(user__mobile_phone__icontains=search_term)
                | Q(nickname__icontains=search_term)
            )

        return queryset, use_distinct

    @admin.display(
        ordering="user__first_name",
        description=_("model.field.name"),
    )
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(
        ordering="user__email",
        description=_("model.field.email"),
    )
    def user_email(self, obj):
        return obj.user.email

    @admin.display(
        ordering="user__cpf",
        description=_("model.field.cpf"),
    )
    def user_cpf(self, obj):
        return obj.user.cpf

    @admin.display(
        ordering="user__mobile_phone",
        description=_("model.field.mobile-phone"),
    )
    def user_mobile_phone(self, obj):
        return obj.user.mobile_phone

    @admin.display(
        boolean=True,
        ordering="user__is_active",
        description=_("model.field.is_active"),
    )
    def user_is_active(self, obj):
        return obj.user.is_active

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            CustomerHelper.post_save(obj)


class CustomerCreditAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "credit_type_badge",
        "credit_amount",
        "price",
        "expire_at",
        "created_at",
    )

    list_display_links = (
        "id",
        "customer",
        "credit_type_badge",
        "credit_amount",
        "price",
        "expire_at",
        "created_at",
    )

    list_filter = [
        "credit_type",
        "object_type",
        ("customer", admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        "customer__user__first_name",
        "customer__user__last_name",
        "customer__user__email",
        "object_type",
        "credit_type",
    ]

    ordering = ("-id",)

    readonly_fields = (
        "id",
        "site",
        "customer",
        "plan_id",
        "object_type",
        "object_id",
        "credit_type",
        "current_amount",
        "initial_amount",
        "price",
        "expire_at",
        "created_at",
        "updated_at",
    )

    list_per_page = 20

    fieldsets = (
        (
            _("admin.fieldsets.general"),
            {
                "fields": (
                    "id",
                    "site",
                    "customer",
                )
            },
        ),
        (
            _("admin.fieldsets.details"),
            {
                "fields": (
                    "plan_id",
                    "object_type",
                    "object_id",
                    "credit_type",
                    "current_amount",
                    "initial_amount",
                    "price",
                )
            },
        ),
        (
            _("admin.fieldsets.important-dates"),
            {
                "fields": (
                    "expire_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def credit_type_badge(self, obj):
        colors = StatusHelper.get_credit_type_color(obj.credit_type)
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 2px 8px; border-radius: 10px;">{}</span>',
            colors["bg"],
            colors["text"],
            obj.get_credit_type_display().lower(),
        )

    credit_type_badge.short_description = _("model.field.credit-type")

    def credit_amount(self, obj):
        return format_html(
            "{}/{}",
            obj.current_amount,
            obj.initial_amount,
        )

    credit_amount.short_description = _("model.field.credit-amount")


admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.CustomerCredit, CustomerCreditAdmin)
