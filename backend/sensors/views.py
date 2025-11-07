import logging

from chatbot.chains import get_agent_executor
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
        mensagem = f"🌾 *ALERTA DE SOLO - {cultivo.upper()}*\n\n"
        mensagem += f"⏰ {sensor_data.timestamp.strftime('%d/%m/%Y %H:%M')}\n\n"
        mensagem += "*Parâmetros fora do limite ideal:*\n\n"

        for alerta in alertas:
            mensagem += f"{alerta}\n"

        # Adiciona recomendações baseadas nos alertas usando o agente de IA
        recomendacoes = self._generate_recommendations(alertas, sensor_data, cultivo)
        if recomendacoes:
            mensagem += f"\n🔧 *RECOMENDAÇÕES:*\n\n{recomendacoes}"

        mensagem += "\n📊 *Valores atuais completos:*\n"
        mensagem += f"• Umidade: {sensor_data.umidade:.1f}%\n"
        mensagem += f"• Temperatura: {sensor_data.temperatura:.1f}°C\n"
        mensagem += f"• pH: {sensor_data.ph:.1f}\n"
        mensagem += f"• Nitrogênio: {sensor_data.nitrogenio:.0f} mg/kg\n"
        mensagem += f"• Fósforo: {sensor_data.fosforo:.0f} mg/kg\n"
        mensagem += f"• Potássio: {sensor_data.potassio:.0f} mg/kg\n"

        mensagem += "\n💬 _Precisa de orientação? Fale comigo no WhatsApp para dicas personalizadas!_"

        return mensagem

    def _generate_recommendations(self, alerts, sensor_data, crop_name):
        """
        Gera recomendações personalizadas usando o agente de IA baseado nos alertas detectados
        """
        try:
            # Prepara o contexto completo para o agente
            context = f"""
📊 **CONTEXTO DO ALERTA - {crop_name.upper()}**

🚨 **Alertas Detectados:**
{chr(10).join(f'- {alert}' for alert in alerts)}

📈 **Dados Atuais dos Sensores:**
- Umidade: {sensor_data.umidade:.1f}%
- Temperatura: {sensor_data.temperatura:.1f}°C
- pH: {sensor_data.ph:.1f}
- Nitrogênio: {sensor_data.nitrogenio:.0f} mg/kg
- Fósforo: {sensor_data.fosforo:.0f} mg/kg
- Potássio: {sensor_data.potassio:.0f} mg/kg
- Condutividade: {sensor_data.condutividade:.0f} µS/cm
- Salinidade: {sensor_data.salinidade:.0f} mg/L
- TDS: {sensor_data.tds:.0f} mg/L

⏰ **Timestamp:** {sensor_data.timestamp.strftime('%d/%m/%Y %H:%M')}

🌾 **Cultivo:** {crop_name}
"""

            # Monta a pergunta para o agente
            prompt = f"""{context}

Com base nos alertas detectados acima e nos dados atuais dos sensores, forneça recomendações técnicas e práticas para o agricultor. 

**IMPORTANTE:**
- Seja objetivo e direto
- Forneça ações concretas que podem ser tomadas AGORA
- Considere o cultivo específico ({crop_name})
- Limite a resposta a 500 caracteres para caber no WhatsApp
- Use emojis para facilitar a leitura
- Não repita as informações dos alertas, foque nas AÇÕES

Formato esperado:
🔧 *RECOMENDAÇÕES:*

[suas recomendações aqui]
"""

            logger.info(f"Solicitando recomendações ao agente de IA para {crop_name}")

            # Obtém o agente executor
            agent_executor = get_agent_executor()

            # Executa o agente com chat_history vazio (chamada única sem contexto anterior)
            result = agent_executor.invoke({"input": prompt, "chat_history": []})

            # Extrai a resposta do agente
            ai_response = result.get("output", "")

            logger.info(
                f"Recomendações geradas pelo agente de IA: {len(ai_response)} caracteres"
            )

            # Remove o prefixo "🔧 *RECOMENDAÇÕES:*" se o agente já o incluiu
            if "🔧 *RECOMENDAÇÕES:*" in ai_response:
                ai_response = ai_response.replace("🔧 *RECOMENDAÇÕES:*", "").strip()

            return ai_response or self._generate_fallback_recommendations(alerts)

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações com IA: {str(e)}")
            # Fallback para recomendações estáticas em caso de erro
            return self._generate_fallback_recommendations(alerts)

    def _generate_fallback_recommendations(self, alerts):
        """
        Gera recomendações básicas como fallback caso o agente de IA falhe
        """
        recommendations = []

        # Recomendações básicas por tipo de alerta
        if any("UMIDADE" in alert for alert in alerts):
            recommendations.append("💧 Ajuste a irrigação conforme necessário")

        if any("TEMPERATURA" in alert for alert in alerts):
            recommendations.append("🌡️ Monitore as condições climáticas")

        if any("pH" in alert for alert in alerts):
            recommendations.append("⚗️ Realize análise de solo e correção de pH")

        if any(
            "NITROGÊNIO" in alert or "FÓSFORO" in alert or "POTÁSSIO" in alert
            for alert in alerts
        ):
            recommendations.append("🌾 Ajuste o plano de adubação (NPK)")

        if any("CONDUTIVIDADE" in alert or "SALINIDADE" in alert for alert in alerts):
            recommendations.append("⚡ Atenção à salinidade do solo")

        return (
            "\n".join(recommendations)
            if recommendations
            else "Consulte um agrônomo para orientações específicas."
        )


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
