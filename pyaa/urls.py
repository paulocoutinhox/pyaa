"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

from apps.web.urls import urlpatterns as web_urlpatterns

from . import views
from .apis import api

urlpatterns = [
    path(
        "api/",
        api.urls,
    ),
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "upload-image/",
        views.upload_image,
        name="upload-image",
    ),
    path(
        "tinymce/",
        include("tinymce.urls"),
    ),
    path(
        "i18n/",
        include("django_translation_flags.urls"),
    ),
    re_path(
        r"^app/(?P<path>.*)$",
        views.serve_app_files,
    ),
]

urlpatterns += web_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
