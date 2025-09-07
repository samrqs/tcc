from django.urls import reverse
from rest_framework.test import APITestCase


class ChatbotWebhookTest(APITestCase):
    def test_chatbot_webhook(self):
        url = reverse("chatbot-webhook")
        payload = {
            "user_id": "u1",
            "message": "oi",
            "timestamp": "2025-09-05T10:00:00Z",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
