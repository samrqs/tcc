# 🤖 TCC - Chatbot com IA e WhatsApp

Sistema de chatbot inteligente que integra **WhatsApp**, **Retrieval-Augmented Generation (RAG)** e **OpenAI** para fornecer respostas contextualizadas baseadas em documentos personalizados.

## 🌟 Características Principais

- **🔗 Integração WhatsApp**: Conexão nativa via EvolutionAPI
- **🧠 IA Conversacional**: Powered by OpenAI GPT-4o-mini
- **📚 RAG (Retrieval-Augmented Generation)**: Busca inteligente em documentos
- **💾 Memória de Conversas**: Histórico contextualizado por sessão
- **📄 Suporte Multi-formato**: PDF, TXT e CSV
- **🐳 Deploy Docker**: Containerização completa
- **⚡ Cache Redis**: Performance otimizada
- **📊 Health Checks**: Monitoramento de saúde dos serviços
- **🔧 API RESTful**: Endpoints documentados com OpenAPI

## 🏗️ Arquitetura do Sistema

### Stack Tecnológica

**Backend:**

- **Django 5.2.6** - Framework web principal
- **Django REST Framework** - API REST
- **LangChain** - Framework para aplicações com LLM
- **OpenAI** - Modelo de linguagem
- **Chroma** - Vector database para embeddings
- **Redis** - Cache e sessões
- **PostgreSQL** - Banco de dados principal

**Infrastructure:**

- **Docker & Docker Compose** - Containerização
- **EvolutionAPI** - Gateway WhatsApp
- **Gunicorn** - Servidor WSGI

### Componentes

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   EvolutionAPI  │    │   Django API    │
│                 │◄──►│                 │◄──►│                 │
│                 │    │                 │    │   ┌─────────┐   │
└─────────────────┘    └─────────────────┘    │   │ Chatbot │   │
                                              │   │ Module  │   │
┌─────────────────┐    ┌─────────────────┐    │   └─────────┘   │
│   PostgreSQL    │    │     Redis       │    │   ┌─────────┐   │
│                 │◄──►│                 │◄──►│   │ Sensors │   │
│                 │    │                 │    │   │ Module  │   │
│                 │    │                 │    │   └─────────┘   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       ▲
                       ┌─────────────────┐             │
                       │   Chroma DB     │◄────────────┘
                       │  (Vectorstore)  │
                       └─────────────────┘
```

## 🚀 Tecnologias e Dependências

### Dependências Principais

| Tecnologia            | Versão                  | Propósito         |
| --------------------- | ----------------------- | ----------------- |
| Python                | ≥3.11,<3.15             | Runtime           |
| Django                | ^5.2.6                  | Framework web     |
| Django REST Framework | ^3.16.1                 | API REST          |
| OpenAI                | ^1.107.0                | Modelos de IA     |
| LangChain             | ^0.3.27                 | Framework LLM     |
| LangChain-OpenAI      | ^0.3.33                 | Integração OpenAI |
| LangChain-Chroma      | ^0.2.6                  | Vector database   |
| Redis                 | ^6.4.0                  | Cache e sessões   |
| PostgreSQL            | psycopg2-binary ^2.9.10 | Banco de dados    |
| FAISS-CPU             | ^1.12.0                 | Busca vetorial    |

### Dependências de Desenvolvimento

- **pytest** ^8.4.2 - Framework de testes
- **pytest-django** ^4.11.1 - Testes Django
- **pytest-cov** ^6.3.0 - Cobertura de testes

## 📋 Pré-requisitos

- **Docker** e **Docker Compose**
- **Git**
- **Chave da OpenAI API**
- **Instância EvolutionAPI configurada**

## 🛠️ Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/samrqs/tcc
cd tcc
cd backend
```

### 2. Configure as Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas chaves:

```bash
cp .env.example .env
```

**⚠️ Configurações Obrigatórias:**

Edite o arquivo `.env` e configure:

```bash
# Chaves de API
OPENAI_API_KEY=sua_chave_openai_aqui

# EvolutionAPI
EVOLUTION_INSTANCE_NAME=chatbot  # Deve ser idêntico ao nome da instância no painel
AUTHENTICATION_API_KEY=sua_chave_auth_aqui
```

### 3. Prepare os Documentos RAG

Adicione seus documentos na pasta `rag_files/`:

```bash
rag_files/
├── documento1.pdf
├── perguntas_frequentes.txt
└── dados_produtos.csv
```

**Formatos suportados:**

- **PDF** - Documentos, manuais, relatórios
- **TXT** - Textos simples, FAQs
- **CSV** - Dados estruturados, planilhas

Os documentos serão automaticamente:

1. Processados e vetorizados
2. Movidos para `rag_files/processed/`
3. Indexados no Chroma DB

### 4. Inicie os Serviços

```bash
docker-compose up --build
```

**Serviços iniciados:**

- **🤖 EvolutionAPI**: `http://localhost:8080`
- **🐍 Django API**: `http://localhost:8000`
- **🗄️ PostgreSQL**: `localhost:5432`
- **⚡ Redis**: `localhost:6379`

### 5. Configure o WhatsApp

1. **Acesse o painel EvolutionAPI:**

   ```
   http://localhost:8080/manager
   ```

2. **Crie uma nova instância:**

   - Nome: `chatbot` (deve ser igual ao `EVOLUTION_INSTANCE_NAME`)
   - Configure conforme necessário

3. **Conecte ao WhatsApp:**

   - Escaneie o QR Code
   - Aguarde a conexão

4. **Configure o Webhook:**
   - URL: `http://api:8000/api/chatbot/webhook/`
   - Eventos: `MESSAGES_UPSERT`

## 🎯 Uso do Sistema

### API Endpoints

| Endpoint                | Método | Descrição                       |
| ----------------------- | ------ | ------------------------------- |
| `/api/chatbot/webhook/` | POST   | Webhook para mensagens WhatsApp |
| `/api/sensors/webhook/` | POST   | Webhook para sensores (futuro)  |
| `/admin/`               | GET    | Painel administrativo Django    |
| `/api/schema/`          | GET    | Documentação OpenAPI            |
| `/health/`              | GET    | Health check dos serviços       |

### Fluxo de Funcionamento

1. **📱 Mensagem WhatsApp** → EvolutionAPI recebe
2. **🔗 Webhook** → EvolutionAPI envia para Django
3. **🧠 Processamento IA:**
   - Contextualização da mensagem
   - Busca RAG nos documentos
   - Geração de resposta com OpenAI
4. **💾 Memória** → Histórico salvo no Redis
5. **📤 Resposta** → Enviada via EvolutionAPI → WhatsApp

### Estrutura dos Dados RAG

Os documentos são processados e divididos em chunks de:

- **Tamanho**: 1000 caracteres
- **Sobreposição**: 200 caracteres
- **Embeddings**: OpenAI text-embedding-ada-002

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
backend/
├── 📁 chatbot/              # Módulo principal do chatbot
│   ├── chains.py           # Chains LangChain
│   ├── config.py          # Configurações
│   ├── evolution_api.py   # Cliente EvolutionAPI
│   ├── memory.py          # Gestão de memória
│   ├── prompts.py         # Templates de prompts
│   ├── vectorstore.py     # Gestão Chroma DB
│   └── views.py           # Views da API
├── 📁 sensors/             # Módulo de sensores (futuro)
├── 📁 core/               # Configurações Django
├── 📁 rag_files/          # Documentos para RAG
│   └── processed/         # Documentos processados
├── 📁 vectorstore/        # Banco vetorial Chroma
├── docker-compose.yml     # Orquestração containers
├── Dockerfile            # Imagem Python
├── pyproject.toml        # Dependências Poetry
└── .env.example          # Template variáveis
```

### Comandos de Desenvolvimento

```bash
# Testes
docker-compose exec api python -m pytest

# Logs em tempo real
docker-compose logs -f api

# Shell Django
docker-compose exec api python manage.py shell

# Migrations
docker-compose exec api python manage.py makemigrations
docker-compose exec api python manage.py migrate

# Collectstatic
docker-compose exec api python manage.py collectstatic
```

### Adicionando Novos Documentos

1. Adicione arquivos em `rag_files/`
2. Reinicie o container:
   ```bash
   docker-compose restart api
   ```
3. Os documentos serão automaticamente processados

## 🚨 Solução de Problemas

### Problemas Comuns

**❌ "OpenAI API key not found"**

```bash
# Verifique se a chave está no .env
grep OPENAI_API_KEY .env
```

**❌ "Instance not found"**

- Verifique se `EVOLUTION_INSTANCE_NAME` no `.env` é igual ao nome no painel
- Confirme se a instância está conectada no painel EvolutionAPI

**❌ "Webhook not receiving messages"**

- Verifique se o webhook está configurado: `http://api:8000/api/chatbot/webhook/`
- Confirme se o evento `MESSAGES_UPSERT` está habilitado

**❌ "No documents found for RAG"**

```bash
# Verifique se há documentos processados
ls -la rag_files/processed/
```

### Logs e Debugging

```bash
# Logs do Django
docker-compose logs api

# Logs da EvolutionAPI
docker-compose logs evolution-api

# Logs completos
docker-compose logs

# Health check
curl http://localhost:8000/health/
```

## 📊 Monitoramento

### Health Checks Disponíveis

- **Database**: Conectividade PostgreSQL
- **Cache**: Conectividade Redis
- **Migrations**: Status das migrações Django

### Métricas de Performance

O sistema inclui health checks em:

```
http://localhost:8000/health/
```

---

**⭐ Se este projeto foi útil, considere dar uma estrela no repositório!**
