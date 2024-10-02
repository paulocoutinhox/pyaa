from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_admin_extras import InputFilter


class NameFilter(InputFilter):
    parameter_name = "name"
    title = _("filter.name")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            value = value.strip()

            return queryset.filter(
                Q(user__first_name__icontains=value)
                | Q(user__last_name__icontains=value)
            )
        return queryset


class EmailFilter(InputFilter):
    parameter_name = "email"
    title = _("filter.email")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            value = value.strip()

            return queryset.filter(Q(user__email=value))
        return queryset
