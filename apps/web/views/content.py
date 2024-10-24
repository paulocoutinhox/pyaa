from django.shortcuts import redirect, render
from django.urls import path

from apps.content.helpers import ContentHelper


def content_by_id_view(request, content_id):
    content = ContentHelper.get_content(content_id=content_id)

    if not content:
        return redirect("home")

    return render(
        request,
        "pages/content/view.html",
        {
            "content": content,
        },
    )


def content_by_tag_view(request, content_tag):
    content = ContentHelper.get_content(content_tag=content_tag)

    if not content:
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
