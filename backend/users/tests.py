import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_can_register_and_login():
    client = APIClient()

    # 1) Register
    url_register = reverse("user-register")
    payload = {
        "email": "teste@example.com",
        "name": "Samara",
        "password": "senha12345"
    }
    resp = client.post(url_register, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["email"] == "teste@example.com"
    assert User.objects.count() == 1

    # 2) Login (token)
    url_login = reverse("token_obtain_pair")
    login_payload = {
        "email": "teste@example.com",
        "password": "senha12345"
    }
    resp_login = client.post(url_login, login_payload, format="json")

    assert resp_login.status_code == 200
    assert "access" in resp_login.data
    assert "refresh" in resp_login.data
