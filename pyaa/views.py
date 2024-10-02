import os
import pathlib

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
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
            return JsonResponse({"message": "Wrong file format"})

        # create file name and path
        file_name = FileHelper.generate_filename(file_obj)
        upload_time = timezone.now()
        path = os.path.join(
            settings.MEDIA_ROOT,
            settings.UPLOAD_PATH,
            str(upload_time.year),
            str(upload_time.month),
            str(upload_time.day),
        )

        # if there is no such path, create
        if not os.path.exists(path):
            os.makedirs(path)

        # create final paths
        file_path = os.path.join(path, file_name)
        file_url = f"{settings.MEDIA_URL}{settings.UPLOAD_PATH}/{upload_time.year}/{upload_time.month}/{upload_time.day}/{file_name}"

        # check if file exists
        if os.path.exists(file_path):
            return JsonResponse({"message": "File already exist", "location": file_url})

        # write file contents
        with open(file_path, "wb+") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        # return success
        return JsonResponse(
            {"message": "Image uploaded successfully", "location": file_url}
        )

    # return generic request error
    return JsonResponse({"detail": "Wrong request"})


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
