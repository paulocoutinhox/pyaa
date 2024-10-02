from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import path

from apps.gallery.models import Gallery


def gallery_index_view(request):
    gallery_list = Gallery.objects.filter(active=True)

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
    try:
        gallery = Gallery.objects.prefetch_related("gallery_photos").get(
            id=gallery_id, active=True
        )
    except Gallery.DoesNotExist:
        return redirect("home")

    return render(
        request,
        "pages/gallery/view.html",
        {
            "gallery": gallery,
        },
    )


def gallery_by_tag_view(request, gallery_tag):
    try:
        gallery = Gallery.objects.prefetch_related("gallery_photos").get(
            tag=gallery_tag, active=True
        )
    except Gallery.DoesNotExist:
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
