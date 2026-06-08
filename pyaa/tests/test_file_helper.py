from unittest.mock import Mock

from django.test import TestCase

from pyaa.helpers.file import FileHelper


class FileHelperTest(TestCase):
    def test_generate_filename_keeps_lowercase_extension(self):
        file_obj = Mock()
        file_obj.name = "Photo.JPG"

        filename = FileHelper.generate_filename(file_obj)

        self.assertTrue(filename.endswith(".jpg"))

    def test_generate_filename_uses_uuid_name(self):
        file_obj = Mock()
        file_obj.name = "document.pdf"

        first = FileHelper.generate_filename(file_obj)
        second = FileHelper.generate_filename(file_obj)

        self.assertNotEqual(first, second)
        self.assertTrue(first.endswith(".pdf"))

    def test_generate_filename_without_extension(self):
        file_obj = Mock()
        file_obj.name = "noext"

        filename = FileHelper.generate_filename(file_obj)

        self.assertNotIn(".", filename)
