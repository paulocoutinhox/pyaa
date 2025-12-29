from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from fastapi import APIRouter, HTTPException, status

from apps.api.auth.dependencies import CurrentUser
from apps.api.customer.schemas import (
    CustomerCreateResponseSchema,
    CustomerCreateSchema,
    CustomerResponseSchema,
    CustomerUpdateSchema,
)
from apps.customer.helpers import CustomerHelper
from apps.customer.models import Customer
from apps.language.models import Language
from pyaa.fastapi.jwt import create_access_token, create_refresh_token

User = get_user_model()

router = APIRouter()


@sync_to_async
@transaction.atomic
def _create_customer_transaction(data: CustomerCreateSchema):
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"user": e.message_dict}],
        )

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

    # refresh to get language and user
    customer = Customer.objects.select_related("language", "user").get(id=customer.id)

    CustomerHelper.post_save(customer)
    return customer, user


@router.post(
    "",
    response_model=CustomerCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(data: CustomerCreateSchema):
    customer, user = await _create_customer_transaction(data)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    customer_data = CustomerResponseSchema.model_validate(customer).model_dump()
    customer_data["token"] = {"refresh": refresh_token, "access": access_token}
    return CustomerCreateResponseSchema(**customer_data)


@sync_to_async
@transaction.atomic
def _update_customer_transaction(user: User, data: CustomerUpdateSchema):
    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found."
        )

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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"user": e.message_dict}],
        )

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

    # refresh to get language and user
    customer = Customer.objects.select_related("language", "user").get(id=customer.id)

    return customer, user


async def _update_customer(user: User, data: CustomerUpdateSchema):
    customer, user = await _update_customer_transaction(user, data)
    return CustomerResponseSchema.model_validate(customer)


@router.put("", response_model=CustomerResponseSchema)
async def update_customer_put(data: CustomerUpdateSchema, user: CurrentUser):
    return await _update_customer(user, data)


@router.patch("", response_model=CustomerResponseSchema)
async def update_customer_patch(data: CustomerUpdateSchema, user: CurrentUser):
    return await _update_customer(user, data)


@router.get("/me", response_model=CustomerResponseSchema)
async def get_customer_me(user: CurrentUser):
    try:
        customer = await Customer.objects.select_related("language", "user").aget(
            user=user
        )
    except Customer.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found."
        )

    return CustomerResponseSchema.model_validate(customer)
