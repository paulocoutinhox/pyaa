from django.shortcuts import redirect, render
from django.urls import path

from apps.content.models import Content


def content_by_id_view(request, content_id):
    try:
        content = Content.objects.get(id=content_id, active=True)
    except Content.DoesNotExist:
        return redirect("home")

    return render(
        request,
        "pages/content/view.html",
        {
            "content": content,
        },
    )


def content_by_tag_view(request, content_tag):
    try:
        content = Content.objects.get(tag=content_tag, active=True)
    except Content.DoesNotExist:
        return redirect("home")

    return render(
        request,
        "pages/content/view.html",
        {
            "content": content,
        },
    )


urlpatterns = [
    path("c/i/<int:content_id>/", content_by_id_view, name="content_by_id"),
    path("c/t/<slug:content_tag>/", content_by_tag_view, name="content_by_tag"),
]
