# Generated by Django 5.2 on 2025-04-07 20:10

import apps.customer.fields
import django.db.models.deletion
import timezone_field.fields
import tinymce.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("language", "0001_initial"),
        ("sites", "0002_alter_domain_unique"),
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
                    "nickname",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="model.field.nickname",
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
                    "timezone",
                    timezone_field.fields.TimeZoneField(
                        default="America/Sao_Paulo",
                        max_length=255,
                        verbose_name="model.field.timezone",
                    ),
                ),
                (
                    "activate_token",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="model.field.activate-token",
                    ),
                ),
                (
                    "recovery_token",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="model.field.recovery-token",
                    ),
                ),
                (
                    "credits",
                    models.IntegerField(default=0, verbose_name="model.field.credits"),
                ),
                (
                    "obs",
                    tinymce.models.HTMLField(
                        blank=True, null=True, verbose_name="model.field.obs"
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
                        default=0,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="language.language",
                        verbose_name="model.field.language",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customers",
                        to="sites.site",
                        verbose_name="model.field.site",
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
                    models.Index(fields=["nickname"], name="customer_nickname"),
                    models.Index(fields=["gender"], name="customer_gender"),
                    models.Index(
                        fields=["activate_token"], name="customer_activate_token"
                    ),
                    models.Index(
                        fields=["recovery_token"], name="customer_recovery_token"
                    ),
                    models.Index(fields=["created_at"], name="customer_created_at"),
                ],
            },
        ),
    ]
