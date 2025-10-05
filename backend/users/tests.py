import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_user_can_register_and_login():
    client = APIClient()

    # 1) Register
    url_register = reverse("user-register")
    payload = {
        "email": "teste@example.com",
        "name": "Samara",
        "phone": "5511999887766",
        "password": "senha12345",
    }
    resp = client.post(url_register, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["email"] == "teste@example.com"
    assert resp.data["name"] == "Samara"
    assert resp.data["phone"] == "5511999887766"
    assert User.objects.count() == 1

    # 2) Login (token)
    url_login = reverse("token_obtain_pair")
    login_payload = {"email": "teste@example.com", "password": "senha12345"}
    resp_login = client.post(url_login, login_payload, format="json")

    assert resp_login.status_code == 200
    assert "access" in resp_login.data
    assert "refresh" in resp_login.data


@pytest.mark.django_db
def test_user_register_without_phone():
    """Teste registro sem telefone (campo opcional)"""
    client = APIClient()
    url_register = reverse("user-register")

    payload = {
        "email": "sem_telefone@example.com",
        "name": "João Silva",
        "password": "senha12345",
    }

    resp = client.post(url_register, payload, format="json")
    assert resp.status_code == 201
    assert resp.data["phone"] is None


@pytest.mark.django_db
def test_phone_unique_constraint():
    """Teste que garante que telefones são únicos"""
    client = APIClient()
    url_register = reverse("user-register")

    # Primeiro usuário
    payload1 = {
        "email": "user1@example.com",
        "name": "Usuário 1",
        "phone": "55119999887766",
        "password": "senha12345",
    }
    resp1 = client.post(url_register, payload1, format="json")
    assert resp1.status_code == 201

    # Segundo usuário com mesmo telefone
    payload2 = {
        "email": "user2@example.com",
        "name": "Usuário 2",
        "phone": "55119999887766",  # Mesmo telefone
        "password": "senha12345",
    }
    resp2 = client.post(url_register, payload2, format="json")
    assert resp2.status_code == 400
    assert "phone" in resp2.data


@pytest.mark.django_db
def test_phone_validation():
    """Teste validação de formato do telefone"""
    client = APIClient()
    url_register = reverse("user-register")

    payload = {
        "email": "telefone_invalido@example.com",
        "name": "Teste Telefone",
        "phone": "123",  # Telefone muito curto
        "password": "senha12345",
    }

    resp = client.post(url_register, payload, format="json")
    assert resp.status_code == 400
    assert "phone" in resp.data


@pytest.mark.django_db
def test_phone_validation_no_symbols():
    """Teste que telefone não aceita símbolos como +"""
    client = APIClient()
    url_register = reverse("user-register")

    payload = {
        "email": "telefone_simbolo@example.com",
        "name": "Teste Símbolo",
        "phone": "+5511999887766",  # Com símbolo +
        "password": "senha12345",
    }

    resp = client.post(url_register, payload, format="json")
    # Deve aceitar e limpar automaticamente, removendo o +
    assert resp.status_code == 201
    assert resp.data["phone"] == "5511999887766"  # Sem o +


@pytest.mark.django_db
def test_phone_validation_max_length():
    """Teste que telefone não aceita mais de 20 dígitos"""
    client = APIClient()
    url_register = reverse("user-register")

    payload = {
        "email": "telefone_longo@example.com",
        "name": "Teste Longo",
        "phone": "123456789012345678901",  # 21 dígitos
        "password": "senha12345",
    }

    resp = client.post(url_register, payload, format="json")
    assert resp.status_code == 400
    assert "phone" in resp.data
