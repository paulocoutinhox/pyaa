from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.customer.models import Customer


class CustomerUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "obs",
            "timezone",
        ]

    first_name = serializers.CharField(
        label=_("model.field.first-name"),
        required=False,
    )

    last_name = serializers.CharField(
        label=_("model.field.last-name"),
        required=False,
    )

    email = serializers.EmailField(
        label=_("model.field.email"),
        write_only=True,
    )

    password = serializers.CharField(
        label=_("model.field.password"),
        write_only=True,
        min_length=8,
    )

    mobile_phone = serializers.CharField(
        required=False,
        label=_("model.field.mobile-phone"),
    )

    home_phone = serializers.CharField(
        required=False,
        label=_("model.field.home-phone"),
    )

    obs = serializers.CharField(
        label=_("model.field.obs"),
        required=False,
    )

    def validate(self, data):
        # this serializer only validates the data, not saving automatically
        # add any custom validation here if needed
        return data


class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "avatar",
            "obs",
            "timezone",
        ]

    first_name = serializers.CharField(
        label=_("model.field.first-name"),
        required=False,
    )

    last_name = serializers.CharField(
        label=_("model.field.last-name"),
        required=False,
    )

    email = serializers.EmailField(
        label=_("model.field.email"),
        write_only=True,
    )

    password = serializers.CharField(
        label=_("model.field.password"),
        write_only=True,
        min_length=8,
    )

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

    def validate(self, data):
        # this serializer only validates the data, not updating automatically
        # add any custom validation here if needed
        return data


class CustomerMeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    timezone = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "language",
            "mobile_phone",
            "home_phone",
            "gender",
            "avatar",
            "obs",
            "timezone",
        ]
