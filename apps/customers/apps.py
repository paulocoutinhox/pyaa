from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomersAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
    verbose_name = _("apps.customers.description")
