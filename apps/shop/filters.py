from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_admin_extras import InputFilter


class TokenFilter(InputFilter):
    parameter_name = "token"
    title = _("filter.token")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            value = value.strip()

            return queryset.filter(Q(token=value))
        return queryset
