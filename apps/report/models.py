from django.utils.translation import gettext_lazy as _

from apps.customer.models import Customer


class CustomerGenderSummary(Customer):
    class Meta:
        proxy = True
        verbose_name = _("model.customer-gender-summary.name")
