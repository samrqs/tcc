import json
import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

logger = logging.getLogger("chatbot")


class ChatbotWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            data = payload.get("data")
            message = data.get("message").get("conversation")
            chat_id = data.get("key").get("remoteJid")
            sender_number = chat_id.split("@")[0]
            is_group = chat_id and "@g.us" in chat_id

            if is_group:
                return JsonResponse(
                    {"status": "success", "message": "Mensagem de grupo ignorada."},
                    status=status.HTTP_201_CREATED,
                )

            logger.info(f"Chat ID: {chat_id}")
            logger.info(f"Mensagem privada recebida: {message}")
            logger.info(f"Payload recebido: {data}")
            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar a mensagem: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
