# Generated by Django 5.2 on 2025-04-10 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Language",
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
                    "name",
                    models.CharField(max_length=255, verbose_name="model.field.name"),
                ),
                (
                    "native_name",
                    models.CharField(
                        help_text="model.hint.native_name",
                        max_length=255,
                        verbose_name="model.field.native_name",
                    ),
                ),
                (
                    "code_iso_639_1",
                    models.CharField(
                        help_text="model.hint.code_iso_639_1",
                        max_length=255,
                        verbose_name="model.field.code_iso_639_1",
                    ),
                ),
                (
                    "code_iso_language",
                    models.CharField(
                        help_text="model.hint.code_iso_language",
                        max_length=255,
                        verbose_name="model.field.code_iso_language",
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
            ],
            options={
                "verbose_name": "model.language.name",
                "verbose_name_plural": "model.language.name.plural",
                "db_table": "language",
                "indexes": [
                    models.Index(fields=["name"], name="language_name"),
                    models.Index(
                        fields=["code_iso_639_1"], name="language_code_iso_639_1"
                    ),
                    models.Index(
                        fields=["code_iso_language"], name="language_code_iso_language"
                    ),
                ],
            },
        ),
    ]
