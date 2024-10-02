from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.customer.serializers import (
    CustomerMeSerializer,
    CustomerUserCreateSerializer,
    CustomerUserUpdateSerializer,
)

User = get_user_model()


class CustomerView(GenericAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CustomerUserCreateSerializer
        return CustomerUserUpdateSerializer

    # manually handle customer and user creation
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # validate the data, but don't save anything yet
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # start a transaction to ensure both user and customer are created together
        with transaction.atomic():
            # extract user data from validated_data
            user_data = {
                "email": validated_data.pop("email"),
                "first_name": validated_data.pop("first_name", ""),
                "last_name": validated_data.pop("last_name", ""),
            }

            # create the user manually
            user = User(**user_data)

            try:
                user.set_password(validated_data.pop("password"))
                user.full_clean()
            except ValidationError as e:
                raise serializers.ValidationError({"user": e.message_dict})

            user.save()

            # create the customer manually
            validated_data["user"] = user
            customer = Customer.objects.create(**validated_data)
            CustomerHelper.post_save(customer)

            # generate JWT token for the created user
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "first_name": customer.user.first_name,
                    "last_name": customer.user.last_name,
                    "email": customer.user.email,
                    "language": customer.language.id,
                    "mobile_phone": customer.mobile_phone,
                    "home_phone": customer.home_phone,
                    "gender": customer.gender,
                    "avatar": customer.avatar.url if customer.avatar else None,
                    "obs": customer.obs,
                    "timezone": str(customer.timezone),
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, *args, **kwargs):
        return self.update_customer(request)

    def patch(self, request, *args, **kwargs):
        return self.update_customer(request)

    def update_customer(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # create serializer instance with the partial update data
        serializer = self.get_serializer(customer, data=request.data, partial=True)

        # validate the data without saving yet
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # manually update user and customer data inside a transaction
        with transaction.atomic():
            user_data = {
                "email": validated_data.pop(
                    "email",
                    customer.user.email,
                ),
                "first_name": validated_data.pop(
                    "first_name", customer.user.first_name
                ),
                "last_name": validated_data.pop(
                    "last_name",
                    customer.user.last_name,
                ),
            }

            # update user manually
            user = customer.user
            user.email = user_data["email"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]

            # check if password is provided and set it using set_password
            if "password" in validated_data and validated_data["password"]:
                user.set_password(validated_data.pop("password"))

            try:
                user.full_clean()
            except ValidationError as e:
                raise serializers.ValidationError({"user": e.message_dict})

            # save updated user data
            user.save()

            # update customer fields manually
            for attr, value in validated_data.items():
                setattr(customer, attr, value)

            # save updated customer data
            customer.save()

        return Response(
            {
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "language": customer.language.id,
                "mobile_phone": customer.mobile_phone,
                "home_phone": customer.home_phone,
                "gender": customer.gender,
                "avatar": customer.avatar.url if customer.avatar else None,
                "obs": customer.obs,
                "timezone": str(customer.timezone),
            },
            status=status.HTTP_200_OK,
        )


class CustomerMeView(GenericAPIView):
    serializer_class = CustomerMeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
