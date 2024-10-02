# Generated by Django 5.1.1 on 2024-09-29 05:45

import django.db.models.deletion
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("language", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Content",
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
                    "content",
                    tinymce.models.HTMLField(
                        blank=True, null=True, verbose_name="model.field.content"
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
                "verbose_name": "model.content.name",
                "verbose_name_plural": "model.content.name.plural",
                "db_table": "content",
                "indexes": [
                    models.Index(fields=["language"], name="content_language"),
                    models.Index(fields=["tag"], name="content_tag"),
                    models.Index(fields=["title"], name="content_title"),
                ],
            },
        ),
    ]
