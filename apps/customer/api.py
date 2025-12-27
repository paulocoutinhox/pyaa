from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError, ValidationError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken

from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.customer.schemas import (
    CustomerCreateResponseSchema,
    CustomerResponseSchema,
    CustomerUserCreateSchema,
    CustomerUserUpdateSchema,
)
from apps.language.models import Language

User = get_user_model()

router = Router()


@router.post(
    "/", response={201: CustomerCreateResponseSchema}, auth=None, by_alias=True
)
def create_customer(request, data: CustomerUserCreateSchema):
    with transaction.atomic():
        user_data = {
            "first_name": data.first_name or "",
            "last_name": data.last_name or "",
            "email": data.email or "",
            "cpf": data.cpf or "",
            "mobile_phone": data.mobile_phone or "",
        }

        user = User(**user_data)

        try:
            user.set_password(data.password)
            user.full_clean()
        except DjangoValidationError as e:
            raise ValidationError([{"user": e.message_dict}])

        user.save()

        customer_data = {
            "user": user,
            "nickname": data.nickname or "",
            "gender": data.gender or "",
            "obs": data.obs or "",
            "timezone": data.timezone,
        }

        if data.language:
            try:
                language = Language.objects.get(id=data.language)
                customer_data["language"] = language
            except Language.DoesNotExist:
                pass

        customer = Customer.objects.create(**customer_data)
        CustomerHelper.post_save(customer)

        customer.refresh_from_db()

        refresh = RefreshToken.for_user(user)

        customer.token = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return customer


@router.put("/", response=CustomerResponseSchema, auth=JWTAuth(), by_alias=True)
def update_customer_put(request, data: CustomerUserUpdateSchema):
    return _update_customer(request, data)


@router.patch("/", response=CustomerResponseSchema, auth=JWTAuth(), by_alias=True)
def update_customer_patch(request, data: CustomerUserUpdateSchema):
    return _update_customer(request, data)


def _update_customer(request, data: CustomerUserUpdateSchema):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        raise HttpError(404, "Customer not found.")

    with transaction.atomic():
        user = customer.user

        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.email is not None:
            user.email = data.email
        if data.cpf is not None:
            user.cpf = data.cpf
        if data.mobile_phone is not None:
            user.mobile_phone = data.mobile_phone

        if data.password:
            user.set_password(data.password)

        try:
            user.full_clean()
        except DjangoValidationError as e:
            raise ValidationError([{"user": e.message_dict}])

        user.save()

        if data.nickname is not None:
            customer.nickname = data.nickname
        if data.gender is not None:
            customer.gender = data.gender
        if data.obs is not None:
            customer.obs = data.obs
        if data.timezone is not None:
            customer.timezone = data.timezone
        if data.language is not None:
            try:
                language = Language.objects.get(id=data.language)
                customer.language = language
            except Language.DoesNotExist:
                pass

        customer.save()

    return customer


@router.get("/me/", response=CustomerResponseSchema, auth=JWTAuth(), by_alias=True)
def get_customer_me(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        raise HttpError(404, "Customer not found.")

    return customer
