from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from account import enums
from account.forms import CustomerAdminForm
from account.models import Customer
from main.settings import DEFAULT_TIME_ZONE


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer

        fields = [
            "id",
            "name",
            "email",
            "password",
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "obs",
            "timezone",
        ]

    password = serializers.CharField(
        required=True,
        label=_("form.label.password"),
        write_only=True,
    )

    mobile_phone = serializers.CharField(
        required=False,
        label=_("form.label.mobile-phone"),
    )

    home_phone = serializers.CharField(
        required=False,
        label=_("form.label.home-phone"),
    )

    timezone = serializers.CharField(
        required=False,
        label=_("form.label.timezone"),
        max_length=255,
        default=DEFAULT_TIME_ZONE,
        write_only=True,
    )

    def create(self, validated_data):
        validated_data["confirm_password"] = validated_data["password"]
        validated_data["status"] = enums.CustomerStatus.ACTIVE

        form = CustomerAdminForm(data=validated_data)

        if form.is_valid():
            customer = form.save()
            return customer
        else:
            raise serializers.ValidationError(form.errors)

    def update(self, instance: Customer, validated_data):
        if "password" in validated_data:
            validated_data["confirm_password"] = validated_data["password"]

        if "timezone" not in validated_data:
            validated_data["timezone"] = instance.timezone

        validated_data["status"] = instance.status

        form = CustomerAdminForm(validated_data, instance=instance)

        if form.is_valid():
            form.save()
            return instance

        raise serializers.ValidationError(form.errors)
