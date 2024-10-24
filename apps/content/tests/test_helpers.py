from django.test import TestCase
from django.utils.translation import activate, deactivate

from apps.content.helpers import ContentHelper
from apps.content.models import Content
from apps.language.models import Language


class ContentHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # load languages from the fixture
        self.language_en = Language.objects.get(code_iso_language="en-us")
        self.language_pt = Language.objects.get(code_iso_language="pt-br")
        self.language_es = Language.objects.get(code_iso_language="es-es")

        # create test content for en-us, pt-br, and es-es
        self.content_en = Content.objects.create(
            title="English Content",
            language=self.language_en,
            tag="test-content",
            content="<p>Content in English</p>",
            active=True,
        )

        self.content_pt = Content.objects.create(
            title="Portuguese Content",
            language=self.language_pt,
            tag="test-content",
            content="<p>Conteúdo em português</p>",
            active=True,
        )

        self.content_es = Content.objects.create(
            title="Spanish Content",
            language=self.language_es,
            tag="test-content",
            content="<p>Contenido en español</p>",
            active=True,
        )

        # create content that is available for all languages (language=None)
        self.content_global = Content.objects.create(
            title="Global Content",
            language=None,
            tag="global-content",
            content="<p>Global content for all languages</p>",
            active=True,
        )

    def tearDown(self):
        # deactivate translation after each test to prevent influence on other tests
        deactivate()

    def test_get_content_by_id_ignores_language(self):
        # activate Portuguese (pt-BR) language
        activate("pt-BR")

        # test fetching content by id should ignore the language
        content = ContentHelper.get_content(content_id=self.content_en.id)
        self.assertEqual(content, self.content_en)
        self.assertEqual(content.content, "<p>Content in English</p>")

    def test_get_content_in_user_language(self):
        # activate Portuguese (pt-BR) language
        activate("pt-BR")

        # test fetching content in the user's language (portuguese in this case)
        content = ContentHelper.get_content(content_tag="test-content")
        self.assertEqual(content, self.content_pt)
        self.assertEqual(content.content, "<p>Conteúdo em português</p>")

    def test_fallback_to_en_us_if_user_language_not_found(self):
        # activate a language not available (fr)
        activate("fr")

        # test fallback to en-us when the user's language is not available (french in this case)
        content = ContentHelper.get_content(content_tag="test-content")
        self.assertEqual(content, self.content_en)
        self.assertEqual(content.content, "<p>Content in English</p>")

    def test_fallback_to_global_content_if_no_language_match(self):
        # test fallback to global content (language=None) when no specific language matches
        activate("fr")

        content = ContentHelper.get_content(content_tag="global-content")
        self.assertEqual(content, self.content_global)
        self.assertEqual(content.content, "<p>Global content for all languages</p>")

    def test_fallback_to_any_language_if_no_en_us_or_user_language(self):
        # deactivate en-us content to trigger fallback to first available language (portuguese in this case)
        self.content_en.active = False
        self.content_en.save()

        # activate an unavailable language
        activate("fr")

        content = ContentHelper.get_content(content_tag="test-content")
        self.assertEqual(content, self.content_pt)
        self.assertEqual(content.content, "<p>Conteúdo em português</p>")

    def test_no_content_found(self):
        # deactivate all content to trigger no content found case
        self.content_en.active = False
        self.content_en.save()
        self.content_pt.active = False
        self.content_pt.save()
        self.content_es.active = False
        self.content_es.save()

        content = ContentHelper.get_content(content_tag="non-existing-tag")
        self.assertIsNone(content)

    def test_get_content_by_tag_not_found(self):
        # test case when content by tag is not found
        content = ContentHelper.get_content(content_tag="non-existing-tag")
        self.assertIsNone(content)

    def test_invalid_parameters_raise_error(self):
        # test raising ValueError when neither content_id nor content_tag is provided
        with self.assertRaises(ValueError):
            ContentHelper.get_content()
