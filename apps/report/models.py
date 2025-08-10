from django.utils.translation import gettext_lazy as _

from apps.banner.models import Banner
from apps.customer.models import Customer


class CustomerGenderSummary(Customer):
    class Meta:
        proxy = True
        verbose_name = _("model.customer-gender-summary.name")
        verbose_name_plural = _("model.customer-gender-summary.name")


class BannerAccessSummary(Banner):
    class Meta:
        proxy = True
        verbose_name = _("model.banner-access-summary.name")
        verbose_name_plural = _("model.banner-access-summary.name")
