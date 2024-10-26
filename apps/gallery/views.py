from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.gallery.helpers import GalleryHelper
from apps.gallery.models import Gallery
from apps.gallery.serializers import GalleryListSerializer, GallerySerializer


class GalleryList(generics.ListCreateAPIView):
    queryset = Gallery.objects.filter(active=True).order_by("-published_at").all()
    serializer_class = GalleryListSerializer
    permission_classes = [AllowAny]


class GalleryByTag(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tag):
        gallery = GalleryHelper.get_gallery(gallery_tag=tag)

        if gallery:
            serializer = GallerySerializer(gallery, context={"request": request})
            return Response(serializer.data)

        return Response({"detail": "Not found."}, status=404)
