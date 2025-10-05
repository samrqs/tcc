from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        credentials = {"email": attrs.get("email"), "password": attrs.get("password")}
        user = authenticate(**credentials)
        if user is None:
            raise serializers.ValidationError("Credenciais inválidas")
        if not user.is_active:
            raise serializers.ValidationError("Conta inativa")
        data = super().validate(attrs)
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "name": getattr(user, "name", ""),
            "phone": getattr(user, "phone", None),
        }
        return data
