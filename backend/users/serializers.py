import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name", "phone")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Senha deve ter pelo menos 8 caracteres",
    )
    name = serializers.CharField(max_length=150, help_text="Nome completo do usuário")
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Número de telefone/celular - apenas números, 10-20 dígitos (opcional, mas único se preenchido)",
    )

    class Meta:
        model = User
        fields = ("email", "name", "phone", "password")

    def validate_phone(self, value):
        """Valida o formato do telefone - apenas números"""
        if not value:
            return value

        # Remove espaços e caracteres especiais, mantendo apenas números
        cleaned_phone = re.sub(r"[^\d]", "", value)

        # Verifica se tem apenas números
        if not cleaned_phone.isdigit():
            raise serializers.ValidationError("Telefone deve conter apenas números")

        # Verifica se tem pelo menos 10 dígitos (formato brasileiro)
        if len(cleaned_phone) < 10:
            raise serializers.ValidationError("Telefone deve ter pelo menos 10 dígitos")

        # Verifica se não excede 20 dígitos
        if len(cleaned_phone) > 20:
            raise serializers.ValidationError("Telefone deve ter no máximo 20 dígitos")

        # Verifica se o telefone já está em uso
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if User.objects.filter(phone=cleaned_phone).exists():
            raise serializers.ValidationError("Este telefone já está cadastrado")

        return cleaned_phone

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
