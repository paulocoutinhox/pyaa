import json
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.utils.translation import gettext as _
from PIL import Image

from pyaa.views import serve_app_files, upload_image

User = get_user_model()


def make_png_bytes():
    buffer = BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, format="PNG")
    return buffer.getvalue()


class UploadImageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff = User.objects.create_user(
            email="staff@example.com", password="StrongPass123", is_staff=True
        )

    def _post(self, file_obj):
        request = self.factory.post("/upload", {"file": file_obj})
        request.user = self.staff
        return request

    def _body(self, response):
        return json.loads(response.content)

    def test_anonymous_user_is_forbidden(self):
        upload = SimpleUploadedFile("photo.png", make_png_bytes())
        request = self.factory.post("/upload", {"file": upload})
        request.user = AnonymousUser()

        response = upload_image(request)

        self.assertEqual(response.status_code, 403)

    def test_non_staff_user_is_forbidden(self):
        user = User.objects.create_user(
            email="member@example.com", password="StrongPass123"
        )
        upload = SimpleUploadedFile("photo.png", make_png_bytes())
        request = self.factory.post("/upload", {"file": upload})
        request.user = user

        response = upload_image(request)

        self.assertEqual(response.status_code, 403)

    def test_get_request_returns_invalid_request(self):
        request = self.factory.get("/upload")
        request.user = self.staff
        response = upload_image(request)

        self.assertEqual(
            self._body(response)["message"],
            _("error.upload-image.invalid-request"),
        )

    def test_invalid_extension_is_rejected(self):
        upload = SimpleUploadedFile("file.txt", b"data", content_type="text/plain")
        response = upload_image(self._post(upload))

        self.assertEqual(
            self._body(response)["message"],
            _("error.upload-image.invalid-format"),
        )

    def test_non_image_content_is_rejected(self):
        # a payload renamed with an image extension must fail content validation
        upload = SimpleUploadedFile(
            "photo.png", b"<html>not an image</html>", content_type="image/png"
        )
        response = upload_image(self._post(upload))

        self.assertEqual(
            self._body(response)["message"],
            _("error.upload-image.invalid-format"),
        )

    def test_valid_image_is_saved(self):
        upload = SimpleUploadedFile(
            "photo.png", make_png_bytes(), content_type="image/png"
        )

        with patch("pyaa.views.default_storage") as mock_storage, patch(
            "pyaa.views.FileHelper.generate_filename", return_value="generated.png"
        ):
            mock_storage.exists.return_value = False
            mock_storage.save.return_value = "saved/path/generated.png"
            mock_storage.url.return_value = "/media/saved/path/generated.png"

            response = upload_image(self._post(upload))

        body = self._body(response)
        self.assertEqual(body["message"], _("error.upload-image.success"))
        self.assertEqual(body["location"], "/media/saved/path/generated.png")
        mock_storage.save.assert_called_once()

    def test_existing_file_returns_file_exists(self):
        upload = SimpleUploadedFile(
            "photo.jpg", make_png_bytes(), content_type="image/jpeg"
        )

        with patch("pyaa.views.default_storage") as mock_storage, patch(
            "pyaa.views.FileHelper.generate_filename", return_value="generated.jpg"
        ):
            mock_storage.exists.return_value = True
            mock_storage.url.return_value = "/media/existing.jpg"

            response = upload_image(self._post(upload))

        body = self._body(response)
        self.assertEqual(body["message"], _("error.upload-image.file-exists"))
        self.assertEqual(body["location"], "/media/existing.jpg")
        mock_storage.save.assert_not_called()


class ServeAppFilesTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_serves_existing_file(self):
        request = self.factory.get("/app/index.html")
        response = serve_app_files(request, "index.html")

        self.assertEqual(response.status_code, 200)

    def test_directory_path_falls_back_to_index_html(self):
        request = self.factory.get("/app/")

        with patch("pyaa.views.os.path.isdir", return_value=True), patch(
            "pyaa.views.serve"
        ) as mock_serve:
            mock_serve.return_value = "served"
            result = serve_app_files(request, "subdir")

        # index.html should be appended to the path passed to serve
        called_path = mock_serve.call_args.args[1]
        self.assertTrue(called_path.endswith("index.html"))
        self.assertEqual(result, "served")
