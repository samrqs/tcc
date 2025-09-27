from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import AI_CONTEXTUALIZE_PROMPT, AI_SYSTEM_PROMPT

contextualize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", AI_CONTEXTUALIZE_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", AI_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


def get_agent_prompt() -> ChatPromptTemplate:
    """Retorna o prompt do agente com a data atual."""
    # Obtém a data atual no formato brasileiro
    current_date = datetime.now().strftime("%d/%m/%Y")
    current_month_year = datetime.now().strftime("%m/%Y")
    current_year = datetime.now().year

    system_message = (
        "Você é um assistente virtual que irá responder dúvidas dos clientes. "
        + "Use no máximo três frases e mantenha a resposta concisa.\n\n"
        + "Você tem acesso a ferramentas que podem ajudar a responder perguntas. "
        + "Use a ferramenta rag_search quando precisar buscar informações específicas "
        + "na base de conhecimento para responder perguntas dos usuários.\n\n"
        + f"INFORMAÇÕES IMPORTANTES SOBRE DATA E TEMPO:\n"
        + f"- Data atual: {current_date}\n"
        + f"- Mês/Ano atual: {current_month_year}\n"
        + f"- Ano atual: {current_year}\n"
        + f"- Quando o usuário mencionar 'este mês', refere-se ao mês {current_month_year}\n"
        + f"- Quando mencionar 'este ano', refere-se ao ano {current_year}\n"
        + f"- Para consultas SQL com datas, use os valores corretos baseados na data atual acima\n\n"
        + "EXEMPLO: Para 'temperaturas deste mês', use:\n"
        + f"- Mês: {datetime.now().month}\n"
        + f"- Ano: {current_year}"
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )


# Para compatibilidade com código existente
agent_prompt = get_agent_prompt()
