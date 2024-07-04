from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.customer.forms import CustomerAdminForm
from apps.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer

        fields = [
            "id",
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "avatar",
            "obs",
            "timezone",
        ]

    mobile_phone = serializers.CharField(
        required=False,
        label=_("model.field.mobile-phone"),
    )

    home_phone = serializers.CharField(
        required=False,
        label=_("model.field.home-phone"),
    )

    gender = serializers.CharField(
        label=_("model.field.gender"),
        max_length=255,
        required=False,
    )

    avatar = serializers.CharField(
        label=_("model.field.avatar"),
        required=False,
    )

    obs = serializers.CharField(
        label=_("model.field.obs"),
        required=False,
    )

    timezone = serializers.CharField(
        required=False,
        label=_("model.field.timezone"),
        max_length=255,
        default=settings.DEFAULT_TIME_ZONE,
    )

    def create(self, validated_data):
        form = CustomerAdminForm(data=validated_data)

        if form.is_valid():
            customer = form.save()
            return customer
        else:
            raise serializers.ValidationError(form.errors)

    def update(self, instance: Customer, validated_data):
        form = CustomerAdminForm(validated_data, instance=instance)

        if form.is_valid():
            form.save()
            return instance

        raise serializers.ValidationError(form.errors)
