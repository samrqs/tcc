from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import AI_SYSTEM_PROMPT


def get_agent_prompt() -> ChatPromptTemplate:
    """Retorna o prompt do agente com a data atual."""
    current_date = datetime.now().strftime("%d/%m/%Y")
    current_month_year = datetime.now().strftime("%m/%Y")
    current_year = datetime.now().year

    system_message = AI_SYSTEM_PROMPT.format(
        current_date=current_date,
        current_month_year=current_month_year,
        current_year=current_year,
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
