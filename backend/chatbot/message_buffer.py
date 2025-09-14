import asyncio
import logging
from collections import defaultdict

import redis.asyncio as redis

from .chains import get_conversational_rag_chain
from .config import BUFFER_KEY_SUFIX, BUFFER_TTL, DEBOUNCE_SECONDS, REDIS_URL
from .evolution_api import send_whatsapp_message

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_rag_chain = get_conversational_rag_chain()
debounce_tasks = defaultdict(asyncio.Task)

logger = logging.getLogger(__name__)


def log(*args):
    logger.info("[BUFFER] %s", " ".join(str(arg) for arg in args))


async def buffer_message(chat_id: str, message: str):
    buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, BUFFER_TTL)

    log(f"Mensagem adicionada ao buffer de {chat_id}: {message}")

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        log(f"Debounce resetado para {chat_id}")

    debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id))


async def handle_debounce(chat_id: str):
    try:
        log(f"Iniciando debounce para {chat_id}")
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = " ".join(messages).strip()
        if full_message:
            log(f"Enviando mensagem agrupada para {chat_id}: {full_message}")
            ai_response = conversational_rag_chain.invoke(
                input={"input": full_message},
                config={"configurable": {"session_id": chat_id}},
            )["answer"]

            send_whatsapp_message(
                number=chat_id,
                text=ai_response,
            )
        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f"Debounce cancelado para {chat_id}")
