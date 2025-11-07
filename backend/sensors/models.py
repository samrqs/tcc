from django.conf import settings
from django.db import models


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


class CropAlert(models.Model):
    """
    Configuração de plantio e limites de alertas para o agricultor.
    Define os valores de referência para cada parâmetro do sensor.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crop_alerts"
    )

    # Informações do cultivo
    cultivo = models.CharField(
        max_length=100, help_text="Nome do cultivo plantado (ex: Milho, Soja, Feijão)"
    )
    area = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Área ou talhão onde está plantado (opcional)",
    )
    data_plantio = models.DateField(
        blank=True, null=True, help_text="Data do plantio (opcional)"
    )

    # Limites de Umidade (%)
    umidade_min = models.FloatField(help_text="Umidade mínima ideal (%)")
    umidade_ideal = models.FloatField(
        help_text="Umidade ideal (%)", blank=True, null=True
    )
    umidade_max = models.FloatField(help_text="Umidade máxima ideal (%)")

    # Limites de Temperatura (°C)
    temperatura_min = models.FloatField(help_text="Temperatura mínima ideal (°C)")
    temperatura_ideal = models.FloatField(
        help_text="Temperatura ideal (°C)", blank=True, null=True
    )
    temperatura_max = models.FloatField(help_text="Temperatura máxima ideal (°C)")

    # Limites de pH
    ph_min = models.FloatField(help_text="pH mínimo ideal")
    ph_ideal = models.FloatField(help_text="pH ideal", blank=True, null=True)
    ph_max = models.FloatField(help_text="pH máximo ideal")

    # Limites de Nitrogênio (mg/kg)
    nitrogenio_min = models.FloatField(help_text="Nitrogênio mínimo ideal (mg/kg)")
    nitrogenio_ideal = models.FloatField(
        help_text="Nitrogênio ideal (mg/kg)", blank=True, null=True
    )
    nitrogenio_max = models.FloatField(help_text="Nitrogênio máximo ideal (mg/kg)")

    # Limites de Fósforo (mg/kg)
    fosforo_min = models.FloatField(help_text="Fósforo mínimo ideal (mg/kg)")
    fosforo_ideal = models.FloatField(
        help_text="Fósforo ideal (mg/kg)", blank=True, null=True
    )
    fosforo_max = models.FloatField(help_text="Fósforo máximo ideal (mg/kg)")

    # Limites de Potássio (mg/kg)
    potassio_min = models.FloatField(help_text="Potássio mínimo ideal (mg/kg)")
    potassio_ideal = models.FloatField(
        help_text="Potássio ideal (mg/kg)", blank=True, null=True
    )
    potassio_max = models.FloatField(help_text="Potássio máximo ideal (mg/kg)")

    # Limites de Condutividade (uS/cm)
    condutividade_min = models.FloatField(
        help_text="Condutividade mínima ideal (uS/cm)", blank=True, null=True
    )
    condutividade_ideal = models.FloatField(
        help_text="Condutividade ideal (uS/cm)", blank=True, null=True
    )
    condutividade_max = models.FloatField(
        help_text="Condutividade máxima ideal (uS/cm)", blank=True, null=True
    )

    # Limites de Salinidade (mg/L)
    salinidade_min = models.FloatField(
        help_text="Salinidade mínima ideal (mg/L)", blank=True, null=True
    )
    salinidade_ideal = models.FloatField(
        help_text="Salinidade ideal (mg/L)", blank=True, null=True
    )
    salinidade_max = models.FloatField(
        help_text="Salinidade máxima ideal (mg/L)", blank=True, null=True
    )

    # Limites de TDS (mg/L)
    tds_min = models.FloatField(
        help_text="TDS mínimo ideal (mg/L)", blank=True, null=True
    )
    tds_ideal = models.FloatField(help_text="TDS ideal (mg/L)", blank=True, null=True)
    tds_max = models.FloatField(
        help_text="TDS máximo ideal (mg/L)", blank=True, null=True
    )

    # Controle de alertas
    alertas_ativos = models.BooleanField(
        default=True, help_text="Se os alertas devem ser enviados via WhatsApp"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Alerta do Cultivo"
        verbose_name_plural = "Alertas do Cultivo"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.cultivo} - {self.user.email}"

    def check_limits(self, sensor_data):
        """
        Verifica se os valores do sensor estão dentro dos limites configurados.
        Retorna uma lista de alertas a serem enviados.
        """
        alertas = []

        # Verificar Umidade
        if sensor_data.umidade < self.umidade_min:
            alertas.append(
                f"🚨 UMIDADE BAIXA: {sensor_data.umidade:.1f}% (mínimo ideal: {self.umidade_min:.1f}%)"
            )
        elif sensor_data.umidade > self.umidade_max:
            alertas.append(
                f"🚨 UMIDADE ALTA: {sensor_data.umidade:.1f}% (máximo ideal: {self.umidade_max:.1f}%)"
            )

        # Verificar Temperatura
        if sensor_data.temperatura < self.temperatura_min:
            alertas.append(
                f"🌡️ TEMPERATURA BAIXA: {sensor_data.temperatura:.1f}°C (mínimo ideal: {self.temperatura_min:.1f}°C)"
            )
        elif sensor_data.temperatura > self.temperatura_max:
            alertas.append(
                f"🌡️ TEMPERATURA ALTA: {sensor_data.temperatura:.1f}°C (máximo ideal: {self.temperatura_max:.1f}°C)"
            )

        # Verificar pH
        if sensor_data.ph < self.ph_min:
            alertas.append(
                f"⚗️ pH BAIXO: {sensor_data.ph:.1f} (mínimo ideal: {self.ph_min:.1f})"
            )
        elif sensor_data.ph > self.ph_max:
            alertas.append(
                f"⚗️ pH ALTO: {sensor_data.ph:.1f} (máximo ideal: {self.ph_max:.1f})"
            )

        # Verificar Nitrogênio
        if sensor_data.nitrogenio < self.nitrogenio_min:
            alertas.append(
                f"🌾 NITROGÊNIO BAIXO: {sensor_data.nitrogenio:.0f} mg/kg (mínimo ideal: {self.nitrogenio_min:.0f} mg/kg)"
            )
        elif sensor_data.nitrogenio > self.nitrogenio_max:
            alertas.append(
                f"🌾 NITROGÊNIO ALTO: {sensor_data.nitrogenio:.0f} mg/kg (máximo ideal: {self.nitrogenio_max:.0f} mg/kg)"
            )

        # Verificar Fósforo
        if sensor_data.fosforo < self.fosforo_min:
            alertas.append(
                f"🌿 FÓSFORO BAIXO: {sensor_data.fosforo:.0f} mg/kg (mínimo ideal: {self.fosforo_min:.0f} mg/kg)"
            )
        elif sensor_data.fosforo > self.fosforo_max:
            alertas.append(
                f"🌿 FÓSFORO ALTO: {sensor_data.fosforo:.0f} mg/kg (máximo ideal: {self.fosforo_max:.0f} mg/kg)"
            )

        # Verificar Potássio
        if sensor_data.potassio < self.potassio_min:
            alertas.append(
                f"🍃 POTÁSSIO BAIXO: {sensor_data.potassio:.0f} mg/kg (mínimo ideal: {self.potassio_min:.0f} mg/kg)"
            )
        elif sensor_data.potassio > self.potassio_max:
            alertas.append(
                f"🍃 POTÁSSIO ALTO: {sensor_data.potassio:.0f} mg/kg (máximo ideal: {self.potassio_max:.0f} mg/kg)"
            )

        # Verificar Condutividade (se configurado)
        if (
            self.condutividade_min is not None
            and sensor_data.condutividade < self.condutividade_min
        ):
            alertas.append(
                f"⚡ CONDUTIVIDADE BAIXA: {sensor_data.condutividade:.0f} uS/cm (mínimo ideal: {self.condutividade_min:.0f} uS/cm)"
            )
        elif (
            self.condutividade_max is not None
            and sensor_data.condutividade > self.condutividade_max
        ):
            alertas.append(
                f"⚡ CONDUTIVIDADE ALTA: {sensor_data.condutividade:.0f} uS/cm (máximo ideal: {self.condutividade_max:.0f} uS/cm)"
            )

        # Verificar Salinidade (se configurado)
        if (
            self.salinidade_min is not None
            and sensor_data.salinidade < self.salinidade_min
        ):
            alertas.append(
                f"🧂 SALINIDADE BAIXA: {sensor_data.salinidade:.0f} mg/L (mínimo ideal: {self.salinidade_min:.0f} mg/L)"
            )
        elif (
            self.salinidade_max is not None
            and sensor_data.salinidade > self.salinidade_max
        ):
            alertas.append(
                f"🧂 SALINIDADE ALTA: {sensor_data.salinidade:.0f} mg/L (máximo ideal: {self.salinidade_max:.0f} mg/L)"
            )

        # Verificar TDS (se configurado)
        if self.tds_min is not None and sensor_data.tds < self.tds_min:
            alertas.append(
                f"💧 TDS BAIXO: {sensor_data.tds:.0f} mg/L (mínimo ideal: {self.tds_min:.0f} mg/L)"
            )
        elif self.tds_max is not None and sensor_data.tds > self.tds_max:
            alertas.append(
                f"💧 TDS ALTO: {sensor_data.tds:.0f} mg/L (máximo ideal: {self.tds_max:.0f} mg/L)"
            )

        return alertas
