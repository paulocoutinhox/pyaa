from django.test import TestCase

from apps.language.models import Language


class LanguageAPITest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_list_languages(self):
        response = self.client.get("/api/language/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertGreater(len(data["items"]), 0)

    def test_list_languages_with_pagination(self):
        response = self.client.get("/api/language/?limit=2&offset=0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)

    def test_create_language(self):
        language_data = {
            "name": "Test Language",
            "nativeName": "Test Native",
            "codeIso6391": "tl",
            "codeIsoLanguage": "test",
        }

        response = self.client.post(
            "/api/language/", language_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Test Language")
        self.assertEqual(data["codeIso6391"], "tl")

        language = Language.objects.get(code_iso_639_1="tl")
        self.assertEqual(language.name, "Test Language")
