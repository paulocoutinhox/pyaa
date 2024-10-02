from rest_framework.test import APITestCase

from apps.customer.serializers import (
    CustomerMeSerializer,
    CustomerUserCreateSerializer,
    CustomerUserUpdateSerializer,
)


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
            "home_phone": "987654321",
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


class CustomerUserUpdateSerializerTest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_validate_update_customer_data(self):
        customer_data = {
            "email": "johndoe@example.com",
            "password": "password123",
            "language": 1,
            "mobile_phone": "123456789",
            "home_phone": "987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
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


class CustomerMeSerializerTest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_validate_customer_me_data(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "language": 1,
            "mobile_phone": "123456789",
            "home_phone": "987654321",
            "gender": "male",
            "obs": "Some observations",
            "timezone": "America/Sao_Paulo",
        }

        serializer = CustomerMeSerializer(data=customer_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
