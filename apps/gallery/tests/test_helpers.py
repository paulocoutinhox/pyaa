from django.test import TestCase
from django.utils.translation import activate, deactivate

from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery
from apps.language.models import Language


class GalleryHelperTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def setUp(self):
        # load languages from the fixture
        self.language_en = Language.objects.get(code_iso_language="en-us")
        self.language_pt = Language.objects.get(code_iso_language="pt-br")
        self.language_es = Language.objects.get(code_iso_language="es-es")

        # create test galleries for en-us, pt-br, and es-es
        self.gallery_en = Gallery.objects.create(
            title="English Gallery",
            language=self.language_en,
            tag="test-gallery",
            active=True,
        )

        self.gallery_pt = Gallery.objects.create(
            title="Portuguese Gallery",
            language=self.language_pt,
            tag="test-gallery",
            active=True,
        )

        self.gallery_es = Gallery.objects.create(
            title="Spanish Gallery",
            language=self.language_es,
            tag="test-gallery",
            active=True,
        )

        # create gallery that is available for all languages (language=None)
        self.gallery_global = Gallery.objects.create(
            title="Global Gallery",
            language=None,
            tag="global-gallery",
            active=True,
        )

    def tearDown(self):
        # deactivate translation after each test to prevent influence on other tests
        deactivate()

    def test_get_gallery_by_id_ignores_language(self):
        # activate Portuguese (pt-BR) language
        activate("pt-BR")

        # test fetching gallery by id should ignore the language
        gallery = GalleryHelper.get_gallery(gallery_id=self.gallery_en.id)
        self.assertEqual(gallery, self.gallery_en)
        self.assertEqual(gallery.title, "English Gallery")

    def test_get_gallery_in_user_language(self):
        # activate Portuguese (pt-BR) language
        activate("pt-BR")

        # test fetching gallery in the user's language (portuguese in this case)
        gallery = GalleryHelper.get_gallery(gallery_tag="test-gallery")
        self.assertEqual(gallery, self.gallery_pt)
        self.assertEqual(gallery.title, "Portuguese Gallery")

    def test_fallback_to_en_us_if_user_language_not_found(self):
        # activate a language not available (fr)
        activate("fr")

        # test fallback to en-us when the user's language is not available (french in this case)
        gallery = GalleryHelper.get_gallery(gallery_tag="test-gallery")
        self.assertEqual(gallery, self.gallery_en)
        self.assertEqual(gallery.title, "English Gallery")

    def test_fallback_to_global_gallery_if_no_language_match(self):
        # activate a language not available (fr)
        activate("fr")

        gallery = GalleryHelper.get_gallery(gallery_tag="global-gallery")
        self.assertEqual(gallery, self.gallery_global)
        self.assertEqual(gallery.title, "Global Gallery")

    def test_fallback_to_any_language_if_no_en_us_or_user_language(self):
        # deactivate en-us gallery to trigger fallback to first available language (portuguese in this case)
        self.gallery_en.active = False
        self.gallery_en.save()

        # activate an unavailable language
        activate("fr")

        # test fallback to any available language
        gallery = GalleryHelper.get_gallery(gallery_tag="test-gallery")
        self.assertEqual(gallery, self.gallery_pt)
        self.assertEqual(gallery.title, "Portuguese Gallery")

    def test_no_gallery_found(self):
        # deactivate all galleries to trigger no gallery found case
        self.gallery_en.active = False
        self.gallery_en.save()
        self.gallery_pt.active = False
        self.gallery_pt.save()
        self.gallery_es.active = False
        self.gallery_es.save()

        gallery = GalleryHelper.get_gallery(gallery_tag="non-existing-gallery")
        self.assertIsNone(gallery)

    def test_get_gallery_by_tag_not_found(self):
        # test case when gallery by tag is not found
        gallery = GalleryHelper.get_gallery(gallery_tag="non-existing-gallery")
        self.assertIsNone(gallery)

    def test_invalid_parameters_raise_error(self):
        # test raising ValueError when neither gallery_id nor gallery_tag is provided
        with self.assertRaises(ValueError):
            GalleryHelper.get_gallery()

    # Novos testes adicionados para verificar a lista de galerias por idioma do usuário ou None

    def test_get_gallery_list_in_user_language_or_none(self):
        # activate Portuguese (pt-BR) language
        activate("pt-BR")

        gallery_list = GalleryHelper.get_gallery_list()
        gallery_titles = [gallery.title for gallery in gallery_list]

        # ensure the list contains the Portuguese and Global galleries only
        self.assertIn("Portuguese Gallery", gallery_titles)
        self.assertIn("Global Gallery", gallery_titles)
        self.assertNotIn("English Gallery", gallery_titles)
        self.assertNotIn("Spanish Gallery", gallery_titles)

    def test_get_global_gallery_list_if_no_language_match(self):
        # activate a language not available (fr)
        activate("fr")

        gallery_list = GalleryHelper.get_gallery_list()
        gallery_titles = [gallery.title for gallery in gallery_list]

        # ensure the list contains only the global gallery
        self.assertIn("Global Gallery", gallery_titles)
        self.assertNotIn("Portuguese Gallery", gallery_titles)
        self.assertNotIn("English Gallery", gallery_titles)
        self.assertNotIn("Spanish Gallery", gallery_titles)
