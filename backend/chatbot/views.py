from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ChatbotWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
