from rest_framework import generics

from apps.gallery.models import Gallery
from apps.gallery.serializers import GallerySerializer
from pyaa.helpers.rest import AppModelPermissions


class GalleryList(generics.ListCreateAPIView):
    queryset = Gallery.objects.order_by("-id").all()
    serializer_class = GallerySerializer
    permission_classes = [AppModelPermissions]

    list_display = ["id", "title"]
