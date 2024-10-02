from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from apps.language.models import Language


class LanguageModelTest(TestCase):
    def test_language_creation(self):
        # create a language instance and verify its existence in the database
        language = Language.objects.create(
            name="English",
            native_name="English",
            code_iso_639_1="en",
            code_iso_language="en-US",
        )
        self.assertTrue(Language.objects.filter(name="English").exists())

    def test_language_deletion(self):
        # create a language instance, delete it, and verify its non-existence in the database
        language = Language.objects.create(
            name="English",
            native_name="English",
            code_iso_639_1="en",
            code_iso_language="en-US",
        )
        language.delete()
        self.assertFalse(Language.objects.filter(name="English").exists())

    def test_get_language(self):
        # create a language instance, fetch it from the database, and verify its name
        language = Language.objects.create(
            name="English",
            native_name="English",
            code_iso_639_1="en",
            code_iso_language="en-US",
        )
        fetched_language = Language.objects.get(name="English")
        self.assertEqual(fetched_language.name, "English")

    def test_get_nonexistent_language(self):
        # attempt to fetch a non-existent language and verify that an exception is raised
        with self.assertRaises(ObjectDoesNotExist):
            Language.objects.get(name="Nonexistent")

    def test_language_str(self):
        # create a language instance and verify its string representation
        language = Language.objects.create(
            name="English",
            native_name="English",
            code_iso_639_1="en",
            code_iso_language="en-US",
        )
        self.assertEqual(str(language), "English")
