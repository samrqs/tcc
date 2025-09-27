import asyncio
import json
import os
import shutil
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.test import AsyncRequestFactory
from rest_framework import status


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to avoid real connections during tests"""
    with patch("chatbot.chains.ChatOpenAI") as mock_openai, patch(
        "chatbot.vectorstore.Chroma"
    ) as mock_chroma, patch(
        "chatbot.vectorstore.OpenAIEmbeddings"
    ) as mock_embeddings, patch(
        "chatbot.memory.RedisChatMessageHistory"
    ) as mock_redis_history, patch(
        "chatbot.message_buffer.redis_client"
    ) as mock_redis_client, patch(
        "chatbot.evolution_api.requests.post"
    ) as mock_requests:

        mock_openai.return_value = MagicMock()
        mock_chroma.return_value = MagicMock()
        mock_chroma.from_documents.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_redis_history.return_value = MagicMock()
        mock_redis_client.rpush = AsyncMock()
        mock_redis_client.expire = AsyncMock()
        mock_redis_client.lrange = AsyncMock()
        mock_redis_client.delete = AsyncMock()
        mock_requests.return_value = MagicMock()

        yield {
            "openai": mock_openai,
            "chroma": mock_chroma,
            "embeddings": mock_embeddings,
            "redis_history": mock_redis_history,
            "redis_client": mock_redis_client,
            "requests": mock_requests,
        }


@pytest.mark.asyncio
class TestChatbotWebhookView:
    def setup_method(self):
        self.factory = AsyncRequestFactory()

        # Import here to avoid initialization issues
        from .views import ChatbotWebhookView

        self.view = ChatbotWebhookView()

    async def test_post_valid_payload_individual_chat(self, mock_external_services):
        """Testa o processamento de uma mensagem válida de chat individual"""
        with patch("chatbot.views.buffer_message") as mock_buffer_message:
            mock_buffer_message.return_value = None

            payload = {
                "data": {
                    "message": {"conversation": "Olá, como você está?"},
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                }
            }

            request = self.factory.post(
                "/webhook/", data=json.dumps(payload), content_type="application/json"
            )

            response = await self.view.post(request)

            assert response.status_code == status.HTTP_201_CREATED
            response_data = json.loads(response.content)
            assert response_data["status"] == "success"

            mock_buffer_message.assert_called_once_with(
                chat_id="5511999999999@s.whatsapp.net", message="Olá, como você está?"
            )

    async def test_post_group_message_ignored(self, mock_external_services):
        """Testa que mensagens de grupo são ignoradas"""
        payload = {
            "data": {
                "message": {"conversation": "Mensagem de grupo"},
                "key": {"remoteJid": "120363043617067382@g.us"},
            }
        }

        request = self.factory.post(
            "/webhook/", data=json.dumps(payload), content_type="application/json"
        )

        response = await self.view.post(request)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = json.loads(response.content)
        assert response_data["status"] == "success"
        assert response_data["message"] == "Mensagem de grupo ignorada."

    async def test_post_invalid_json(self, mock_external_services):
        """Testa o tratamento de JSON inválido"""
        request = self.factory.post(
            "/webhook/", data="invalid json", content_type="application/json"
        )

        response = await self.view.post(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = json.loads(response.content)
        assert response_data["status"] == "error"

    async def test_post_missing_data_fields(self, mock_external_services):
        """Testa o tratamento de campos obrigatórios faltando"""
        payload = {"data": {"message": {}, "key": {}}}

        request = self.factory.post(
            "/webhook/", data=json.dumps(payload), content_type="application/json"
        )

        response = await self.view.post(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = json.loads(response.content)
        assert response_data["status"] == "error"


class TestChains:
    def test_get_agent_executor(self, mock_external_services):
        """Testa a criação do agent executor"""
        from .chains import get_agent_executor
        from .config import OPENAI_API_KEY, OPENAI_MODEL_NAME, OPENAI_MODEL_TEMPERATURE

        # Teste mais simples que verifica apenas se a função não falha
        with patch("chatbot.chains.get_tools") as mock_get_tools, patch(
            "chatbot.chains.get_agent_prompt"
        ) as mock_get_agent_prompt, patch(
            "chatbot.chains.create_tool_calling_agent"
        ) as mock_create_agent, patch(
            "chatbot.chains.AgentExecutor"
        ) as mock_agent_executor:

            mock_tools = []
            mock_get_tools.return_value = mock_tools
            mock_get_agent_prompt.return_value = MagicMock()
            mock_create_agent.return_value = MagicMock()
            mock_agent_executor.return_value = MagicMock()

            agent_executor = get_agent_executor()

            mock_external_services["openai"].assert_called_with(
                model=OPENAI_MODEL_NAME,
                temperature=OPENAI_MODEL_TEMPERATURE,
                api_key=OPENAI_API_KEY,
            )
            mock_get_tools.assert_called_once()
            mock_get_agent_prompt.assert_called_once()
            mock_create_agent.assert_called_once()
            mock_agent_executor.assert_called_once()
            assert agent_executor is not None

    def test_get_conversational_agent(self, mock_external_services):
        """Testa a criação do conversational agent"""
        from .chains import get_conversational_agent

        with patch(
            "chatbot.chains.get_agent_executor"
        ) as mock_get_agent_executor, patch(
            "chatbot.chains.RunnableWithMessageHistory"
        ) as mock_runnable:

            mock_agent_executor = MagicMock()
            mock_get_agent_executor.return_value = mock_agent_executor

            mock_conversational_agent = MagicMock()
            mock_runnable.return_value = mock_conversational_agent

            conversational_agent = get_conversational_agent()

            mock_get_agent_executor.assert_called_once()
            mock_runnable.assert_called_once()
            assert conversational_agent == mock_conversational_agent


class TestVectorstore:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(self.test_dir, "rag_files")
        os.makedirs(self.test_files_dir)

    def teardown_method(self):
        shutil.rmtree(self.test_dir)

    def test_load_documents_multiple_file_types(self, mock_external_services):
        """Testa o carregamento de documentos de diferentes tipos"""
        from .vectorstore import load_documents

        # Criar arquivos de teste
        pdf_file = os.path.join(self.test_files_dir, "test.pdf")
        txt_file = os.path.join(self.test_files_dir, "test.txt")
        csv_file = os.path.join(self.test_files_dir, "test.csv")

        with open(pdf_file, "w") as f:
            f.write("test pdf content")
        with open(txt_file, "w") as f:
            f.write("test txt content")
        with open(csv_file, "w") as f:
            f.write("test,csv,content")

        with patch("chatbot.vectorstore.RAG_FILES_DIR", self.test_files_dir), patch(
            "chatbot.vectorstore.PyPDFLoader"
        ) as mock_pdf_loader, patch(
            "chatbot.vectorstore.TextLoader"
        ) as mock_text_loader, patch(
            "chatbot.vectorstore.CSVLoader"
        ) as mock_csv_loader:

            # Configurar mocks
            mock_pdf_loader.return_value.load.return_value = [MagicMock()]
            mock_text_loader.return_value.load.return_value = [MagicMock()]
            mock_csv_loader.return_value.load.return_value = [MagicMock()]

            docs = load_documents()

            assert len(docs) == 3
            mock_pdf_loader.assert_called_once_with(pdf_file)
            mock_text_loader.assert_called_once_with(txt_file)
            mock_csv_loader.assert_called_once_with(csv_file)

    def test_load_documents_with_unknown_file_type(self, mock_external_services):
        """Testa o carregamento de documentos com tipo de arquivo desconhecido"""
        from .vectorstore import load_documents

        # Criar arquivo com extensão desconhecida
        unknown_file = os.path.join(self.test_files_dir, "test.unknown")
        txt_file = os.path.join(self.test_files_dir, "test.txt")

        with open(unknown_file, "w") as f:
            f.write("unknown file content")
        with open(txt_file, "w") as f:
            f.write("txt file content")

        with patch("chatbot.vectorstore.RAG_FILES_DIR", self.test_files_dir), patch(
            "chatbot.vectorstore.TextLoader"
        ) as mock_text_loader:

            mock_text_loader.return_value.load.return_value = [MagicMock()]

            docs = load_documents()

            # Apenas o arquivo .txt deve ter sido processado
            assert len(docs) == 1
            mock_text_loader.assert_called_once_with(txt_file)

    def test_get_vectorstore_with_documents(self, mock_external_services):
        """Testa a criação do vectorstore com documentos"""
        from .vectorstore import get_vectorstore

        with patch("chatbot.vectorstore.load_documents") as mock_load_docs, patch(
            "chatbot.vectorstore.RecursiveCharacterTextSplitter"
        ) as mock_splitter:

            mock_docs = [MagicMock(), MagicMock()]
            mock_load_docs.return_value = mock_docs

            mock_splitter.return_value.split_documents.return_value = mock_docs

            result = get_vectorstore()

            mock_load_docs.assert_called_once()
            mock_external_services["chroma"].from_documents.assert_called_once()
            assert result is not None

    def test_get_vectorstore_without_documents(self, mock_external_services):
        """Testa a criação do vectorstore sem documentos"""
        from .vectorstore import get_vectorstore

        with patch("chatbot.vectorstore.load_documents") as mock_load_docs:
            mock_load_docs.return_value = []

            result = get_vectorstore()

            mock_load_docs.assert_called_once()
            mock_external_services["chroma"].assert_called_once()
            assert result is not None


class TestEvolutionApi:
    def test_send_whatsapp_message(self, mock_external_services):
        """Testa o envio de mensagem via Evolution API"""
        from .evolution_api import send_whatsapp_message

        number = "5511999999999"
        text = "Mensagem de teste"

        with patch("chatbot.evolution_api.EVOLUTION_API_URL", "http://test.com"), patch(
            "chatbot.evolution_api.EVOLUTION_INSTANCE_NAME", "test_instance"
        ), patch("chatbot.evolution_api.EVOLUTION_AUTHENTICATION_API_KEY", "test_key"):

            send_whatsapp_message(number, text)

        mock_external_services["requests"].assert_called_once()
        args, kwargs = mock_external_services["requests"].call_args

        assert kwargs["url"] == "http://test.com/message/sendText/test_instance"
        assert kwargs["headers"]["apikey"] == "test_key"
        assert kwargs["json"]["number"] == number
        assert kwargs["json"]["text"] == text
        assert kwargs["json"]["delay"] == 2000


class TestMemory:
    def test_get_session_history(self, mock_external_services):
        """Testa a criação do histórico de sessão"""
        from .memory import get_session_history

        session_id = "test_session_123"

        with patch("chatbot.memory.REDIS_URL", "redis://localhost:6379"):
            result = get_session_history(session_id)

        mock_external_services["redis_history"].assert_called_once_with(
            session_id=session_id, url="redis://localhost:6379"
        )
        assert result is not None


@pytest.mark.asyncio
class TestMessageBuffer:
    def setup_method(self):
        self.chat_id = "5511999999999@s.whatsapp.net"
        self.message = "Mensagem de teste"

    async def test_buffer_message(self, mock_external_services):
        """Testa o buffer de mensagens"""
        from .message_buffer import buffer_message

        with patch(
            "chatbot.message_buffer.asyncio.create_task"
        ) as mock_create_task, patch(
            "chatbot.message_buffer.BUFFER_KEY_SUFIX", "_buffer"
        ), patch(
            "chatbot.message_buffer.BUFFER_TTL", 300
        ):

            mock_task = AsyncMock()
            mock_create_task.return_value = mock_task

            await buffer_message(self.chat_id, self.message)

            buffer_key = f"{self.chat_id}_buffer"
            mock_external_services["redis_client"].rpush.assert_called_once_with(
                buffer_key, self.message
            )
            mock_external_services["redis_client"].expire.assert_called_once_with(
                buffer_key, 300
            )
            mock_create_task.assert_called_once()

    async def test_handle_debounce(self, mock_external_services):
        """Testa o tratamento do debounce"""
        from .message_buffer import handle_debounce

        with patch("chatbot.message_buffer.conversational_agent") as mock_agent, patch(
            "chatbot.message_buffer.send_whatsapp_message"
        ) as mock_send_whatsapp, patch(
            "chatbot.message_buffer.asyncio.sleep"
        ) as mock_sleep, patch(
            "chatbot.message_buffer.BUFFER_KEY_SUFIX", "_buffer"
        ), patch(
            "chatbot.message_buffer.DEBOUNCE_SECONDS", "2"
        ), patch(
            "chatbot.message_buffer.check_user_permission"
        ) as mock_check_permission:

            mock_sleep.return_value = None
            mock_external_services["redis_client"].lrange.return_value = [
                "Olá",
                "como",
                "você",
                "está?",
            ]
            mock_agent.invoke.return_value = {"output": "Estou bem, obrigado!"}
            mock_check_permission.return_value = (True, "")

            await handle_debounce(self.chat_id)

            buffer_key = f"{self.chat_id}_buffer"
            mock_external_services["redis_client"].lrange.assert_called_once_with(
                buffer_key, 0, -1
            )
            mock_check_permission.assert_called_once()
            mock_agent.invoke.assert_called_once_with(
                input={"input": "Olá como você está?"},
                config={"configurable": {"session_id": self.chat_id}},
            )
            mock_send_whatsapp.assert_called_once_with(
                number=self.chat_id, text="Estou bem, obrigado!"
            )
            mock_external_services["redis_client"].delete.assert_called_once_with(
                buffer_key
            )

    async def test_handle_debounce_cancellation(self, mock_external_services):
        """Testa o cancelamento do debounce"""
        from .message_buffer import handle_debounce

        with patch("chatbot.message_buffer.asyncio.sleep") as mock_sleep:
            # Simular cancelamento
            mock_sleep.side_effect = asyncio.CancelledError("Task cancelled")

            try:
                await handle_debounce(self.chat_id)
            except asyncio.CancelledError:
                pass  # Esperado

    async def test_handle_debounce_empty_message(self, mock_external_services):
        """Testa o debounce com mensagem vazia"""
        from .message_buffer import handle_debounce

        with patch("chatbot.message_buffer.asyncio.sleep") as mock_sleep, patch(
            "chatbot.message_buffer.BUFFER_KEY_SUFIX", "_buffer"
        ):

            mock_sleep.return_value = None
            mock_external_services["redis_client"].lrange.return_value = []

            await handle_debounce(self.chat_id)

            buffer_key = f"{self.chat_id}_buffer"
            mock_external_services["redis_client"].lrange.assert_called_once_with(
                buffer_key, 0, -1
            )
            mock_external_services["redis_client"].delete.assert_called_once_with(
                buffer_key
            )


class TestUrls:
    def test_urls_patterns(self):
        """Testa os padrões de URL do chatbot"""
        from django.urls import resolve, reverse

        from .urls import urlpatterns

        assert len(urlpatterns) == 1

        # Testa se a URL do webhook pode ser resolvida
        url = reverse("chatbot-webhook")
        assert url == "/api/chatbot/webhook/"

        # Testa se a view correta é chamada
        resolver = resolve("/api/chatbot/webhook/")
        assert resolver.view_name == "chatbot-webhook"


class TestConfig:
    def test_config_imports(self):
        """Testa se todas as configurações podem ser importadas"""
        from .config import (
            AI_CONTEXTUALIZE_PROMPT,
            AI_SYSTEM_PROMPT,
            BUFFER_KEY_SUFIX,
            BUFFER_TTL,
            DEBOUNCE_SECONDS,
            EVOLUTION_API_URL,
            EVOLUTION_AUTHENTICATION_API_KEY,
            EVOLUTION_INSTANCE_NAME,
            OPENAI_API_KEY,
            OPENAI_MODEL_NAME,
            OPENAI_MODEL_TEMPERATURE,
            RAG_FILES_DIR,
            REDIS_URL,
            VECTOR_STORE_PATH,
        )

        # Verifica se as configurações existem (não são None)
        configs = [
            OPENAI_API_KEY,
            OPENAI_MODEL_NAME,
            OPENAI_MODEL_TEMPERATURE,
            AI_CONTEXTUALIZE_PROMPT,
            AI_SYSTEM_PROMPT,
            EVOLUTION_API_URL,
            EVOLUTION_INSTANCE_NAME,
            EVOLUTION_AUTHENTICATION_API_KEY,
            REDIS_URL,
            RAG_FILES_DIR,
            VECTOR_STORE_PATH,
            BUFFER_KEY_SUFIX,
            DEBOUNCE_SECONDS,
            BUFFER_TTL,
        ]

        for config in configs:
            assert config is not None


class TestPrompts:
    def test_contextualize_prompt_structure(self):
        """Testa a estrutura do prompt de contextualização"""
        from .config import AI_CONTEXTUALIZE_PROMPT
        from .prompts import contextualize_prompt

        assert contextualize_prompt is not None
        assert len(contextualize_prompt.messages) == 3

        # Verifica se contém os elementos esperados
        system_message = contextualize_prompt.messages[0]
        assert system_message.prompt.template == AI_CONTEXTUALIZE_PROMPT

    def test_qa_prompt_structure(self):
        """Testa a estrutura do prompt de Q&A"""
        from .config import AI_SYSTEM_PROMPT
        from .prompts import qa_prompt

        assert qa_prompt is not None
        assert len(qa_prompt.messages) == 3

        # Verifica se contém os elementos esperados
        system_message = qa_prompt.messages[0]
        assert system_message.prompt.template == AI_SYSTEM_PROMPT

    def test_prompts_contain_placeholders(self):
        """Testa se os prompts contêm os placeholders necessários"""
        from .prompts import contextualize_prompt, qa_prompt

        # Verifica se o contextualize_prompt tem os placeholders corretos
        contextualize_input_vars = set()
        for message in contextualize_prompt.messages:
            if hasattr(message, "variable_name"):
                contextualize_input_vars.add(message.variable_name)
            elif hasattr(message, "prompt") and hasattr(
                message.prompt, "input_variables"
            ):
                contextualize_input_vars.update(message.prompt.input_variables)

        # Verifica se o qa_prompt tem os placeholders corretos
        qa_input_vars = set()
        for message in qa_prompt.messages:
            if hasattr(message, "variable_name"):
                qa_input_vars.add(message.variable_name)
            elif hasattr(message, "prompt") and hasattr(
                message.prompt, "input_variables"
            ):
                qa_input_vars.update(message.prompt.input_variables)


class TestTools:
    """Testes para as ferramentas do chatbot"""

    def test_get_tools(self):
        """Testa se todas as ferramentas são retornadas"""
        from .tools import get_tools

        tools = get_tools()
        assert len(tools) == 4

        tool_names = [tool.name for tool in tools]
        expected_tools = ["rag_search", "weather_search", "web_scraping", "sql_select"]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_rag_search_input_validation(self):
        """Testa a validação de entrada da RAGSearchTool"""
        from .tools import RAGSearchInput

        # Teste com dados válidos
        valid_input = RAGSearchInput(query="test query", k=5)
        assert valid_input.query == "test query"
        assert valid_input.k == 5

        # Teste com valores padrão
        default_input = RAGSearchInput(query="test query")
        assert default_input.k == 3

    @patch("chatbot.tools.get_vectorstore")
    def test_rag_search_tool_success(self, mock_get_vectorstore):
        """Testa o funcionamento da RAGSearchTool com sucesso"""
        from .tools import RAGSearchTool

        # Mock do vectorstore
        mock_doc = MagicMock()
        mock_doc.page_content = "Este é um documento de teste sobre agricultura"

        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = [mock_doc]

        mock_vectorstore = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_get_vectorstore.return_value = mock_vectorstore

        tool = RAGSearchTool()
        result = tool._run("como plantar milho", k=3)

        assert "Resultado 1:" in result
        assert "Este é um documento de teste sobre agricultura" in result
        mock_get_vectorstore.assert_called_once()
        mock_retriever.get_relevant_documents.assert_called_once_with(
            "como plantar milho"
        )

    @patch("chatbot.tools.get_vectorstore")
    def test_rag_search_tool_no_results(self, mock_get_vectorstore):
        """Testa a RAGSearchTool quando não há resultados"""
        from .tools import RAGSearchTool

        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = []

        mock_vectorstore = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_get_vectorstore.return_value = mock_vectorstore

        tool = RAGSearchTool()
        result = tool._run("query inexistente")

        assert "Não foram encontradas informações relevantes nos documentos." in result

    @patch("chatbot.tools.get_vectorstore")
    def test_rag_search_tool_error(self, mock_get_vectorstore):
        """Testa o tratamento de erro da RAGSearchTool"""
        from .tools import RAGSearchTool

        mock_get_vectorstore.side_effect = Exception("Erro no vectorstore")

        tool = RAGSearchTool()
        result = tool._run("test query")

        assert "Erro ao buscar nos documentos:" in result

    def test_weather_input_validation(self):
        """Testa a validação de entrada da WeatherTool"""
        from .tools import WeatherInput

        # Teste com localização customizada
        weather_input = WeatherInput(location="São Paulo,SP,BR")
        assert weather_input.location == "São Paulo,SP,BR"

        # Teste com valor padrão
        default_input = WeatherInput()
        assert default_input.location == "Parelheiros,SP,BR"

    @patch("chatbot.tools.requests.get")
    @patch("chatbot.tools.OPENWEATHER_API_KEY", "test_key")
    def test_weather_tool_success(self, mock_get):
        """Testa o funcionamento da WeatherTool com sucesso"""
        from .tools import WeatherTool

        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Parelheiros",
            "sys": {"country": "BR"},
            "main": {
                "temp": 25.5,
                "feels_like": 27.0,
                "humidity": 65,
                "pressure": 1013,
            },
            "weather": [{"description": "céu limpo"}],
            "wind": {"speed": 3.2},
        }
        mock_get.return_value = mock_response

        tool = WeatherTool()
        result = tool._run("Parelheiros,SP,BR")

        assert "🌤️ Clima em Parelheiros, BR" in result
        assert "25.5°C" in result
        assert "27.0°C" in result
        assert "65%" in result
        assert "céu limpo" in result.lower()

    @patch("chatbot.tools.requests.get")
    @patch("chatbot.tools.OPENWEATHER_API_KEY", None)
    def test_weather_tool_no_api_key(self, mock_get):
        """Testa a WeatherTool sem chave da API"""
        from .tools import WeatherTool

        tool = WeatherTool()
        result = tool._run()

        assert "API key do OpenWeatherMap não configurada" in result

    @patch("chatbot.tools.requests.get")
    @patch("chatbot.tools.OPENWEATHER_API_KEY", "test_key")
    def test_weather_tool_location_not_found(self, mock_get):
        """Testa a WeatherTool com localização não encontrada"""
        from .tools import WeatherTool

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        tool = WeatherTool()
        result = tool._run("LocalizacaoInexistente")

        assert "Localização 'LocalizacaoInexistente' não encontrada" in result

    def test_web_scraping_input_validation(self):
        """Testa a validação de entrada da WebScrapingTool"""
        from .tools import WebScrapingInput

        # Teste com todos os parâmetros
        scraping_input = WebScrapingInput(
            url="https://example.com", selector="h1", extract_links=True
        )
        assert scraping_input.url == "https://example.com"
        assert scraping_input.selector == "h1"
        assert scraping_input.extract_links is True

        # Teste com valores padrão
        default_input = WebScrapingInput(url="https://example.com")
        assert default_input.selector == ""
        assert default_input.extract_links is False

    @patch("chatbot.tools.requests.get")
    def test_web_scraping_tool_success(self, mock_get):
        """Testa o funcionamento da WebScrapingTool com sucesso"""
        from .tools import WebScrapingTool

        # Mock HTML de resposta
        html_content = """
        <html>
            <head><title>Teste de Agricultura</title></head>
            <body>
                <h1>Título Principal</h1>
                <p>Este é um parágrafo sobre agricultura sustentável.</p>
                <a href="https://example.com/link1">Link de exemplo</a>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode("utf-8")
        mock_get.return_value = mock_response

        tool = WebScrapingTool()
        result = tool._run("https://example.com")

        assert "Teste de Agricultura" in result
        assert "🌐 **Fonte:** https://example.com" in result

    @patch("chatbot.tools.requests.get")
    def test_web_scraping_tool_invalid_url(self, mock_get):
        """Testa a WebScrapingTool com URL inválida"""
        from .tools import WebScrapingTool

        tool = WebScrapingTool()
        result = tool._run("url-invalida")

        assert "URL inválida" in result

    @patch("chatbot.tools.requests.get")
    def test_web_scraping_tool_http_error(self, mock_get):
        """Testa a WebScrapingTool com erro HTTP"""
        from .tools import WebScrapingTool

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        tool = WebScrapingTool()
        result = tool._run("https://example.com")

        assert "Erro HTTP 500" in result

    def test_sql_select_input_validation(self):
        """Testa a validação de entrada da SQLSelectTool"""
        from .tools import SQLSelectInput

        # Teste com parâmetros
        sql_input = SQLSelectInput(query="SELECT * FROM test WHERE id = %s", params=[1])
        assert sql_input.query == "SELECT * FROM test WHERE id = %s"
        assert sql_input.params == [1]

        # Teste com valores padrão
        default_input = SQLSelectInput(query="SELECT * FROM test")
        assert default_input.params == []

    def test_sql_select_tool_validate_query(self):
        """Testa a validação de queries da SQLSelectTool"""
        from .tools import SQLSelectTool

        tool = SQLSelectTool()

        # Queries válidas
        assert tool._validate_query("SELECT * FROM users") is True
        assert tool._validate_query("select count(*) from sensors") is True
        assert (
            tool._validate_query("SELECT id, name FROM users WHERE active = true")
            is True
        )

        # Queries inválidas
        assert tool._validate_query("INSERT INTO users VALUES (1, 'test')") is False
        assert tool._validate_query("UPDATE users SET name = 'test'") is False
        assert tool._validate_query("DELETE FROM users") is False
        assert tool._validate_query("DROP TABLE users") is False
        assert tool._validate_query("SELECT * FROM users; DROP TABLE users;") is False
        assert tool._validate_query("SELECT * FROM pg_user") is False

    def test_sql_select_tool_add_limit(self):
        """Testa a adição automática de LIMIT"""
        from .tools import SQLSelectTool

        tool = SQLSelectTool()

        # Query sem LIMIT - deve adicionar
        query1 = "SELECT * FROM users"
        result1 = tool._add_limit_to_query(query1)
        assert "LIMIT 50" in result1

        # Query com LIMIT - não deve modificar
        query2 = "SELECT * FROM users LIMIT 10"
        result2 = tool._add_limit_to_query(query2)
        assert result2 == query2

        # Query COUNT - não deve adicionar LIMIT
        query3 = "SELECT COUNT(*) FROM users"
        result3 = tool._add_limit_to_query(query3)
        assert "LIMIT" not in result3

    def test_sql_select_tool_format_results(self):
        """Testa a formatação de resultados da SQLSelectTool"""
        from .tools import SQLSelectTool

        tool = SQLSelectTool()

        # Teste com resultados
        results = [(1, "João", "joao@email.com"), (2, "Maria", "maria@email.com")]
        columns = ["id", "name", "email"]

        formatted = tool._format_results(results, columns)
        assert "id | name | email" in formatted
        assert "João" in formatted
        assert "Maria" in formatted
        assert "📊 Total: 2 resultado(s)" in formatted

        # Teste sem resultados
        empty_formatted = tool._format_results([], columns)
        assert "Nenhum resultado encontrado." in empty_formatted

    @patch("chatbot.tools.connection")
    def test_sql_select_tool_execute_query_sync(self, mock_connection):
        """Testa a execução síncrona de query"""
        from .tools import SQLSelectTool

        # Mock do cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_cursor.description = [("id",), ("name",)]

        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        tool = SQLSelectTool()
        results, columns = tool._execute_query_sync("SELECT id, name FROM users", [])

        assert results == [(1, "test")]
        assert columns == ["id", "name"]
        # Quando params está vazio, execute é chamado apenas com a query
        mock_cursor.execute.assert_called_once_with("SELECT id, name FROM users")

    @patch("chatbot.tools.connection")
    def test_sql_select_tool_run_success(self, mock_connection):
        """Testa a execução bem-sucedida da SQLSelectTool"""
        from .tools import SQLSelectTool

        # Mock do cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "João")]
        mock_cursor.description = [("id",), ("name",)]

        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        tool = SQLSelectTool()
        result = tool._run("SELECT id, name FROM users_user", [])

        assert "id | name" in result
        assert "João" in result
        assert "📊 Total: 1 resultado(s)" in result

    def test_sql_select_tool_run_invalid_query(self):
        """Testa a SQLSelectTool com query inválida"""
        from .tools import SQLSelectTool

        tool = SQLSelectTool()
        result = tool._run("DROP TABLE users", [])

        assert "Apenas queries SELECT são permitidas" in result

    @patch("chatbot.tools.connection")
    def test_sql_select_tool_run_database_error(self, mock_connection):
        """Testa a SQLSelectTool com erro de banco de dados"""
        from .tools import SQLSelectTool

        mock_connection.cursor.side_effect = Exception("Database connection error")

        tool = SQLSelectTool()
        result = tool._run("SELECT * FROM users_user", [])

        assert "Erro ao executar query:" in result

    @pytest.mark.asyncio
    async def test_sql_select_tool_arun(self):
        """Testa a execução assíncrona da SQLSelectTool"""
        from .tools import SQLSelectTool

        tool = SQLSelectTool()

        # Teste com query inválida (não precisa de mock de BD)
        result = await tool._arun("INSERT INTO users VALUES (1)", [])
        assert "Apenas queries SELECT são permitidas" in result

    @pytest.mark.asyncio
    async def test_rag_search_tool_arun(self):
        """Testa a execução assíncrona da RAGSearchTool"""
        from .tools import RAGSearchTool

        with patch("chatbot.tools.get_vectorstore") as mock_get_vectorstore:
            mock_doc = MagicMock()
            mock_doc.page_content = "Documento de teste"

            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents.return_value = [mock_doc]

            mock_vectorstore = MagicMock()
            mock_vectorstore.as_retriever.return_value = mock_retriever
            mock_get_vectorstore.return_value = mock_vectorstore

            tool = RAGSearchTool()
            result = await tool._arun("test query")

            assert "Resultado 1:" in result
            assert "Documento de teste" in result

    @pytest.mark.asyncio
    async def test_weather_tool_arun(self):
        """Testa a execução assíncrona da WeatherTool"""
        from .tools import WeatherTool

        with patch("chatbot.tools.OPENWEATHER_API_KEY", None):
            tool = WeatherTool()
            result = await tool._arun()

            assert "API key do OpenWeatherMap não configurada" in result

    @pytest.mark.asyncio
    async def test_web_scraping_tool_arun(self):
        """Testa a execução assíncrona da WebScrapingTool"""
        from .tools import WebScrapingTool

        tool = WebScrapingTool()
        result = await tool._arun("url-invalida")

        assert "URL inválida" in result
