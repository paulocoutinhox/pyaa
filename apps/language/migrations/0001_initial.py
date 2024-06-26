# Generated by Django 5.0.3 on 2024-05-16 13:00

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
            ],
            options={
                "verbose_name": "model.language.name",
                "verbose_name_plural": "model.language.name.plural",
                "db_table": "language",
                "indexes": [models.Index(fields=["name"], name="language_name")],
            },
        ),
    ]
