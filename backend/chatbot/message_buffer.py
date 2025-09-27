import asyncio
import logging
from collections import defaultdict

import redis.asyncio as redis
from asgiref.sync import sync_to_async

from .chains import get_conversational_agent
from .config import BUFFER_KEY_SUFIX, BUFFER_TTL, DEBOUNCE_SECONDS, REDIS_URL
from .evolution_api import send_whatsapp_message

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_agent = get_conversational_agent()
debounce_tasks = defaultdict(asyncio.Task)

logger = logging.getLogger(__name__)


def log(*args):
    logger.info("[BUFFER] %s", " ".join(str(arg) for arg in args))


@sync_to_async
def check_user_permission(phone_number: str) -> tuple[bool, str]:
    """
    Verifica se o usuário tem permissão para acessar dados do chatbot.

    Args:
        phone_number: Número de telefone do usuário (sem formatação especial)

    Returns:
        tuple: (tem_permissao, mensagem_de_resposta)
    """
    from users.models import User

    try:
        # Remove caracteres especiais do número para comparação
        clean_phone = "".join(filter(str.isdigit, phone_number))

        if user := User.objects.filter(phone__icontains=clean_phone).first():
            if user.is_active:
                log(f"Usuário autorizado: {user.email} ({phone_number})")
                return True, ""
            else:
                log(f"Usuário inativo tentou acessar: {user.email} ({phone_number})")
                return (
                    False,
                    "Sua conta está inativa. Entre em contato com o administrador para reativar o acesso.",
                )
        else:
            log(f"Usuário não autorizado tentou acessar: {phone_number}")
            return False, (
                "🚫 Acesso não autorizado.\n\n"
                "Este número de telefone não está cadastrado no sistema. "
                "Para ter acesso ao assistente virtual, entre em contato com o administrador "
                "para cadastrar seu número de telefone."
            )

    except Exception as e:
        logger.error(f"Erro ao verificar permissão para {phone_number}: {str(e)}")
        return False, "Erro interno. Tente novamente em alguns minutos."


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

        if full_message := " ".join(messages).strip():
            log(f"Processando mensagem para {chat_id}: {full_message}")

            # Extrai o número de telefone do chat_id
            phone_number = chat_id.split("@")[0] if "@" in chat_id else chat_id

            # Verifica permissão do usuário
            has_permission, permission_message = await check_user_permission(
                phone_number
            )

            if has_permission:
                # Usuário autorizado - processa normalmente
                log(f"Usuário autorizado, processando mensagem para {chat_id}")
                ai_response = conversational_agent.invoke(
                    input={"input": full_message},
                    config={"configurable": {"session_id": chat_id}},
                )["output"]
            else:
                # Usuário não autorizado - envia mensagem de erro
                log(f"Usuário não autorizado: {phone_number}")
                ai_response = permission_message

            send_whatsapp_message(
                number=chat_id,
                text=ai_response,
            )
        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f"Debounce cancelado para {chat_id}")
