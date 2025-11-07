from rest_framework import serializers

from .models import CropAlert, SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = [
            "id",
            "timestamp",
            "umidade",
            "condutividade",
            "temperatura",
            "ph",
            "nitrogenio",
            "fosforo",
            "potassio",
            "salinidade",
            "tds",
        ]
        read_only_fields = ["id", "timestamp"]


class CropAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropAlert
        fields = [
            "id",
            "cultivo",
            "area",
            "data_plantio",
            "umidade_min",
            "umidade_ideal",
            "umidade_max",
            "temperatura_min",
            "temperatura_ideal",
            "temperatura_max",
            "ph_min",
            "ph_ideal",
            "ph_max",
            "nitrogenio_min",
            "nitrogenio_ideal",
            "nitrogenio_max",
            "fosforo_min",
            "fosforo_ideal",
            "fosforo_max",
            "potassio_min",
            "potassio_ideal",
            "potassio_max",
            "condutividade_min",
            "condutividade_ideal",
            "condutividade_max",
            "salinidade_min",
            "salinidade_ideal",
            "salinidade_max",
            "tds_min",
            "tds_ideal",
            "tds_max",
            "alertas_ativos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
