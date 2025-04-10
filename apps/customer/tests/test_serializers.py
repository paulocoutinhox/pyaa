from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.customer.models import Customer
from apps.customer.serializers import (
    CustomerMeSerializer,
    CustomerUserCreateSerializer,
    CustomerUserUpdateSerializer,
)
from apps.language.models import Language
from apps.site.models import Site


class CustomerUserCreateSerializerTest(APITestCase):
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

        serializer = CustomerUserCreateSerializer(data=customer_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_customer_data_invalid_email(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "password123",
            "language": 1,
        }

        serializer = CustomerUserCreateSerializer(data=customer_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_validate_customer_data_missing_password(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "language": 1,
        }

        serializer = CustomerUserCreateSerializer(data=customer_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_validate_customer_data_short_password(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "short",
            "language": 1,
        }

        serializer = CustomerUserCreateSerializer(data=customer_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_validate_customer_data_cpf(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "password123",
            "language": 1,
            "cpf": "12345678900",
        }

        serializer = CustomerUserCreateSerializer(data=customer_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class CustomerUserUpdateSerializerTest(APITestCase):
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

        serializer = CustomerUserUpdateSerializer(data=customer_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_update_customer_data_invalid_email(self):
        customer_data = {
            "email": "invalid-email",
        }

        serializer = CustomerUserUpdateSerializer(data=customer_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_validate_update_customer_data_short_password(self):
        customer_data = {
            "password": "short",
        }

        serializer = CustomerUserUpdateSerializer(data=customer_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_validate_update_customer_partial(self):
        customer_data = {
            "nickname": "new_nickname",
        }

        serializer = CustomerUserUpdateSerializer(data=customer_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class CustomerMeSerializerTest(TestCase):
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

    def test_serializer_contains_expected_fields(self):
        serializer = CustomerMeSerializer(instance=self.customer)
        data = serializer.data

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
            "created_at",
            "updated_at",
        ]

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serializer_field_content(self):
        serializer = CustomerMeSerializer(instance=self.customer)
        data = serializer.data

        self.assertEqual(data["nickname"], "tester")
        self.assertEqual(data["gender"], "male")
        self.assertEqual(data["credits"], 100)
        self.assertEqual(data["obs"], "Test customer")
        self.assertEqual(data["timezone"], "UTC")
        self.assertEqual(data["user"]["first_name"], "Test")
        self.assertEqual(data["user"]["last_name"], "User")
        self.assertEqual(data["user"]["email"], "test@example.com")
        self.assertEqual(data["language"]["id"], 1)
