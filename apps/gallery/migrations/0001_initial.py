# Generated by Django 5.1.7 on 2025-03-29 01:40

import apps.gallery.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("language", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Gallery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="model.field.id",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="model.field.title"),
                ),
                (
                    "tag",
                    models.SlugField(
                        blank=True,
                        default=None,
                        help_text="model.field.tag.help",
                        max_length=255,
                        null=True,
                        verbose_name="model.field.tag",
                    ),
                ),
                (
                    "published_at",
                    models.DateField(
                        blank=True, null=True, verbose_name="model.field.published-at"
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, verbose_name="model.field.active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="model.field.created-at"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="model.field.updated-at"
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="language.language",
                        verbose_name="model.field.language",
                    ),
                ),
            ],
            options={
                "verbose_name": "model.gallery.name",
                "verbose_name_plural": "model.gallery.name.plural",
                "db_table": "gallery",
            },
        ),
        migrations.CreateModel(
            name="GalleryPhoto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    apps.gallery.fields.GalleryPhotoImageField(
                        crop=None,
                        force_format=None,
                        keep_meta=True,
                        quality=100,
                        scale=None,
                        size=[1024, 1024],
                        upload_to="images/gallery/%Y/%m/%d",
                        verbose_name="model.field.image",
                    ),
                ),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="model.field.caption",
                    ),
                ),
                (
                    "main",
                    models.BooleanField(default=False, verbose_name="model.field.main"),
                ),
                (
                    "gallery",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery_photos",
                        to="gallery.gallery",
                    ),
                ),
            ],
            options={
                "verbose_name": "model.gallery-photo.name",
                "verbose_name_plural": "model.gallery-photo.name.plural",
                "db_table": "gallery_photo",
            },
        ),
        migrations.AddIndex(
            model_name="gallery",
            index=models.Index(fields=["title"], name="gallery_title"),
        ),
        migrations.AddIndex(
            model_name="gallery",
            index=models.Index(fields=["language"], name="gallery_language"),
        ),
    ]
