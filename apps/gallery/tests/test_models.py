from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from apps.gallery.models import Gallery, GalleryPhoto
from apps.language.models import Language


class GalleryModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_gallery_creation(self):
        language = Language.objects.get(code_iso_language="en-US")

        Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        self.assertTrue(Gallery.objects.filter(title="Test Gallery").exists())

    def test_gallery_deletion(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        gallery.delete()

        self.assertFalse(Gallery.objects.filter(title="Test Gallery").exists())

    def test_get_gallery(self):
        language = Language.objects.get(code_iso_language="en-US")

        Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        fetched_gallery = Gallery.objects.get(title="Test Gallery")

        self.assertEqual(fetched_gallery.title, "Test Gallery")

    def test_get_nonexistent_gallery(self):
        with self.assertRaises(ObjectDoesNotExist):
            Gallery.objects.get(title="Nonexistent Gallery")

    def test_gallery_str(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        self.assertEqual(str(gallery), "Test Gallery")

    def test_get_main_photo_url(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        self.assertEqual(
            gallery.get_main_photo_url(), "/media/extras/images/python.png"
        )

    def test_get_main_photo_url_no_main_photo(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        self.assertEqual(gallery.get_main_photo_url(), "/static/images/no-image.png")

    def test_gallery_tag_creation(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            active=True,
        )

        self.assertEqual(gallery.tag, "test-gallery")


class GalleryPhotoModelTest(TestCase):
    fixtures = ["apps/language/fixtures/initial.json"]

    def test_gallery_photo_creation(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        self.assertTrue(GalleryPhoto.objects.filter(gallery=gallery).exists())

    def test_gallery_photo_deletion(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        photo = GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        photo.delete()

        self.assertFalse(GalleryPhoto.objects.filter(gallery=gallery).exists())

    def test_get_gallery_photo(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        fetched_photo = GalleryPhoto.objects.get(gallery=gallery)

        self.assertEqual(fetched_photo.caption, "Test Caption")

    def test_get_nonexistent_gallery_photo(self):
        with self.assertRaises(ObjectDoesNotExist):
            GalleryPhoto.objects.get(caption="Nonexistent Caption")

    def test_gallery_photo_str(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        photo = GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        self.assertEqual(str(photo), "Test Caption")

    def test_preview(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        photo = GalleryPhoto.objects.create(
            gallery=gallery,
            image="extras/images/python.png",
            caption="Test Caption",
            main=True,
        )

        self.assertIn('href="/media/extras/images/python.png', photo.preview())

    def test_preview_no_image(self):
        language = Language.objects.get(code_iso_language="en-US")

        gallery = Gallery.objects.create(
            title="Test Gallery",
            language=language,
            tag="test-gallery",
            active=True,
        )

        photo = GalleryPhoto.objects.create(
            gallery=gallery,
            caption="Test Caption",
            main=True,
        )

        self.assertEqual(photo.preview(), "")
