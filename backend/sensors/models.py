from django.db import models
from django.conf import settings

class SensorData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sensor_data"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    umidade = models.FloatField()
    condutividade = models.FloatField()
    temperatura = models.FloatField()
    ph = models.FloatField()
    nitrogenio = models.FloatField()
    fosforo = models.FloatField()
    potassio = models.FloatField()
    salinidade = models.FloatField()
    tds = models.FloatField()

    def __str__(self):
        return f"SensorData {self.id} - {self.user.email}"
