import os

from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import OPENAI_API_KEY, OPENAI_MODEL_NAME, OPENAI_MODEL_TEMPERATURE
from .prompts import prompt

csv_path = os.path.join(os.path.dirname(__file__), "Q&A.csv")


def get_rag_chain():
    loader = CSVLoader(file_path=csv_path)
    documents = loader.load()
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_documents(documents, embeddings)
    retrieval = vector_store.as_retriever()
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        temperature=OPENAI_MODEL_TEMPERATURE,
    )

    return {"context": retrieval, "question": RunnablePassthrough()} | prompt | llm
