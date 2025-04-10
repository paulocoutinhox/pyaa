from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from apps.language import models as language_models


class ContentCategory(models.Model):
    class Meta:
        db_table = "content_category"
        verbose_name = _("model.content-category.name")
        verbose_name_plural = _("model.content-category.name.plural")

        indexes = [
            models.Index(
                fields=["name"],
                name="{0}_name".format(db_table),
            ),
            models.Index(
                fields=["tag"],
                name="{0}_tag".format(db_table),
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
        blank=False,
        null=False,
    )

    tag = models.SlugField(
        _("model.field.tag"),
        max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text=_("model.field.tag.help"),
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("model.field.updated-at"),
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = slugify(self.name)

        super(ContentCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Content(models.Model):
    class Meta:
        db_table = "content"
        verbose_name = _("model.content.name")
        verbose_name_plural = _("model.content.name.plural")

        indexes = [
            models.Index(
                fields=["language"],
                name="{0}_language".format(db_table),
            ),
            models.Index(
                fields=["tag"],
                name="{0}_tag".format(db_table),
            ),
            models.Index(
                fields=["title"],
                name="{0}_title".format(db_table),
            ),
            models.Index(
                fields=["published_at"],
                name="{0}_published_at".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    title = models.CharField(
        _("model.field.title"),
        max_length=255,
        blank=False,
        null=False,
    )

    category = models.ForeignKey(
        ContentCategory,
        on_delete=models.RESTRICT,
        related_name="contents",
        blank=True,
        null=True,
        verbose_name=_("model.field.category"),
    )

    language = models.ForeignKey(
        language_models.Language,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("model.field.language"),
    )

    tag = models.SlugField(
        _("model.field.tag"),
        max_length=255,
        blank=True,
        null=True,
        default=None,
        help_text=_("model.field.tag.help"),
    )

    content = HTMLField(
        _("model.field.content"),
        blank=True,
        null=True,
    )

    published_at = models.DateField(
        _("model.field.published-at"),
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        _("model.field.active"),
        default=True,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(
        _("model.field.created-at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("model.field.updated-at"),
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = slugify(self.title)

        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
