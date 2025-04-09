from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery
from apps.gallery.serializers import GalleryListSerializer, GallerySerializer


class GalleryList(generics.ListCreateAPIView):
    queryset = Gallery.objects.filter(active=True).order_by("-published_at").all()
    serializer_class = GalleryListSerializer
    permission_classes = [AllowAny]


class GalleryByTag(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GallerySerializer

    def get(self, request, tag):
        gallery = GalleryHelper.get_gallery(gallery_tag=tag)

        if gallery:
            serializer = self.get_serializer(gallery, context={"request": request})
            return Response(serializer.data)

        return Response({"detail": "Not found."}, status=404)
