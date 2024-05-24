from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_admin_extras import InputFilter


class TitleFilter(InputFilter):
    parameter_name = "title"
    title = _("filter.title")

    def queryset(self, request, queryset):
        if self.value() is not None:
            value = self.value()

            return queryset.filter(Q(title__contains=value))
