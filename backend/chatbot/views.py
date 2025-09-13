import json
import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from .chains import get_conversational_rag_chain
from .evolution_api import send_whatsapp_message

logger = logging.getLogger(__name__)


class ChatbotWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            data = payload.get("data")
            message = data.get("message").get("conversation")
            chat_id = data.get("key").get("remoteJid")
            sender_number = chat_id.split("@")[0]
            is_group = "@g.us" in chat_id

            if is_group:
                return JsonResponse(
                    {"status": "success", "message": "Mensagem de grupo ignorada."},
                    status=status.HTTP_201_CREATED,
                )

            conversational_rag_chain = get_conversational_rag_chain()

            ai_response = conversational_rag_chain.invoke(
                input={"input": message},
                config={"configurable": {"session_id": chat_id}},
            )["answer"]

            send_whatsapp_message(
                sender_number,
                ai_response,
            )
            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar a mensagem: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
