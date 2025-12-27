from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from pydantic import ValidationError

from apps.customer.models import Customer
from apps.customer.schemas import (
    CustomerResponseSchema,
    CustomerUserCreateSchema,
    CustomerUserUpdateSchema,
)
from apps.language.models import Language


class CustomerUserCreateSchemaTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_validate_customer_data(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "password123",
            "language": 1,
            "mobile_phone": "123456789",
            "nickname": "johndoe",
            "gender": "male",
            "obs": "Some observations",
            "timezone": "America/Sao_Paulo",
        }

        schema = CustomerUserCreateSchema(**customer_data)
        self.assertEqual(schema.email, "johndoe@example.com")
        self.assertEqual(schema.first_name, "John")

    def test_validate_customer_data_invalid_email(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "password123",
            "language": 1,
        }

        with self.assertRaises(ValidationError) as context:
            CustomerUserCreateSchema(**customer_data)
        self.assertIn("email", str(context.exception))

    def test_validate_customer_data_missing_password(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "language": 1,
        }

        with self.assertRaises(ValidationError) as context:
            CustomerUserCreateSchema(**customer_data)
        self.assertIn("password", str(context.exception))


class CustomerUserUpdateSchemaTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_validate_update_customer_data(self):
        customer_data = {
            "email": "johndoe@example.com",
            "password": "password123",
            "language": 1,
            "mobile_phone": "123456789",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
            "nickname": "jdoe",
        }

        schema = CustomerUserUpdateSchema(**customer_data)
        self.assertEqual(schema.email, "johndoe@example.com")
        self.assertEqual(schema.nickname, "jdoe")

    def test_validate_update_customer_data_invalid_email(self):
        customer_data = {
            "email": "invalid-email",
        }

        with self.assertRaises(ValidationError) as context:
            CustomerUserUpdateSchema(**customer_data)
        self.assertIn("email", str(context.exception))

    def test_validate_update_customer_partial(self):
        customer_data = {
            "nickname": "new_nickname",
        }

        schema = CustomerUserUpdateSchema(**customer_data)
        self.assertEqual(schema.nickname, "new_nickname")


class CustomerResponseSchemaTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )
        self.site = Site.objects.get_current()
        self.language = Language.objects.get(id=1)
        self.customer = Customer.objects.create(
            user=self.user,
            site=self.site,
            language=self.language,
            nickname="tester",
            gender="male",
            timezone="UTC",
            credits=100,
            obs="Test customer",
        )

    def test_schema_from_orm(self):
        schema = CustomerResponseSchema.from_orm(self.customer)
        data = schema.model_dump(by_alias=True)

        expected_fields = [
            "id",
            "user",
            "language",
            "nickname",
            "gender",
            "avatar",
            "credits",
            "obs",
            "timezone",
            "createdAt",
            "updatedAt",
        ]

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_schema_field_content(self):
        schema = CustomerResponseSchema.from_orm(self.customer)
        data = schema.model_dump(by_alias=True)

        self.assertEqual(data["nickname"], "tester")
        self.assertEqual(data["gender"], "male")
        self.assertEqual(data["credits"], 100)
        self.assertEqual(data["obs"], "Test customer")
        self.assertEqual(data["timezone"], "UTC")
