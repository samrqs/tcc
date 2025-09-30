from django.urls import reverse

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from sensors.models import SensorData


@pytest.mark.django_db
def test_sensor_webhook_with_jwt():
    client = APIClient()

    # 1) Create user
    user = User.objects.create_user(
        email="sensor@example.com",
        password="StrongPass123",
        name="Sensor User"
    )

    # 2) Obtain token JWT
    url_token = reverse("token_obtain_pair")
    response = client.post(url_token, {
        "email": "sensor@example.com",
        "password": "StrongPass123"
    }, format="json")
    assert response.status_code == 200
    access_token = response.data["access"]

    # 3) Send sensor data
    url_webhook = reverse("sensor-webhook")
    payload = {
        "umidade": 55.2,
        "condutividade": 1.2,
        "temperatura": 24.7,
        "ph": 6.5,
        "nitrogenio": 10.5,
        "fosforo": 3.4,
        "potassio": 7.8,
        "salinidade": 0.6,
        "tds": 450.0
    }

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = client.post(url_webhook, payload, format="json")

    assert response.status_code == 201
    assert response.data["umidade"] == 55.2
    assert SensorData.objects.count() == 1

    sensor_data = SensorData.objects.first()
    assert sensor_data.user == user
    assert sensor_data.temperatura == 24.7