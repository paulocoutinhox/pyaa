from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.gallery import fields
from apps.language import models as language_models


class Gallery(models.Model):
    class Meta:
        db_table = "gallery"
        verbose_name = _("model.gallery.name")
        verbose_name_plural = _("model.gallery.name.plural")

        indexes = [
            models.Index(
                fields=["title"],
                name="{0}_title".format(db_table),
            ),
            models.Index(
                fields=["language"],
                name="{0}_language".format(db_table),
            ),
        ]

    id = models.BigAutoField(
        _("model.field.id"),
        unique=True,
        primary_key=True,
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="galleries",
        verbose_name=_("model.field.site"),
        blank=True,
        null=True,
    )

    title = models.CharField(
        _("model.field.title"),
        max_length=255,
        blank=False,
        null=False,
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

    def get_main_photo_url(self, request=None):
        main_photo = self.gallery_photos.filter(main=True).first()

        if main_photo and main_photo.image:
            photo_url = main_photo.image.url
        else:
            photo_url = settings.STATIC_URL + "images/no-image.png"

        if request:
            return urljoin(request.build_absolute_uri("/"), photo_url)

        return photo_url

    def photos_count(self):
        return self.gallery_photos.count()

    photos_count.short_description = _("model.field.photos-count")

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = slugify(self.title)
        super(Gallery, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    class Meta:
        db_table = "gallery_photo"
        verbose_name = _("model.gallery-photo.name")
        verbose_name_plural = _("model.gallery-photo.name.plural")

    gallery = models.ForeignKey(
        Gallery, on_delete=models.CASCADE, related_name="gallery_photos"
    )

    image = fields.GalleryPhotoImageField(
        _("model.field.image"),
        size=[1024, 1024],
        quality=100,
        upload_to="images/gallery/%Y/%m/%d",
        blank=False,
        null=False,
    )

    caption = models.CharField(
        _("model.field.caption"),
        max_length=255,
        blank=True,
        null=True,
    )

    main = models.BooleanField(
        _("model.field.main"),
        default=False,
    )

    def preview(self):
        if self.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width: 45px;" /></a>'.format(
                    self.image.url,
                    self.image.url,
                )
            )
        return ""

    preview.short_description = _("model.field.preview")
    preview.allow_tags = True
