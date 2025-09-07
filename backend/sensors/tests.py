from django.urls import reverse
from rest_framework.test import APITestCase


class SensorWebhookTest(APITestCase):
    def test_sensor_webhook(self):
        url = reverse("sensor-webhook")
        payload = {
            "sensor_id": "s1",
            "value": 42.0,
            "timestamp": "2025-09-05T10:00:00Z",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
