from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.customer.models import Customer
from apps.language.serializers import LanguageSerializer
from apps.user.serializers import UserSerializer


class CustomerUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "nickname",
            "email",
            "cpf",
            "mobile_phone",
            "password",
            "language",
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
        required=False,
    )

    cpf = serializers.CharField(
        label=_("model.field.cpf"),
        write_only=True,
        required=False,
    )

    mobile_phone = serializers.CharField(
        label=_("model.field.mobile-phone"),
        write_only=True,
        required=False,
    )

    password = serializers.CharField(
        label=_("model.field.password"),
        write_only=True,
        min_length=8,
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
        # this serializer only validates the data, not saving automatically
        # add any custom validation here if needed
        return data


class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "nickname",
            "email",
            "cpf",
            "mobile_phone",
            "password",
            "language",
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
        required=False,
    )

    cpf = serializers.CharField(
        label=_("model.field.cpf"),
        write_only=True,
        required=False,
    )

    mobile_phone = serializers.CharField(
        label=_("model.field.mobile-phone"),
        write_only=True,
        required=False,
    )

    password = serializers.CharField(
        label=_("model.field.password"),
        write_only=True,
        min_length=8,
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
    user = UserSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    timezone = serializers.CharField(read_only=True)

    class Meta:
        model = Customer

        fields = [
            "id",
            "user",
            "language",
            "nickname",
            "gender",
            "avatar",
            "credits",
            "obs",
            "timezone",
            "created_at",
            "updated_at",
        ]
