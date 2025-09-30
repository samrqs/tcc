import logging
import os
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import OPENAI_API_KEY, RAG_FILES_DIR, VECTOR_STORE_PATH

logger = logging.getLogger(__name__)


def load_documents_from_directory(directory):
    """Carrega documentos de um diretório específico sem movê-los"""
    docs = []

    if not os.path.exists(directory):
        return docs

    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith((".pdf", ".txt", ".csv"))
    ]

    for file in files:
        try:
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file)
            elif file.endswith(".txt"):
                loader = TextLoader(file, encoding="utf-8")
            elif file.endswith(".csv"):
                loader = CSVLoader(file)
            else:
                continue

            file_docs = loader.load()
            docs.extend(file_docs)
            logger.info(
                f"Carregado: {os.path.basename(file)} ({len(file_docs)} documentos)"
            )

        except Exception as e:
            logger.error(f"Erro ao carregar {file}: {e}")
            continue

    return docs


def load_documents():
    """Carrega documentos de ambas as pastas: RAG_FILES_DIR e processed"""
    all_docs = []

    # Carregar da pasta processed (arquivos já processados anteriormente)
    processed_dir = os.path.join(RAG_FILES_DIR, "processed")
    if os.path.exists(processed_dir):
        logger.info("Carregando documentos da pasta processed...")
        processed_docs = load_documents_from_directory(processed_dir)
        all_docs.extend(processed_docs)
        logger.info(f"Documentos da pasta processed: {len(processed_docs)}")

    # Carregar da pasta principal (novos arquivos)
    logger.info("Carregando documentos da pasta principal...")
    main_docs = load_documents_from_directory(RAG_FILES_DIR)
    all_docs.extend(main_docs)
    logger.info(f"Documentos da pasta principal: {len(main_docs)}")

    logger.info(f"Total de documentos carregados: {len(all_docs)}")
    return all_docs


def get_vectorstore():
    """Obtém o vectorstore, recriando se necessário"""
    try:
        # Primeiro tenta carregar vectorstore existente
        vectorstore = Chroma(
            embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            persist_directory=VECTOR_STORE_PATH,
        )

        # Verifica se tem documentos no vectorstore
        test_results = vectorstore.similarity_search("test", k=1)
        if test_results:
            logger.info("Vectorstore existente carregado")
            return vectorstore
        else:
            logger.info("Vectorstore vazio, recriando...")

    except Exception as e:
        logger.error(f"Erro ao carregar vectorstore existente: {e}")
        logger.info("Criando novo vectorstore...")

    # Carregar documentos e criar novo vectorstore
    docs = load_documents()
    if not docs:
        logger.warning("Nenhum documento encontrado para criar vectorstore")
        return Chroma(
            embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            persist_directory=VECTOR_STORE_PATH,
        )

    logger.info(f"Criando vectorstore com {len(docs)} documentos...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Chunks menores
        chunk_overlap=100,
    )
    splits = text_splitter.split_documents(docs)
    logger.info(f"Documentos divididos em {len(splits)} chunks")

    # Processar em lotes para evitar limite de tokens
    embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = Chroma(
        embedding_function=embedding_function,
        persist_directory=VECTOR_STORE_PATH,
    )

    batch_size = 50  # Processar 50 chunks por vez
    total_batches = (len(splits) + batch_size - 1) // batch_size

    for i in range(0, len(splits), batch_size):
        batch = splits[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        logger.debug(
            f"Processando lote {batch_num}/{total_batches} ({len(batch)} chunks)..."
        )

        try:
            # Adiciona o lote ao vectorstore
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            vectorstore.add_texts(texts=texts, metadatas=metadatas)

        except Exception as e:
            logger.error(f"Erro ao processar lote {batch_num}: {e}")
            continue

    logger.info("Vectorstore criado com sucesso!")
    return vectorstore
