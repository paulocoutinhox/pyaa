from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_admin_extras import InputFilter


class NameFilter(InputFilter):
    parameter_name = "name"
    title = _("filter.name")

    def queryset(self, request, queryset):
        if self.value() is not None:
            value = self.value()

            return queryset.filter(Q(name__contains=value))
