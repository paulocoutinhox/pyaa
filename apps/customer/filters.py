from django.contrib.admin import SimpleListFilter
from django.contrib.sites.models import Site
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_admin_extras import InputFilter
from rangefilter.filters import DateRangeFilter

from pyaa.filters import DigitsOnlyFilter


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


class CpfFilter(DigitsOnlyFilter):
    parameter_name = "cpf"
    title = _("filter.cpf")
    input_mask = "000.000.000-00"

    def field_query(self, value):
        return Q(user__cpf=value)


class MobilePhoneFilter(DigitsOnlyFilter):
    parameter_name = "mobile_phone"
    title = _("filter.mobile-phone")
    input_mask = "(00)0000-00009"

    def field_query(self, value):
        return Q(user__mobile_phone=value)


class SiteFilter(SimpleListFilter):
    title = _("filter.site")
    parameter_name = "site"

    def lookups(self, request, model_admin):
        sites = Site.objects.all().order_by("name")
        return [(str(site.id), site.name) for site in sites]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(site_id=self.value())

        return queryset


class CreatedAtFilter(DateRangeFilter):
    title = _("filter.created-at")
