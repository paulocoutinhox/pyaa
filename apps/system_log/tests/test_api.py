from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.customer.models import Customer
from apps.system_log.enums import LogLevel
from apps.system_log.models import SystemLog

User = get_user_model()


class SystemLogAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    @override_settings(SYSTEM_LOG_API_ENABLED=True)
    def test_create_system_log(self):
        log_data = {
            "level": LogLevel.INFO,
            "description": "Test log entry",
            "category": "test",
        }

        response = self.client.post(
            "/api/system-log/create/", log_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        self.assertTrue(SystemLog.objects.filter(description="Test log entry").exists())

    @override_settings(SYSTEM_LOG_API_ENABLED=False)
    def test_create_system_log_api_disabled(self):
        log_data = {
            "level": LogLevel.INFO,
            "description": "Test log entry",
            "category": "test",
        }

        response = self.client.post(
            "/api/system-log/create/", log_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], "System log API is disabled")

    @override_settings(SYSTEM_LOG_API_ENABLED=True)
    def test_create_system_log_with_different_levels(self):
        for level in [LogLevel.ERROR, LogLevel.WARNING]:
            log_data = {
                "level": level,
                "description": f"{level} log",
                "category": "test",
            }

            response = self.client.post(
                "/api/system-log/create/", log_data, content_type="application/json"
            )

            self.assertEqual(response.status_code, 200)

        self.assertEqual(SystemLog.objects.count(), 2)

    @override_settings(SYSTEM_LOG_API_ENABLED=True)
    def test_create_system_log_with_authenticated_user(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        customer = Customer.objects.create(
            user=user,
            language_id=1,
            gender="male",
        )

        self.client.force_login(user)

        log_data = {
            "level": LogLevel.INFO,
            "description": "Authenticated user log",
            "category": "test",
        }

        response = self.client.post(
            "/api/system-log/create/", log_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        log = SystemLog.objects.get(description="Authenticated user log")
        self.assertEqual(log.customer, customer)
