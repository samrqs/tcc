import asyncio
import logging
from typing import List, Type
from urllib.parse import urljoin, urlparse

import requests
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.db import connection
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


class WebScrapingInput(BaseModel):
    """Input para a ferramenta de Web Scraping."""

    url: str = Field(description="URL da página web para extrair informações")
    selector: str = Field(
        default="",
        description="Seletor CSS opcional para extrair elementos específicos (ex: 'h1', '.classe', '#id')",
    )
    extract_links: bool = Field(
        default=False,
        description="Se deve extrair links da página",
    )


class WebScrapingTool(BaseTool):
    """Ferramenta para extrair informações de páginas web usando BeautifulSoup."""

    name: str = "web_scraping"
    description: str = """
    Extrai informações de páginas web usando BeautifulSoup.
    Use esta ferramenta para obter conteúdo de sites, notícias sobre agricultura,
    preços de commodities, informações técnicas ou qualquer conteúdo web relevante.
    
    Exemplos de uso:
    - "Extrair informações sobre preços do milho de uma página"
    - "Buscar notícias sobre agricultura sustentável"
    - "Obter dados técnicos de equipamentos agrícolas"
    """
    args_schema: Type[BaseModel] = WebScrapingInput

    def _run(self, url: str, selector: str = "", extract_links: bool = False) -> str:
        """Extrai informações de uma página web."""
        logger.info(f"Web Scraping iniciado - URL: '{url}', Selector: '{selector}'")

        try:
            # Validação básica da URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return "URL inválida. Por favor, forneça uma URL completa (ex: https://exemplo.com)"

            # Headers para simular um navegador real
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            # Requisição HTTP
            logger.debug(f"Fazendo requisição para: {url}")
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                track_error("http_error", "web_scraping")
                return f"Erro HTTP {response.status_code} ao acessar a página: {url}"

            # Parse do HTML com BeautifulSoup
            logger.debug("Fazendo parse do HTML...")
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove scripts e estilos para um conteúdo mais limpo
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()

            result_parts = []

            # Título da página
            title = soup.find("title")
            if title:
                result_parts.append(f"📄 **Título:** {title.get_text().strip()}")

            # Se um seletor específico foi fornecido
            if selector:
                logger.debug(f"Aplicando seletor: {selector}")
                elements = soup.select(selector)
                if elements:
                    result_parts.append(f"\n🎯 **Conteúdo do seletor '{selector}':**")
                    for i, element in enumerate(elements[:5], 1):  # Máximo 5 elementos
                        text = element.get_text().strip()
                        if text:
                            result_parts.append(
                                f"{i}. {text[:300]}{'...' if len(text) > 300 else ''}"
                            )
                else:
                    result_parts.append(
                        f"\n❌ Nenhum elemento encontrado com o seletor '{selector}'"
                    )
            else:
                # Extração de conteúdo principal
                main_content = []

                # Tenta encontrar o conteúdo principal
                main_areas = soup.find_all(
                    ["main", "article", "div"],
                    class_=lambda x: x
                    and any(
                        keyword in x.lower()
                        for keyword in ["content", "main", "article", "post", "body"]
                    ),
                )

                if main_areas:
                    for area in main_areas[:2]:  # Máximo 2 áreas principais
                        text = area.get_text().strip()
                        if len(text) > 50:  # Filtra textos muito pequenos
                            main_content.append(text[:800])  # Limita o tamanho
                else:
                    # Fallback: pega todos os parágrafos
                    paragraphs = soup.find_all("p")
                    for p in paragraphs[:5]:  # Máximo 5 parágrafos
                        text = p.get_text().strip()
                        if len(text) > 30:
                            main_content.append(text[:400])

                if main_content:
                    result_parts.append("\n📝 **Conteúdo principal:**")
                    for i, content in enumerate(main_content, 1):
                        result_parts.append(
                            f"\n{i}. {content}{'...' if len(content) >= 400 else ''}"
                        )

            # Extração de links se solicitado
            if extract_links:
                logger.debug("Extraindo links...")
                links = soup.find_all("a", href=True)
                unique_links = []
                seen_urls = set()

                for link in links[:10]:  # Máximo 10 links
                    href = link.get("href")
                    text = link.get_text().strip()

                    if href and text and len(text) > 3:
                        # Converte links relativos em absolutos
                        full_url = urljoin(url, href)
                        if full_url not in seen_urls and full_url.startswith(
                            ("http://", "https://")
                        ):
                            seen_urls.add(full_url)
                            unique_links.append(f"• [{text[:50]}]({full_url})")

                if unique_links:
                    result_parts.append("\n🔗 **Links encontrados:**")
                    result_parts.extend(unique_links)

            if not result_parts:
                return "Não foi possível extrair conteúdo significativo da página."

            # Adiciona informações da fonte
            result_parts.append(f"\n🌐 **Fonte:** {url}")

            final_result = "\n".join(result_parts)

            # Limita o tamanho total da resposta
            if len(final_result) > 2000:
                final_result = final_result[:2000] + "\n\n[Conteúdo truncado...]"

            logger.info(
                f"Web Scraping concluído - URL: {url}, Tamanho: {len(final_result)} chars"
            )
            return final_result

        except requests.RequestException as e:
            track_error("connection_error", "web_scraping")
            logger.error(f"Erro de conexão no Web Scraping: {e}")
            return f"Erro de conexão ao acessar a página: {str(e)}"
        except Exception as e:
            track_error("web_scraping_error", "web_scraping")
            logger.error(f"Erro no Web Scraping: {e}", exc_info=True)
            return f"Erro ao extrair informações da página: {str(e)}"

    async def _arun(
        self, url: str, selector: str = "", extract_links: bool = False
    ) -> str:
        """Versão assíncrona do web scraping."""
        return self._run(url, selector, extract_links)


class SQLSelectInput(BaseModel):
    """Input para a ferramenta SQL SELECT."""

    query: str = Field(
        description="Query SQL SELECT para executar (use %s para parâmetros)"
    )
    params: List = Field(
        default=[],
        description="Lista de parâmetros para a query (substitui %s na ordem)",
    )


class SQLSelectTool(BaseTool):
    """Ferramenta para executar queries SELECT no banco de dados PostgreSQL."""

    name: str = "sql_select"
    description: str = """
    Realiza uma query no Postgres para buscar informações sobre as tabelas do banco de dados.
    
    Só pode realizar operações de busca (SELECT), não é permitido a geração de qualquer operação de escrita.
    
    Tabelas disponíveis:
    
    sensors_sensordata:
    - id (bigint): ID único do registro
    - timestamp (timestamp with time zone): Data/hora da leitura
    - umidade (double precision): Umidade do solo (%)
    - condutividade (double precision): Condutividade elétrica (µS/cm)
    - temperatura (double precision): Temperatura (°C)
    - ph (double precision): pH do solo
    - nitrogenio (double precision): Nitrogênio (ppm)
    - fosforo (double precision): Fósforo (ppm)
    - potassio (double precision): Potássio (ppm)
    - salinidade (double precision): Salinidade (ppm)
    - tds (double precision): Total de sólidos dissolvidos (ppm)
    
    IMPORTANTE: 
    - Apenas queries SELECT são permitidas por motivos de segurança
    - Todas operações retornam um máximo de 50 itens
    - Use %s para parâmetros e forneça a lista de valores no campo params
    
    Exemplos de uso:
    - query: "SELECT timestamp, temperatura, umidade FROM sensors_sensordata WHERE timestamp > %s", params: ["2025-01-01"]
    - query: "SELECT COUNT(*) FROM sensors_sensordata WHERE ph BETWEEN %s AND %s", params: [6.0, 8.0]
    """
    args_schema: Type[BaseModel] = SQLSelectInput

    def _validate_query(self, query: str) -> bool:
        """Valida se a query é segura e é apenas um SELECT."""
        # Remove espaços e converte para minúsculo
        clean_query = query.strip().lower()

        # Verifica se começa com SELECT
        if not clean_query.startswith("select"):
            return False

        # Lista de palavras proibidas que podem ser perigosas
        forbidden_keywords = [
            "insert",
            "update",
            "delete",
            "drop",
            "create",
            "alter",
            "truncate",
            "exec",
            "execute",
            "sp_",
            "xp_",
            "--",
            ";--",
            "into outfile",
            "load_file",
            "information_schema",
            "pg_",
            "current_setting",
            "set ",
            "show ",
            "copy ",
            "\\",
            "pg_read_file",
            "pg_ls_dir",
        ]

        # Verifica se contém palavras proibidas usando any() para melhor performance
        if any(keyword in clean_query for keyword in forbidden_keywords):
            return False

        # Validação adicional: não permitir múltiplas queries (SQL injection)
        if clean_query.count(";") > 1:
            return False

        # Não permitir UNION sem ser em subquery controlada
        if "union" in clean_query and not ("(" in clean_query and ")" in clean_query):
            return False

        return True

    def _format_results(self, results: List[tuple], columns: List[str]) -> str:
        """Formata os resultados da query em uma string legível."""
        if not results:
            return "Nenhum resultado encontrado."

        # Para exibição, limita a 20 resultados para não sobrecarregar a resposta
        max_display = 20
        limited_results = results[:max_display]

        # Cabeçalho
        header = " | ".join(columns)
        separator = "-" * len(header)
        formatted_lines = [header, separator]

        # Resultados
        for row in limited_results:
            row_str = " | ".join(
                str(value) if value is not None else "NULL" for value in row
            )
            formatted_lines.append(row_str)

        # Informações sobre os resultados
        total_count = len(results)
        if total_count > max_display:
            formatted_lines.append(
                f"\n📊 Mostrando {max_display} de {total_count} resultado(s)"
            )
        else:
            formatted_lines.append(f"\n📊 Total: {total_count} resultado(s)")

        return "\n".join(formatted_lines)

    def _add_limit_to_query(self, query: str) -> str:
        """Adiciona LIMIT 50 à query se não tiver LIMIT especificado."""
        clean_query = query.strip().lower()

        # Se já tem LIMIT, não adiciona outro
        if "limit" in clean_query:
            return query

        # Se é uma query de COUNT, não adiciona LIMIT
        if clean_query.startswith("select count("):
            return query

        # Adiciona LIMIT 50
        return f"{query.rstrip(';')} LIMIT 50"

    def _execute_query_sync(self, final_query: str, params: List) -> tuple:
        """Executa a query de forma síncrona e retorna os resultados e colunas."""
        logger.debug("SQL Select Tool - Executando query no banco de dados...")
        with connection.cursor() as cursor:
            if params:
                logger.debug(f"SQL Select Tool - Executando com parâmetros: {params}")
                cursor.execute(final_query, params)
            else:
                logger.debug("SQL Select Tool - Executando sem parâmetros")
                cursor.execute(final_query)

            results = cursor.fetchall()
            logger.info(
                f"SQL Select Tool - Query executada com sucesso, {len(results)} registros retornados"
            )

            # Obtém os nomes das colunas
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            logger.debug(f"SQL Select Tool - Colunas retornadas: {columns}")

            return results, columns

    def _run(self, query: str, params: List = None) -> str:
        """Executa a query SQL e retorna os resultados."""
        if params is None:
            params = []

        # Log da query e parâmetros recebidos
        logger.info(f"SQL Select Tool - Query recebida: {query}")
        logger.info(f"SQL Select Tool - Parâmetros: {params}")

        try:
            # Valida a query
            if not self._validate_query(query):
                logger.warning(
                    f"SQL Select Tool - Query rejeitada por segurança: {query}"
                )
                return "Erro: Apenas queries SELECT são permitidas. Query rejeitada por motivos de segurança."

            # Adiciona LIMIT 50 se necessário
            final_query = self._add_limit_to_query(query)

            # Log da query final se foi modificada
            if final_query != query:
                logger.info(f"SQL Select Tool - Query modificada para: {final_query}")

            # Sempre tenta execução direta primeiro, se falhar usa thread
            try:
                logger.debug("SQL Select Tool - Tentando execução direta")
                results, columns = self._execute_query_sync(final_query, params)
            except Exception as sync_error:
                if "async context" in str(sync_error):
                    logger.debug(
                        "SQL Select Tool - Contexto assíncrono detectado, executando em thread"
                    )
                    # Força execução em thread separada quando em contexto assíncrono
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            self._execute_query_sync, final_query, params
                        )
                        results, columns = future.result()
                else:
                    # Re-lança outros erros
                    raise sync_error

            # Adiciona informação sobre o limite aplicado
            result_text = self._format_results(results, columns)
            if "LIMIT 50" in final_query and final_query != query:
                result_text += "\n\n📝 Nota: LIMIT 50 foi aplicado automaticamente para otimizar a performance."

            logger.info(
                f"SQL Select Tool - Resultado formatado com sucesso ({len(result_text)} caracteres)"
            )
            return result_text

        except Exception as e:
            logger.error(f"SQL Select Tool - Erro ao executar query: {query}")
            logger.error(f"SQL Select Tool - Parâmetros usados: {params}")
            logger.error(f"SQL Select Tool - Erro detalhado: {str(e)}", exc_info=True)
            track_error("sql_query_error", "sql_select_tool")
            return f"Erro ao executar query: {str(e)}"

    async def _arun(self, query: str, params: List = None) -> str:
        """Versão assíncrona da execução."""
        if params is None:
            params = []

        # Log da query e parâmetros recebidos
        logger.info(f"SQL Select Tool - Query recebida: {query}")
        logger.info(f"SQL Select Tool - Parâmetros: {params}")

        try:
            # Valida a query
            if not self._validate_query(query):
                logger.warning(
                    f"SQL Select Tool - Query rejeitada por segurança: {query}"
                )
                return "Erro: Apenas queries SELECT são permitidas. Query rejeitada por motivos de segurança."

            # Adiciona LIMIT 50 se necessário
            final_query = self._add_limit_to_query(query)

            # Log da query final se foi modificada
            if final_query != query:
                logger.info(f"SQL Select Tool - Query modificada para: {final_query}")

            # Executa a query de forma assíncrona
            results, columns = await sync_to_async(
                self._execute_query_sync, thread_sensitive=True
            )(final_query, params)

            # Adiciona informação sobre o limite aplicado
            result_text = self._format_results(results, columns)
            if "LIMIT 50" in final_query and final_query != query:
                result_text += "\n\n📝 Nota: LIMIT 50 foi aplicado automaticamente para otimizar a performance."

            logger.info(
                f"SQL Select Tool - Resultado formatado com sucesso ({len(result_text)} caracteres)"
            )
            return result_text

        except Exception as e:
            logger.error(f"SQL Select Tool - Erro ao executar query: {query}")
            logger.error(f"SQL Select Tool - Parâmetros usados: {params}")
            logger.error(f"SQL Select Tool - Erro detalhado: {str(e)}", exc_info=True)
            track_error("sql_query_error", "sql_select_tool")
            return f"Erro ao executar query: {str(e)}"


def get_tools() -> List[BaseTool]:
    """Retorna a lista de ferramentas disponíveis."""
    return [RAGSearchTool(), WeatherTool(), WebScrapingTool(), SQLSelectTool()]
