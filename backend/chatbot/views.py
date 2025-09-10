import json
import logging

from decouple import config
from django.http import JsonResponse
from openai import OpenAI
from rest_framework import status
from rest_framework.views import APIView

from .evolution_api import send_whatsapp_message

logger = logging.getLogger(__name__)

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def get_chat_response(message):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Você é um chatbot voltado para micro agricultadores.",
            },
            {"role": "user", "content": message},
        ],
    )

    return completion.choices[0].message.content


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

            response = get_chat_response(message)
            send_whatsapp_message(
                sender_number,
                response,
            )
            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar a mensagem: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
