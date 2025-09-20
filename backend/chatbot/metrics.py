import logging

from django.utils.deprecation import MiddlewareMixin
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Métricas customizadas do chatbot
chatbot_messages_total = Counter(
    "chatbot_messages_total",
    "Total number of messages processed by chatbot",
    ["phone_number", "message_type"],
)

chatbot_response_time = Histogram(
    "chatbot_response_time_seconds",
    "Time taken to process chatbot messages",
    ["phone_number"],
)

chatbot_rag_searches = Counter(
    "chatbot_rag_searches_total",
    "Total number of RAG searches performed",
    ["query_type"],
)

chatbot_weather_searches = Counter(
    "chatbot_weather_searches_total",
    "Total number of weather searches performed",
    ["location"],
)

chatbot_active_conversations = Gauge(
    "chatbot_active_conversations", "Number of active conversations"
)

chatbot_errors_total = Counter(
    "chatbot_errors_total",
    "Total number of chatbot errors",
    ["error_type", "component"],
)

# Buffer metrics
chatbot_buffer_size = Gauge(
    "chatbot_buffer_size", "Current size of message buffer", ["chat_id"]
)

chatbot_debounce_triggered = Counter(
    "chatbot_debounce_triggered_total",
    "Number of times debounce was triggered",
    ["chat_id"],
)


def track_message_processed(phone_number: str, message_type: str = "text"):
    """Incrementa contador de mensagens processadas."""
    chatbot_messages_total.labels(
        phone_number=phone_number, message_type=message_type
    ).inc()
    logger.info(f"Metric tracked: message processed for {phone_number}")


def track_response_time(phone_number: str, duration: float):
    """Registra tempo de resposta."""
    chatbot_response_time.labels(phone_number=phone_number).observe(duration)
    logger.info(f"Metric tracked: response time {duration}s for {phone_number}")


def track_rag_search(query_type: str = "general"):
    """Incrementa contador de buscas RAG."""
    chatbot_rag_searches.labels(query_type=query_type).inc()
    logger.info(f"Metric tracked: RAG search {query_type}")


def track_weather_search(location: str = "unknown"):
    """Incrementa contador de buscas meteorológicas."""
    chatbot_weather_searches.labels(location=location).inc()
    logger.info(f"Metric tracked: weather search for {location}")


def track_error(error_type: str, component: str):
    """Incrementa contador de erros."""
    chatbot_errors_total.labels(error_type=error_type, component=component).inc()
    logger.error(f"Metric tracked: error {error_type} in {component}")


def update_active_conversations(count: int):
    """Atualiza número de conversas ativas."""
    chatbot_active_conversations.set(count)
    logger.info(f"Metric updated: {count} active conversations")


def update_buffer_size(chat_id: str, size: int):
    """Atualiza tamanho do buffer."""
    chatbot_buffer_size.labels(chat_id=chat_id).set(size)


def track_debounce_triggered(chat_id: str):
    """Incrementa contador de debounce."""
    chatbot_debounce_triggered.labels(chat_id=chat_id).inc()
