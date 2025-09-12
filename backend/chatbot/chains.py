from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL_NAME, OPENAI_MODEL_TEMPERATURE
from .prompts import prompt
from .vectorstore import get_vectorstore


def get_rag_chain():
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        temperature=OPENAI_MODEL_TEMPERATURE,
        api_key=OPENAI_API_KEY,
    )
    retrieval = get_vectorstore().as_retriever()

    return {"context": retrieval, "question": RunnablePassthrough()} | prompt | llm
