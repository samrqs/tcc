import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .message_buffer import buffer_message

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ChatbotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)

            data = payload.get("data")
            message = data.get("message").get("conversation")
            chat_id = data.get("key").get("remoteJid")
            is_group = "@g.us" in chat_id

            if is_group:
                return JsonResponse(
                    {"status": "success", "message": "Mensagem de grupo ignorada."},
                    status=status.HTTP_201_CREATED,
                )

            await buffer_message(
                chat_id=chat_id,
                message=message,
            )

            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar a mensagem: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
