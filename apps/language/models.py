from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    class Meta:
        db_table = "language"
        verbose_name = _("model.language.name")
        verbose_name_plural = _("model.language.name.plural")

        indexes = [
            models.Index(
                fields=["name"],
                name="{0}_name".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    name = models.CharField(
        _("model.field.name"),
        max_length=255,
    )

    native_name = models.CharField(
        _("model.field.native_name"),
        max_length=255,
        help_text=_("model.hint.native_name"),
    )

    code_iso_639_1 = models.CharField(
        _("model.field.code_iso_639_1"),
        max_length=255,
        help_text=_("model.hint.code_iso_639_1"),
    )

    code_iso_language = models.CharField(
        _("model.field.code_iso_language"),
        help_text=_("model.hint.code_iso_language"),
        max_length=255,
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
        return self.name
