from rest_framework import serializers
from .models import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = [
            "id", "timestamp", "umidade", "condutividade", "temperatura", "ph",
            "nitrogenio", "fosforo", "potassio", "salinidade", "tds"
        ]
        read_only_fields = ["id", "timestamp"]
