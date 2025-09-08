import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("webhook")


class ChatbotWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        logger.info(f"Payload recebido: {payload}")
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
