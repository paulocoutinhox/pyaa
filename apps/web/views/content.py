from django.shortcuts import redirect, render
from django.urls import path

from apps.content.helpers import ContentHelper
from apps.content.models import ContentCategory
from pyaa.utils.cached_paginator import Paginator


def contents_index_view(request, category_tag):
    category = ContentCategory.objects.filter(tag=category_tag).first()

    if not category:
        return redirect("home")

    contents = category.contents.filter(active=True).order_by("-published_at")

    paginator = Paginator(
        contents,
        9,
        cache_key=f"contents-{category_tag}",
    )

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/content/index.html",
        {
            "page_obj": page_obj,
            "category": category,
        },
    )


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
    path(
        "c/<slug:category_tag>/",
        contents_index_view,
        name="contents_index_view",
    ),
    path(
        "c/i/<int:content_id>/",
        content_by_id_view,
        name="content_by_id",
    ),
    path(
        "c/t/<slug:content_tag>/",
        content_by_tag_view,
        name="content_by_tag",
    ),
]
