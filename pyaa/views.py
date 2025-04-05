import os
import pathlib

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from pyaa.helpers.file import FileHelper


@csrf_exempt
def upload_image(request):
    # validate request
    if request.method == "POST":
        # file object
        file_obj = request.FILES["file"]

        # check extension
        file_name_suffix = pathlib.Path(file_obj.name).suffix

        if file_name_suffix not in [
            ".jpg",
            ".png",
            ".gif",
            ".jpeg",
            ".webp",
        ]:
            return JsonResponse({"message": _("error.upload-image.invalid-format")})

        # create file name and path
        file_name = FileHelper.generate_filename(file_obj)
        upload_time = timezone.now()
        path = f"{settings.UPLOAD_PATH}/{upload_time.year}/{upload_time.month}/{upload_time.day}"

        # full file path with name
        file_path = f"{path}/{file_name}"

        # check if file exists
        if default_storage.exists(file_path):
            file_url = default_storage.url(file_path)
            return JsonResponse(
                {"message": _("error.upload-image.file-exists"), "location": file_url}
            )

        # save file using default storage
        file_path_saved = default_storage.save(file_path, ContentFile(file_obj.read()))
        file_url = default_storage.url(file_path_saved)

        # return success
        return JsonResponse(
            {"message": _("error.upload-image.success"), "location": file_url}
        )

    # return generic request error
    return JsonResponse({"message": _("error.upload-image.invalid-request")})


def serve_app_files(request, path):
    file_path = os.path.join(settings.BASE_DIR, "static", "app", path)

    if os.path.isdir(file_path):
        file_path = os.path.join(file_path, "index.html")
        path = os.path.join(path, "index.html")

    return serve(
        request,
        path,
        document_root=os.path.join(settings.BASE_DIR, "static", "app"),
    )
