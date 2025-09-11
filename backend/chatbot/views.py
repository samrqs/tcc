import json
import logging
import os

from decouple import config
from django.http import JsonResponse
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from rest_framework import status
from rest_framework.views import APIView

from .evolution_api import send_whatsapp_message

logger = logging.getLogger(__name__)

csv_path = os.path.join(os.path.dirname(__file__), "Q&A.csv")
loader = CSVLoader(file_path=csv_path)
documents = loader.load()
embeddings = OpenAIEmbeddings(api_key=config("OPENAI_API_KEY"))
vector_store = FAISS.from_documents(documents, embeddings)
retrieval = vector_store.as_retriever()

llm = ChatOpenAI()

template = "Você é um atendente de IA, contexto:{context}, pergunta:{question}"
prompt = ChatPromptTemplate.from_template(template)

chain = {"context": retrieval, "question": RunnablePassthrough()} | prompt | llm


class ChatbotWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            data = payload.get("data")
            message = data.get("message").get("conversation")
            chat_id = data.get("key").get("remoteJid")
            sender_number = chat_id.split("@")[0]
            is_group = "@g.us" in chat_id

            if is_group:
                return JsonResponse(
                    {"status": "success", "message": "Mensagem de grupo ignorada."},
                    status=status.HTTP_201_CREATED,
                )

            response = chain.invoke(message)
            send_whatsapp_message(
                sender_number,
                response.content,
            )
            return JsonResponse({"status": "success"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar a mensagem: {str(e)}")
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
