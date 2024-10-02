from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Content
from apps.content.serializers import ContentSerializer


class ContentByTag(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tag):
        try:
            content = Content.objects.get(tag=tag, active=True)
            serializer = ContentSerializer(content)
            return Response(serializer.data)
        except Content.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
