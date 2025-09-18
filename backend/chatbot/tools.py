import logging
from typing import List, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .config import OPENWEATHER_API_KEY
from .metrics import track_error, track_rag_search, track_weather_search
from .vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


class RAGSearchInput(BaseModel):
    """Input para a ferramenta RAG Search."""

    query: str = Field(description="Pergunta ou consulta para buscar nos documentos")
    k: int = Field(
        default=3,
        description="Número máximo de documentos relevantes a retornar (padrão = 3)",
    )


class RAGSearchTool(BaseTool):
    """Ferramenta para buscar informações nos documentos RAG."""

    name: str = "rag_search"
    description: str = """
    Busque informações relevantes nos documentos da base de conhecimento.
    Use esta ferramenta para responder perguntas gerais ou encontrar trechos de referência.
    
    Exemplos de uso:
    - "Como plantar milho?"
    - "Quais práticas de irrigação existem?"
    - "Últimas técnicas para controle natural de pragas"
    """
    args_schema: Type[BaseModel] = RAGSearchInput

    def _run(self, query: str, k: int = 3) -> str:
        """Busca informações nos documentos RAG."""
        logger.info(f"RAG Search iniciado - Query: '{query}', k: {k}")

        try:
            # Track RAG search
            track_rag_search("general")

            logger.debug("Obtendo vectorstore...")
            vectorstore = get_vectorstore()
            retriever = vectorstore.as_retriever(search_kwargs={"k": k})
            logger.debug("Vectorstore obtido com sucesso")

            # Busca documentos relevantes
            logger.debug(f"Executando busca por documentos relevantes...")
            docs = retriever.get_relevant_documents(query)
            logger.info(f"RAG Search - Documentos encontrados: {len(docs)}")

            if not docs:
                logger.warning(
                    f"RAG Search - Nenhum documento encontrado para query: '{query}'"
                )
                return "Não foram encontradas informações relevantes nos documentos."

            # Formata as informações encontradas
            results = []
            logger.debug("Formatando resultados encontrados...")
            for i, doc in enumerate(docs, 1):
                content = doc.page_content.strip()
                original_length = len(content)

                if len(content) > 500:
                    content = content[:500] + "..."
                    logger.debug(
                        f"Resultado {i}: conteúdo truncado de {original_length} para 500 caracteres"
                    )
                else:
                    logger.debug(
                        f"Resultado {i}: conteúdo completo com {original_length} caracteres"
                    )

                results.append(f"Resultado {i}:\n{content}\n")

            if not results:
                logger.warning("RAG Search - Nenhum resultado formatado disponível")
                return "Não foram encontradas informações relevantes nos documentos."

            logger.info(
                f"RAG Search concluído com sucesso - Query: '{query}', Resultados: {len(results)}"
            )

            return "\n\n".join(results)

        except Exception as e:
            # Track error
            track_error("rag_search_error", "tools")
            logger.error(
                f"Erro no RAG Search - Query: '{query}', Erro: {str(e)}", exc_info=True
            )
            return f"Erro ao buscar nos documentos: {str(e)}"

    async def _arun(self, query: str, k: int = 3) -> str:
        """Versão assíncrona da busca."""
        return self._run(query, k)


class WeatherInput(BaseModel):
    """Input para a ferramenta Weather."""

    location: str = Field(
        default="Parelheiros,SP,BR",
        description="Localização para consultar o clima (cidade, estado, país)",
    )


class WeatherTool(BaseTool):
    """Ferramenta para consultar informações meteorológicas."""

    name: str = "weather_search"
    description: str = """
    Consulte informações meteorológicas atuais para uma localização específica.
    Use esta ferramenta para obter dados sobre temperatura, umidade, pressão atmosférica 
    e condições climáticas que podem afetar a agricultura.
    
    Exemplos de uso:
    - "Qual o clima atual em Parelheiros?"
    - "Está chovendo na região?"
    - "Qual a umidade do ar hoje?"
    """
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str = "Parelheiros,SP,BR") -> str:
        """Consulta informações meteorológicas."""
        try:
            # Track weather search
            track_weather_search(location)

            if not OPENWEATHER_API_KEY:
                track_error("missing_api_key", "weather_tool")
                return "API key do OpenWeatherMap não configurada. Entre em contato com o administrador."

            # URL da API OpenWeatherMap
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",  # Celsius
                "lang": "pt_br",  # Português brasileiro
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 401:
                track_error("api_auth_error", "weather_tool")
                return "Erro de autenticação na API meteorológica. Verifique a chave da API."

            if response.status_code == 404:
                track_error("location_not_found", "weather_tool")
                return f"Localização '{location}' não encontrada. Tente com o nome de uma cidade válida."

            if response.status_code != 200:
                track_error("api_request_error", "weather_tool")
                return f"Erro ao consultar dados meteorológicos: {response.status_code}"

            data = response.json()

            # Extrai informações relevantes
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})

            city_name = data.get("name", location)
            country = data.get("sys", {}).get("country", "")

            temperature = main.get("temp", 0)
            feels_like = main.get("feels_like", 0)
            humidity = main.get("humidity", 0)
            pressure = main.get("pressure", 0)

            description = weather.get("description", "").title()
            wind_speed = wind.get("speed", 0)

            # Formata a resposta
            weather_info = f"""🌤️ Clima em {city_name}, {country}

🌡️ Temperatura: {temperature:.1f}°C (sensação térmica: {feels_like:.1f}°C)
💧 Umidade: {humidity}%
📊 Pressão atmosférica: {pressure} hPa
🌬️ Vento: {wind_speed:.1f} m/s
☁️ Condição: {description}

📍 Localização consultada: {location}
"""

            logger.info(f"Weather Search - Location: {location}, Temp: {temperature}°C")

            return weather_info

        except requests.RequestException as e:
            track_error("connection_error", "weather_tool")
            logger.error(f"Erro na requisição meteorológica: {e}")
            return "Erro de conexão ao consultar dados meteorológicos. Tente novamente em alguns minutos."
        except Exception as e:
            track_error("weather_tool_error", "weather_tool")
            logger.error(f"Erro na WeatherTool: {e}")
            return f"Erro ao consultar informações meteorológicas: {str(e)}"

    async def _arun(self, location: str = "Parelheiros,SP,BR") -> str:
        """Versão assíncrona da consulta meteorológica."""
        return self._run(location)


def get_tools() -> List[BaseTool]:
    """Retorna a lista de ferramentas disponíveis."""
    return [RAGSearchTool(), WeatherTool()]
