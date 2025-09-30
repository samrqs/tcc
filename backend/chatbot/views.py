import json
import logging
import time

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .message_buffer import buffer_message
from .metrics import track_error, track_message_processed, track_response_time

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ChatbotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        start_time = time.time()
        phone_number = None

        try:
            payload = json.loads(request.body)

            data = payload.get("data")
            message = data.get("message").get("conversation")
            chat_id = data.get("key").get("remoteJid")
            phone_number = chat_id.split("@")[0] if "@" in chat_id else chat_id
            is_group = "@g.us" in chat_id

            if is_group:
                track_message_processed(phone_number, "group_ignored")
                return JsonResponse(
                    {"status": "success", "message": "Mensagem de grupo ignorada."},
                    status=status.HTTP_201_CREATED,
                )

            # Track message received
            track_message_processed(phone_number, "text")

            await buffer_message(
                chat_id=chat_id,
                message=message,
            )

            # Track response time
            response_time = time.time() - start_time
            track_response_time(phone_number, response_time)

            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Track error
            track_error("webhook_error", "views")
            logger.error(f"Erro ao processar a mensagem: {str(e)}")

            # Track response time even on error
            if phone_number:
                response_time = time.time() - start_time
                track_response_time(phone_number, response_time)

            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
