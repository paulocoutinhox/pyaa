# Generated by Django 5.1.1 on 2024-10-13 00:53

import django.db.models.deletion
import tinymce.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("customer", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
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
                    "gateway",
                    models.CharField(
                        choices=[("stripe", "enum.shop-payment-gateway.stripe")],
                        max_length=255,
                        verbose_name="model.field.payment-gateway",
                    ),
                ),
                (
                    "external_id",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="model.field.external_id",
                    ),
                ),
                (
                    "currency",
                    models.CharField(max_length=3, verbose_name="model.field.currency"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="model.field.price",
                    ),
                ),
                (
                    "credits",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="model.field.credits"
                    ),
                ),
                (
                    "frequency_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("day", "enum.shop-plan-frequency-type.day"),
                            ("week", "enum.shop-plan-frequency-type.week"),
                            ("month", "enum.shop-plan-frequency-type.month"),
                            ("year", "enum.shop-plan-frequency-type.year"),
                            ("quarter", "enum.shop-plan-frequency-type.quarter"),
                            (
                                "semi_annual",
                                "enum.shop-plan-frequency-type.semi_annual",
                            ),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="model.field.frequency-type",
                    ),
                ),
                (
                    "frequency_amount",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="model.field.frequency-amount",
                    ),
                ),
                (
                    "description",
                    tinymce.models.HTMLField(
                        blank=True, null=True, verbose_name="model.field.description"
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(
                        default=0, verbose_name="model.field.sort-order"
                    ),
                ),
                (
                    "featured",
                    models.BooleanField(
                        default=False, verbose_name="model.field.featured"
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
            ],
            options={
                "verbose_name": "model.shop-plan.name",
                "verbose_name_plural": "model.shop-plan.name.plural",
                "db_table": "shop_plan",
                "indexes": [
                    models.Index(fields=["name"], name="shop_plan_name"),
                    models.Index(fields=["tag"], name="shop_plan_tag"),
                    models.Index(fields=["gateway"], name="shop_plan_gateway"),
                    models.Index(fields=["currency"], name="shop_plan_currency"),
                    models.Index(
                        fields=["frequency_type"], name="shop_plan_frequency_type"
                    ),
                    models.Index(fields=["active"], name="shop_plan_active"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CreditLog",
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
                    "amount",
                    models.IntegerField(default=0, verbose_name="model.field.amount"),
                ),
                (
                    "object_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("general", "enum.shop-object-type.general"),
                            ("unknown", "enum.shop-object-type.unknown"),
                            ("bonus", "enum.shop-object-type.bonus"),
                            ("subscription", "enum.shop-object-type.subscription"),
                        ],
                        default="unknown",
                        max_length=255,
                        null=True,
                        verbose_name="model.field.object-type",
                    ),
                ),
                (
                    "object_id",
                    models.BigIntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="model.field.object-id",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="model.field.description"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="model.field.created-at"
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer.customer",
                        verbose_name="model.field.customer",
                    ),
                ),
            ],
            options={
                "verbose_name": "model.shop-credit-log.name",
                "verbose_name_plural": "model.shop-credit-log.name.plural",
                "db_table": "shop_credit_log",
                "indexes": [
                    models.Index(
                        fields=["object_id", "object_type"],
                        name="shop_credit_log_object",
                    ),
                    models.Index(
                        fields=["object_type"], name="shop_credit_log_object_type"
                    ),
                    models.Index(fields=["customer"], name="shop_credit_log_customer"),
                    models.Index(
                        fields=["created_at"], name="shop_credit_log_created_at"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="EventLog",
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
                    "object_id",
                    models.BigIntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        verbose_name="model.field.object-id",
                    ),
                ),
                (
                    "object_type",
                    models.CharField(
                        choices=[
                            ("general", "enum.shop-object-type.general"),
                            ("unknown", "enum.shop-object-type.unknown"),
                            ("bonus", "enum.shop-object-type.bonus"),
                            ("subscription", "enum.shop-object-type.subscription"),
                        ],
                        default="unknown",
                        max_length=255,
                        verbose_name="model.field.object-type",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="model.field.status",
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        blank=True,
                        max_length=3,
                        null=True,
                        verbose_name="model.field.currency",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="model.field.amount",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="model.field.description"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="model.field.created-at"
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer.customer",
                        verbose_name="model.field.customer",
                    ),
                ),
            ],
            options={
                "verbose_name": "model.shop-event-log.name",
                "verbose_name_plural": "model.shop-event-log.name.plural",
                "db_table": "shop_event_log",
                "indexes": [
                    models.Index(
                        fields=["object_id", "object_type"],
                        name="shop_event_log_object",
                    ),
                    models.Index(
                        fields=["object_type"], name="shop_event_log_object_type"
                    ),
                    models.Index(fields=["customer"], name="shop_event_log_customer"),
                    models.Index(fields=["status"], name="shop_event_log_status"),
                    models.Index(
                        fields=["created_at"], name="shop_event_log_created_at"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Subscription",
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
                    "token",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="model.field.token",
                    ),
                ),
                (
                    "external_id",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="model.field.external_id",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("initial", "enum.shop-subscription-status.initial"),
                            ("analysis", "enum.shop-subscription-status.analysis"),
                            ("active", "enum.shop-subscription-status.active"),
                            ("suspended", "enum.shop-subscription-status.suspended"),
                            ("canceled", "enum.shop-subscription-status.canceled"),
                            ("failed", "enum.shop-subscription-status.failed"),
                        ],
                        default="initial",
                        max_length=255,
                        verbose_name="model.field.status",
                    ),
                ),
                (
                    "expire_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="model.field.expire-at"
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
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer.customer",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shop.plan"
                    ),
                ),
            ],
            options={
                "verbose_name": "model.shop-subscription.name",
                "verbose_name_plural": "model.shop-subscription.name.plural",
                "db_table": "shop_subscription",
                "indexes": [
                    models.Index(fields=["token"], name="shop_subscription_token"),
                    models.Index(
                        fields=["customer"], name="shop_subscription_customer"
                    ),
                    models.Index(fields=["plan"], name="shop_subscription_plan"),
                    models.Index(
                        fields=["external_id"], name="shop_subscription_external_id"
                    ),
                    models.Index(
                        fields=["expire_at"], name="shop_subscription_expire_at"
                    ),
                    models.Index(fields=["status"], name="shop_subscription_status"),
                ],
            },
        ),
    ]
