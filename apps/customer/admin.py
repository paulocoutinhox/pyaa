from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.customer import filters, forms, models
from apps.customer.helpers import CustomerHelper


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_name",
        "user_email",
        "credits",
        "user_is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "user_name",
        "user_email",
        "credits",
        "created_at",
    )

    list_filter = [
        filters.NameFilter,
        filters.EmailFilter,
    ]

    list_per_page = 10

    ordering = ("-id",)

    autocomplete_fields = ["user", "language"]

    readonly_fields = ("created_at", "updated_at")

    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    form = forms.CustomerAdminForm

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        return qs.select_related("user")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        # search by first_name, or last_name, or email
        if search_term:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_term)
                | Q(user__last_name__icontains=search_term)
                | Q(user__email__icontains=search_term)
            )

        return queryset, use_distinct

    @admin.display(
        ordering="user__first_name",
        description=_("model.field.name"),
    )
    def user_name(self, obj):
        return str(obj)

    @admin.display(
        ordering="user__email",
        description=_("model.field.email"),
    )
    def user_email(self, obj):
        return obj.user.email

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


admin.site.register(models.Customer, CustomerAdmin)
