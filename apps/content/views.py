from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.helpers import ContentHelper
from apps.content.serializers import ContentSerializer


class ContentByTag(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tag):
        content = ContentHelper.get_content(content_tag=tag)

        if content:
            serializer = ContentSerializer(content)
            return Response(serializer.data)

        return Response({"detail": "Not found."}, status=404)
