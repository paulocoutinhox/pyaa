# Generated by Django 5.2 on 2025-04-10 03:27

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("customer", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerGenderSummary",
            fields=[],
            options={
                "verbose_name": "model.customer-gender-summary.name",
                "verbose_name_plural": "model.customer-gender-summary.name",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("customer.customer",),
        ),
    ]
