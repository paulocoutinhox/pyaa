# Generated by Django 5.1.2 on 2024-10-24 20:19

import apps.customer.fields
import django.db.models.deletion
import timezone_field.fields
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("language", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
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
                    "mobile_phone",
                    models.CharField(
                        blank=True,
                        max_length=11,
                        null=True,
                        verbose_name="model.field.mobile-phone",
                    ),
                ),
                (
                    "home_phone",
                    models.CharField(
                        blank=True,
                        max_length=11,
                        null=True,
                        verbose_name="model.field.home-phone",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("male", "enum.customer-gender.male"),
                            ("female", "enum.customer-gender.female"),
                            ("none", "enum.customer-gender.none"),
                        ],
                        default="none",
                        max_length=255,
                        null=True,
                        verbose_name="model.field.gender",
                    ),
                ),
                (
                    "avatar",
                    apps.customer.fields.CustomerImageField(
                        blank=True,
                        crop=["middle", "center"],
                        force_format=None,
                        keep_meta=True,
                        null=True,
                        quality=100,
                        scale=None,
                        size=[1024, 1024],
                        upload_to="images/customer/avatar/%Y/%m/%d",
                        verbose_name="model.field.avatar",
                    ),
                ),
                (
                    "obs",
                    tinymce.models.HTMLField(
                        blank=True, null=True, verbose_name="model.field.obs"
                    ),
                ),
                (
                    "timezone",
                    timezone_field.fields.TimeZoneField(
                        default="America/Sao_Paulo",
                        max_length=255,
                        verbose_name="model.field.timezone",
                    ),
                ),
                (
                    "credits",
                    models.IntegerField(default=0, verbose_name="model.field.credits"),
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
                        default=0,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="language.language",
                        verbose_name="model.field.language",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="model.field.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "model.customer.name",
                "verbose_name_plural": "model.customer.name.plural",
                "db_table": "customer",
                "indexes": [
                    models.Index(fields=["language"], name="customer_language"),
                    models.Index(fields=["mobile_phone"], name="customer_mobile_phone"),
                    models.Index(fields=["home_phone"], name="customer_home_phone"),
                    models.Index(fields=["gender"], name="customer_gender"),
                ],
            },
        ),
    ]
