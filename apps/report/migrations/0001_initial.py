# Generated by Django 5.1.7 on 2025-03-29 01:40

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
