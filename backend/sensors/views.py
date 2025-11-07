import logging

from chatbot.evolution_api import send_whatsapp_message
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CropAlert
from .serializers import CropAlertSerializer, SensorDataSerializer

logger = logging.getLogger(__name__)


class SensorWebhookView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SensorDataSerializer(data=request.data)

        if serializer.is_valid():
            # Salva os dados do sensor
            sensor_data = serializer.save(user=request.user)

            # Verifica se existe configuração de plantio ativa para o usuário
            try:
                crop_alert = CropAlert.objects.filter(
                    user=request.user, alertas_ativos=True
                ).first()

                if crop_alert:
                    # Verifica se os valores do sensor atingiram os limites configurados
                    alerts = crop_alert.check_limits(sensor_data)

                    # Se houver alertas, envia mensagem via WhatsApp
                    if alerts and request.user.phone:
                        alert_message = self._format_alert_message(
                            crop_alert.cultivo, alerts, sensor_data
                        )

                        try:
                            # Remove caracteres especiais do número do telefone
                            phone_number = (
                                request.user.phone.replace("+", "")
                                .replace("-", "")
                                .replace(" ", "")
                            )
                            send_whatsapp_message(
                                number=phone_number, text=alert_message
                            )
                            logger.info(
                                f"Alerta enviado para {request.user.email}: {len(alerts)} alertas"
                            )
                        except Exception as e:
                            logger.error(
                                f"Erro ao enviar alerta via WhatsApp para {request.user.email}: {str(e)}"
                            )

            except Exception as e:
                logger.error(f"Erro ao verificar limites de plantio: {str(e)}")
                # Continua mesmo se houver erro na verificação de limites

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _format_alert_message(self, cultivo, alertas, sensor_data):
        """
        Formata a mensagem de alerta para envio via WhatsApp com recomendações
        """
        mensagem = f"🌾 *ALERTA DE SENSORES - {cultivo.upper()}*\n\n"
        mensagem += f"⏰ {sensor_data.timestamp.strftime('%d/%m/%Y %H:%M')}\n\n"
        mensagem += "*Parâmetros fora do limite ideal:*\n\n"

        for alerta in alertas:
            mensagem += f"{alerta}\n"

        # Adiciona recomendações baseadas nos alertas
        recomendacoes = self._generate_recommendations(alertas, sensor_data)
        if recomendacoes:
            mensagem += f"\n� *RECOMENDAÇÕES:*\n\n{recomendacoes}"

        mensagem += "\n�📊 *Valores atuais completos:*\n"
        mensagem += f"• Umidade: {sensor_data.umidade:.1f}%\n"
        mensagem += f"• Temperatura: {sensor_data.temperatura:.1f}°C\n"
        mensagem += f"• pH: {sensor_data.ph:.1f}\n"
        mensagem += f"• Nitrogênio: {sensor_data.nitrogenio:.0f} mg/kg\n"
        mensagem += f"• Fósforo: {sensor_data.fosforo:.0f} mg/kg\n"
        mensagem += f"• Potássio: {sensor_data.potassio:.0f} mg/kg\n"

        mensagem += "\n💬 _Precisa de orientação? Fale comigo no WhatsApp para dicas personalizadas!_"

        return mensagem

    def _generate_recommendations(self, alerts, sensor_data):
        """
        Gera recomendações personalizadas baseadas nos alertas detectados
        """
        recommendations = []

        for alert in alerts:
            # Recomendações para UMIDADE
            if "UMIDADE BAIXA" in alert:
                recommendations.append(
                    "💧 *Umidade Baixa:*\n   → Aumentar irrigação gradualmente\n   → Verificar sistema de irrigação\n   → Considerar mulching para retenção de água"
                )
            elif "UMIDADE ALTA" in alert:
                recommendations.append(
                    "💧 *Umidade Alta:*\n   → Reduzir ou suspender irrigação\n   → Melhorar drenagem do solo\n   → Evitar encharcamento (risco de doenças)"
                )

            # Recomendações para TEMPERATURA
            if "TEMPERATURA BAIXA" in alert:
                recommendations.append(
                    "🌡️ *Temperatura Baixa:*\n   → Monitorar previsão de geadas\n   → Considerar cobertura/proteção das plantas\n   → Avaliar época de plantio"
                )
            elif "TEMPERATURA ALTA" in alert:
                recommendations.append(
                    "🌡️ *Temperatura Alta:*\n   → Aumentar frequência de irrigação\n   → Irrigar nas horas mais frescas\n   → Monitorar estresse hídrico das plantas"
                )

            # Recomendações para pH
            if "pH BAIXO" in alert:
                recommendations.append(
                    f"⚗️ *pH Baixo (Solo Ácido):*\n   → Aplicar calcário dolomítico\n   → Fazer análise completa do solo\n   → pH atual: {sensor_data.ph:.1f} (ideal: 6.0-7.0)"
                )
            elif "pH ALTO" in alert:
                recommendations.append(
                    f"⚗️ *pH Alto (Solo Alcalino):*\n   → Aplicar enxofre elementar ou gesso\n   → Adicionar matéria orgânica\n   → pH atual: {sensor_data.ph:.1f} (ideal: 6.0-7.0)"
                )

            # Recomendações para NITROGÊNIO
            if "NITROGÊNIO BAIXO" in alert:
                recommendations.append(
                    "🌾 *Nitrogênio Baixo:*\n   → Aplicar ureia ou sulfato de amônio\n   → Fazer adubação de cobertura\n   → Considerar plantio de leguminosas (fixam N)"
                )
            elif "NITROGÊNIO ALTO" in alert:
                recommendations.append(
                    "🌾 *Nitrogênio Alto:*\n   → Suspender adubação nitrogenada\n   → Aumentar irrigação (lixiviação moderada)\n   → Monitorar excesso vegetativo"
                )

            # Recomendações para FÓSFORO
            if "FÓSFORO BAIXO" in alert:
                recommendations.append(
                    "🌿 *Fósforo Baixo:*\n   → Aplicar superfosfato simples/triplo\n   → Usar fosfato natural (liberação gradual)\n   → Importante para raízes e floração"
                )
            elif "FÓSFORO ALTO" in alert:
                recommendations.append(
                    "🌿 *Fósforo Alto:*\n   → Suspender adubação fosfatada\n   → Pode bloquear absorção de zinco e ferro\n   → Monitorar sintomas de deficiência de micronutrientes"
                )

            # Recomendações para POTÁSSIO
            if "POTÁSSIO BAIXO" in alert:
                recommendations.append(
                    "🍃 *Potássio Baixo:*\n   → Aplicar cloreto de potássio (KCl)\n   → Usar sulfato de potássio em solos salinos\n   → Essencial para qualidade e resistência"
                )
            elif "POTÁSSIO ALTO" in alert:
                recommendations.append(
                    "🍃 *Potássio Alto:*\n   → Suspender adubação potássica\n   → Pode competir com cálcio e magnésio\n   → Monitorar equilíbrio nutricional"
                )

            # Recomendações para CONDUTIVIDADE/SALINIDADE
            if "CONDUTIVIDADE ALTA" in alert or "SALINIDADE ALTA" in alert:
                recommendations.append(
                    "⚡ *Salinidade/Condutividade Alta:*\n   → Aumentar lâmina de irrigação (lixiviação)\n   → Usar água de melhor qualidade\n   → Evitar excesso de fertilizantes"
                )

        # Remove duplicatas mantendo a ordem
        unique_recommendations = []
        for recommendation in recommendations:
            if recommendation not in unique_recommendations:
                unique_recommendations.append(recommendation)

        return "\n\n".join(unique_recommendations) if unique_recommendations else ""


class CropAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de CropAlert (Alertas de Cultivo).

    Endpoints:
    - GET /api/crop/alerts/ - Lista todos os alertas do usuário
    - POST /api/crop/alerts/ - Cria um novo alerta
    - GET /api/crop/alerts/{id}/ - Detalhe de um alerta específico
    - PUT /api/crop/alerts/{id}/ - Atualiza completamente um alerta
    - PATCH /api/crop/alerts/{id}/ - Atualiza parcialmente um alerta
    - DELETE /api/crop/alerts/{id}/ - Deleta um alerta
    """

    serializer_class = CropAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna apenas os alertas do usuário autenticado"""
        return CropAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Salva o alerta associando ao usuário autenticado"""
        serializer.save(user=self.request.user)
        logger.info(
            f"CropAlert criado para {self.request.user.email}: {serializer.data.get('cultivo')}"
        )

    def perform_update(self, serializer):
        """Log de atualização"""
        serializer.save()
        logger.info(
            f"CropAlert atualizado para {self.request.user.email}: {serializer.data.get('cultivo')}"
        )

    def perform_destroy(self, instance):
        """Log de deleção"""
        cultivo = instance.cultivo
        instance.delete()
        logger.info(f"CropAlert deletado para {self.request.user.email}: {cultivo}")
