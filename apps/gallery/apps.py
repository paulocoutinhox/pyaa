from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GalleryAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gallery"
    verbose_name = _("apps.gallery.description")
