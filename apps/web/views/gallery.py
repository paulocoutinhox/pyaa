from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import path

from apps.gallery.helpers import GalleryHelper


def gallery_index_view(request):
    gallery_list = GalleryHelper.get_gallery_list()

    paginator = Paginator(gallery_list, 9)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/gallery/index.html",
        {
            "page_obj": page_obj,
        },
    )


def gallery_by_id_view(request, gallery_id):
    gallery = GalleryHelper.get_gallery(gallery_id=gallery_id)

    if not gallery:
        return redirect("home")

    return render(
        request,
        "pages/gallery/view.html",
        {
            "gallery": gallery,
        },
    )


def gallery_by_tag_view(request, gallery_tag):
    gallery = GalleryHelper.get_gallery(gallery_tag=gallery_tag)

    if not gallery:
        return redirect("home")

    return render(
        request,
        "pages/gallery/view.html",
        {
            "gallery": gallery,
        },
    )


urlpatterns = [
    path("gallery/", gallery_index_view, name="gallery_index"),
    path("gallery/i/<int:gallery_id>/", gallery_by_id_view, name="gallery_by_id"),
    path("gallery/t/<slug:gallery_tag>/", gallery_by_tag_view, name="gallery_by_tag"),
]
