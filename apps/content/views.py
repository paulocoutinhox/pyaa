from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics

from apps.content.helpers import ContentHelper
from apps.content.serializers import ContentSerializer


class ContentByTag(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContentSerializer

    def get(self, request, tag):
        content = ContentHelper.get_content(content_tag=tag)

        if content:
            serializer = self.get_serializer(content)
            return Response(serializer.data)

        return Response({"detail": "Not found."}, status=404)
