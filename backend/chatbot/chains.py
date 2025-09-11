import os

from decouple import config
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

csv_path = os.path.join(os.path.dirname(__file__), "Q&A.csv")


def get_rag_chain():
    loader = CSVLoader(file_path=csv_path)
    documents = loader.load()
    embeddings = OpenAIEmbeddings(api_key=config("OPENAI_API_KEY"))
    vector_store = FAISS.from_documents(documents, embeddings)
    retrieval = vector_store.as_retriever()
    llm = ChatOpenAI()

    template = "Você é um atendente de IA, contexto:{context}, pergunta:{question}"
    prompt = ChatPromptTemplate.from_template(template)

    return {"context": retrieval, "question": RunnablePassthrough()} | prompt | llm
