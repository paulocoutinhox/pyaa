from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.subscriptions"
    verbose_name = _("apps.subscriptions.description")
