from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import activate

from apps.language.helpers import LanguageHelper
from apps.language.models import Language


class LanguageHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # setup initial languages for testing
        self.language_en = Language.objects.get(code_iso_language="en-US")
        self.language_pt = Language.objects.get(code_iso_language="pt-BR")

    def test_get_current_exact_match(self):
        # test exact match for language code
        activate("en-US")
        language = LanguageHelper.get_current()
        self.assertEqual(language, self.language_en)

    def test_get_current_partial_match(self):
        # test partial match for language code
        activate("en-GB")
        language = LanguageHelper.get_current()
        self.assertEqual(language, self.language_en)

    def test_get_current_no_match(self):
        # test no match for language code, should fallback to portuguese
        activate("pt-PT")
        language = LanguageHelper.get_current()
        self.assertEqual(language, self.language_pt)

    def test_get_current_no_languages_registered(self):
        # test behavior when no languages are registered
        Language.objects.all().delete()
        with self.assertRaises(Exception) as context:
            LanguageHelper.get_current()
        self.assertTrue("No languages have been registered." in str(context.exception))

    def test_get_current_no_language_found(self):
        # test no language found, should fallback to english
        activate("fr-FR")
        language = LanguageHelper.get_current()
        self.assertEqual(language, self.language_en)

    @patch("apps.language.helpers.get_language")
    def test_get_current_partial_match_with_dash(self, mock_get_language):
        # test partial match with mocked language code
        mock_get_language.return_value = "xx"
        language = LanguageHelper.get_current()
        self.assertEqual(language, self.language_en)
