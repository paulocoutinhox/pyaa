from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from ninja_jwt.tokens import RefreshToken

from apps.customer.models import Customer

User = get_user_model()


class CustomerAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_create_and_get_customer(self):
        customer_data = {
            "email": "testuser3@example.com",
            "password": "testpassword",
            "firstName": "Test",
            "lastName": "User",
            "language": 1,
            "mobilePhone": "1234567890",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        response = self.client.post(
            "/api/customer/", customer_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("access", data["token"])
        self.assertIn("refresh", data["token"])

        access_token = data["token"]["access"]

        response = self.client.get(
            "/api/customer/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["firstName"], "Test")
        self.assertEqual(data["user"]["lastName"], "User")
        self.assertEqual(data["user"]["email"], "testuser3@example.com")
        self.assertEqual(data["user"]["mobilePhone"], "1234567890")
        self.assertEqual(data["gender"], "male")

    def test_get_customer_me(self):
        user = User.objects.create_user(
            email="testuser5@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            mobile_phone="1234567890",
        )

        refresh = RefreshToken.for_user(user)

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
            timezone="America/Sao_Paulo",
        )

        response = self.client.get(
            "/api/customer/me/", HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["firstName"], "Test")
        self.assertEqual(data["user"]["lastName"], "User")
        self.assertEqual(data["user"]["email"], "testuser5@example.com")
        self.assertEqual(data["user"]["mobilePhone"], "1234567890")
        self.assertEqual(data["gender"], "male")

    def test_get_customer_me_invalid_token(self):
        response = self.client.get("/api/customer/me/")
        self.assertEqual(response.status_code, 401)

    def test_patch_update_customer_with_patch(self):
        user = User.objects.create_user(
            email="testuser6@example.com",
            password="testpassword",
            mobile_phone="1234567890",
        )

        refresh = RefreshToken.for_user(user)

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        patch_data = {
            "language": 1,
            "mobilePhone": "11111111111",
            "timezone": "America/Sao_Paulo",
        }

        response = self.client.patch(
            "/api/customer/",
            patch_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["mobilePhone"], "11111111111")

    def test_patch_update_customer_with_put(self):
        user = User.objects.create_user(
            email="testuser7@example.com",
            password="testpassword",
            mobile_phone="1234567890",
        )

        refresh = RefreshToken.for_user(user)

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        patch_data = {
            "language": 1,
            "mobilePhone": "22222222222",
            "timezone": "America/Sao_Paulo",
        }

        response = self.client.put(
            "/api/customer/",
            patch_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user"]["mobilePhone"], "22222222222")

    def test_update_customer_invalid_token(self):
        update_data = {
            "mobilePhone": "0987654321",
            "gender": "female",
            "language": 1,
        }

        response = self.client.put(
            "/api/customer/", update_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_patch_update_customer_invalid_token(self):
        patch_data = {
            "mobilePhone": "0987654321",
            "gender": "female",
            "language": 1,
        }

        response = self.client.patch(
            "/api/customer/", patch_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_update_customer_not_found(self):
        user = User.objects.create_user(
            email="testuser8@example.com", password="testpassword"
        )

        refresh = RefreshToken.for_user(user)

        update_data = {
            "mobilePhone": "1234567890",
            "gender": "male",
            "language": 1,
        }

        response = self.client.put(
            "/api/customer/",
            update_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"], "Customer not found.")

    def test_create_user_validation_error(self):
        customer_data = {
            "email": "invalid-email",
            "password": "testpassword",
            "firstName": "Test",
            "lastName": "User",
            "language": 1,
            "mobilePhone": "1234567890",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        response = self.client.post(
            "/api/customer/", customer_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)

    @patch("apps.user.models.User.full_clean")
    def test_create_user_full_clean_validation_error(self, mock_full_clean):
        mock_full_clean.side_effect = ValidationError({"email": "Invalid email format"})

        customer_data = {
            "email": "testuser10@example.com",
            "password": "testpassword",
            "firstName": "Test",
            "lastName": "User",
            "language": 1,
            "mobilePhone": "1234567890",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        response = self.client.post(
            "/api/customer/", customer_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)

    def test_update_customer_with_valid_password(self):
        user = User.objects.create_user(
            email="testuser11@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            mobile_phone="1234567890",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        refresh = RefreshToken.for_user(user)

        update_data = {
            "password": "NewValidPassword123",
        }

        response = self.client.put(
            "/api/customer/",
            update_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewValidPassword123"))

    def test_update_nickname(self):
        user = User.objects.create_user(
            email="testuser15@example.com",
            password="testpassword",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        refresh = RefreshToken.for_user(user)

        update_data = {
            "nickname": "TestNickname",
        }

        response = self.client.patch(
            "/api/customer/",
            update_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["nickname"], "TestNickname")

        customer.refresh_from_db()
        self.assertEqual(customer.nickname, "TestNickname")
