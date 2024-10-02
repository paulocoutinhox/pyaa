import os
import uuid
from unittest.mock import Mock

from django.test import TestCase

from apps.gallery.fields import GalleryPhotoImageField


class GalleryFieldTest(TestCase):
    def setUp(self):
        self.field = GalleryPhotoImageField(size=[1024, 1024])

    def test_generate_filename(self):
        instance = Mock()
        filename = "test_image.jpg"
        generated_filename = self.field.generate_filename(instance, filename)

        # check if the generated filename has the correct extension
        _, ext = os.path.splitext(filename)
        self.assertTrue(generated_filename.endswith(ext))

        # check if the generated filename is a uuid
        name = os.path.splitext(generated_filename)[0]

        try:
            uuid_obj = uuid.UUID(name, version=4)
        except ValueError:
            uuid_obj = None
        self.assertIsNotNone(uuid_obj)
