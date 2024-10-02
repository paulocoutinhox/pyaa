from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.customer.models import Customer

User = get_user_model()


class CustomerAPITest(APITestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        self.client = APIClient()

    def test_create_and_get_customer(self):
        customer_data = {
            "email": "testuser3@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        create_url = reverse("customer")
        response = self.client.post(create_url, customer_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])

        access_token = response.data["token"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        me_url = reverse("customer-me")
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")
        self.assertEqual(response.data["email"], "testuser3@example.com")
        self.assertEqual(response.data["mobile_phone"], "1234567890")
        self.assertEqual(response.data["home_phone"], "0987654321")
        self.assertEqual(response.data["gender"], "male")

    def test_get_customer_me(self):
        user = User.objects.create_user(
            email="testuser5@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
            timezone="America/Sao_Paulo",
        )

        me_url = reverse("customer-me")
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")
        self.assertEqual(response.data["email"], "testuser5@example.com")
        self.assertEqual(response.data["mobile_phone"], "1234567890")
        self.assertEqual(response.data["home_phone"], "0987654321")
        self.assertEqual(response.data["gender"], "male")

    def test_get_customer_me_invalid_token(self):
        me_url = reverse("customer-me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_update_customer_with_patch(self):
        user = User.objects.create_user(
            email="testuser6@example.com", password="testpassword"
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        patch_data = {
            "language": 1,
            "mobile_phone": "11111111111",
            "timezone": "America/Sao_Paulo",
        }

        patch_url = reverse("customer")
        response = self.client.patch(patch_url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mobile_phone"], "11111111111")

    def test_patch_update_customer_with_put(self):
        user = User.objects.create_user(
            email="testuser6@example.com", password="testpassword"
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        patch_data = {
            "language": 1,
            "mobile_phone": "22222222222",
            "timezone": "America/Sao_Paulo",
        }

        patch_url = reverse("customer")
        response = self.client.put(patch_url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mobile_phone"], "22222222222")

    def test_update_customer_invalid_token(self):
        update_data = {
            "mobile_phone": "0987654321",
            "home_phone": "1234567890",
            "gender": "female",
            "language": 1,
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_update_customer_invalid_token(self):
        patch_data = {
            "mobile_phone": "0987654321",
            "home_phone": "1234567890",
            "gender": "female",
            "language": 1,
        }

        patch_url = reverse("customer")
        response = self.client.patch(patch_url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customer_not_found(self):
        user = User.objects.create_user(
            email="testuser7@example.com", password="testpassword"
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        update_data = {
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "language": 1,
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Customer not found.")

    def test_update_customer_invalid_data(self):
        user = User.objects.create_user(
            email="testuser8@example.com", password="testpassword"
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        update_data = {
            "home_phone": "0987654321",
            "gender": "female",
            "language": 99,
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("language", response.data)

    def test_create_user_validation_error(self):
        customer_data = {
            "email": "invalid-email",  # invalid email format
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        create_url = reverse("customer")
        response = self.client.post(create_url, customer_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_user_with_existing_email(self):
        # create a user with the same email first
        User.objects.create_user(
            email="testuser_existing@example.com", password="testpassword"
        )

        customer_data = {
            "email": "testuser_existing@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        create_url = reverse("customer")
        response = self.client.post(create_url, customer_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)

    @patch("apps.user.models.User.full_clean")
    def test_create_user_full_clean_validation_error(self, mock_full_clean):
        mock_full_clean.side_effect = ValidationError({"email": "Invalid email format"})

        customer_data = {
            "email": "testuser10@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "language": 1,
            "mobile_phone": "1234567890",
            "home_phone": "0987654321",
            "gender": "male",
            "timezone": "America/Sao_Paulo",
        }

        create_url = reverse("customer")
        response = self.client.post(create_url, customer_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"][0], "Invalid email format")

    def test_update_customer_with_valid_password(self):
        user = User.objects.create_user(
            email="testuser11@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        update_data = {
            "password": "NewValidPassword123",
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewValidPassword123"))

    def test_update_customer_with_invalid_password(self):
        user = User.objects.create_user(
            email="testuser12@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        update_data = {
            "password": "123",
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    @patch("apps.user.models.User.full_clean")
    def test_update_customer_with_invalid_email(self, mock_full_clean):
        user = User.objects.create_user(
            email="testuser13@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        mock_full_clean.side_effect = ValidationError({"email": "Invalid email format"})

        update_data = {
            "email": "invalid-email",
            "password": "NewValidPassword123",
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @patch("apps.user.models.User.full_clean")
    def test_update_customer_validation_error(self, mock_full_clean):
        user = User.objects.create_user(
            email="testuser13@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        Customer.objects.create(
            user=user,
            language_id=1,
            mobile_phone="1234567890",
            home_phone="0987654321",
            gender="male",
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        mock_full_clean.side_effect = ValidationError({"email": "Invalid email format"})

        update_data = {
            "email": "invalid-email@example.com",
            "first_name": "UpdatedName",
            "password": "NewValidPassword123",
        }

        update_url = reverse("customer")
        response = self.client.put(update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)
        self.assertIn("email", response.data["user"])
        self.assertEqual(response.data["user"]["email"][0], "Invalid email format")
