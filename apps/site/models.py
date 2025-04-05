from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteProfile(models.Model):
    class Meta:
        db_table = "site_profile"
        verbose_name = _("model.site-profile.name")
        verbose_name_plural = _("model.site-profile.name.plural")
        indexes = [
            models.Index(fields=["site"], name="site_profile_title"),
        ]

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("model.field.site"),
    )

    title = models.CharField(
        _("model.field.title"),
        max_length=255,
        blank=True,
        null=True,
    )

    template_folder = models.CharField(
        _("model.field.template-folder"),
        max_length=255,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("model.field.updated-at"),
        auto_now=True,
    )

    def __str__(self):
        return self.title
