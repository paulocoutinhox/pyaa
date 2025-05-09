from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.customer import filters, forms, models
from apps.customer.helpers import CustomerHelper
from pyaa.mixins import ReadonlyLinksMixin


class CustomerAddressInline(admin.StackedInline):
    model = models.CustomerAddress
    form = forms.CustomerAddressAdminForm
    extra = 0
    classes = ["collapse"]

    fieldsets = (
        (
            None,
            {
                "fields": ("address_type",),
            },
        ),
        (
            _("admin.fieldsets.address"),
            {
                "fields": (
                    ("address_line1", "street_number"),
                    "address_line2",
                    "complement",
                ),
            },
        ),
        (
            _("admin.fieldsets.location"),
            {
                "fields": (
                    ("city", "state"),
                    ("postal_code", "country_code"),
                ),
            },
        ),
    )


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
        filters.CpfFilter,
        filters.MobilePhoneFilter,
        filters.SiteFilter,
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

    readonly_fields_links = ["site", "user", "credits"]

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__cpf",
        "user__mobile_phone",
        "nickname",
    ]

    form = forms.CustomerAdminForm

    inlines = [CustomerAddressInline]

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
                "fields": ("nickname", "gender", "avatar"),
            },
        ),
        (
            _("admin.fieldsets.additional-info"),
            {
                "fields": ("credits", "activate_token", "recovery_token", "obs"),
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
        if not obj.user:
            return "-"
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(
        ordering="user__email",
        description=_("model.field.email"),
    )
    def user_email(self, obj):
        if not obj.user:
            return "-"
        return obj.user.email

    @admin.display(
        ordering="user__cpf",
        description=_("model.field.cpf"),
    )
    def user_cpf(self, obj):
        if not obj.user:
            return "-"
        return obj.user.cpf

    @admin.display(
        ordering="user__mobile_phone",
        description=_("model.field.mobile-phone"),
    )
    def user_mobile_phone(self, obj):
        if not obj.user:
            return "-"
        return obj.user.mobile_phone

    @admin.display(
        boolean=True,
        ordering="user__is_active",
        description=_("model.field.is_active"),
    )
    def user_is_active(self, obj):
        if not obj.user:
            return False
        return obj.user.is_active

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            CustomerHelper.post_save(obj)


admin.site.register(models.Customer, CustomerAdmin)
