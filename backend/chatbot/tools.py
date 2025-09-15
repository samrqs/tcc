import logging
from typing import List, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

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
        try:
            vectorstore = get_vectorstore()
            retriever = vectorstore.as_retriever(search_kwargs={"k": k})

            # Busca documentos relevantes
            docs = retriever.get_relevant_documents(query)

            if not docs:
                return "Não foram encontradas informações relevantes nos documentos."

            # Formata as informações encontradas
            results = []
            for i, doc in enumerate(docs, 1):
                content = doc.page_content.strip()
                if len(content) > 500:
                    content = content[:500] + "..."
                results.append(f"Resultado {i}:\n{content}\n")

            if not results:
                return "Não foram encontradas informações relevantes nos documentos."

            logger.info(f"RAG Search - Query: {query}, Results Found: {len(results)}")

            return "\n\n".join(results)

        except Exception as e:
            return f"Erro ao buscar nos documentos: {str(e)}"

    async def _arun(self, query: str, k: int = 3) -> str:
        """Versão assíncrona da busca."""
        return self._run(query, k)


def get_tools() -> List[BaseTool]:
    """Retorna a lista de ferramentas disponíveis."""
    return [RAGSearchTool()]
