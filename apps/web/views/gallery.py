from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import path

from apps.gallery.models import Gallery


def gallery_home(request):
    gallery_list = Gallery.objects.filter(active=True)

    paginator = Paginator(gallery_list, 9)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/gallery/home.html",
        {
            "page_obj": page_obj,
        },
    )


def gallery_by_id_view(request, gallery_id):
    try:
        gallery = Gallery.objects.get(id=gallery_id, active=True)
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
        gallery = Gallery.objects.get(tag=gallery_tag, active=True)
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
    path("gallery/", gallery_home, name="gallery_home"),
    path("g/i/<int:gallery>/", gallery_by_id_view, name="gallery_by_id"),
    path("g/t/<slug:gallery>/", gallery_by_tag_view, name="gallery_by_tag"),
]
