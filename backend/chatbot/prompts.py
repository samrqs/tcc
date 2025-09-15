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

agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Você é um assistente virtual que irá responder dúvidas dos clientes. "
                + "Use no máximo três frases e mantenha a resposta concisa.\n\n"
                + "Você tem acesso a ferramentas que podem ajudar a responder perguntas. "
                + "Use a ferramenta rag_search quando precisar buscar informações específicas "
                + "na base de conhecimento para responder perguntas dos usuários."
            ),
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)
