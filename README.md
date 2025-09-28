# 🌾 TCC - Assistente Técnico Agrícola com IA

Sistema inteligente de assistência técnica agrícola que integra **WhatsApp**, **sensores IoT**, **Retrieval-Augmented Generation (RAG)** e **OpenAI** para fornecer orientações personalizadas para pequenos agricultores e produtores familiares.

## 🌟 Características Principais

- **🌾 Assistência Agrícola Especializada**: Orientações técnicas para cultivos, manejo e práticas sustentáveis
- **💬 Integração WhatsApp**: Acesso via mensagem para agricultores no campo
- **🧠 IA Agrícola**: OpenAI GPT-4o-mini com conhecimento técnico especializado
- **🌱 Sensores IoT**: Monitoramento em tempo real de solo, clima e nutrientes
- **📚 Base de Conhecimento RAG**: Documentos técnicos, manuais e boas práticas
- **🌤️ Dados Meteorológicos**: Informações climáticas via OpenWeatherMap
- **🌐 Web Scraping**: Cotações de commodities e notícias do agronegócio
- **💾 Histórico Inteligente**: Memória contextualizada por propriedade
- **🐳 Deploy Robusto**: Containerização completa para produção
- **⚡ Performance Otimizada**: Cache Redis e consultas SQL eficientes

## 🏗️ Arquitetura do Sistema

### Stack Tecnológica

**Backend:**

- **Django 5.2.6** - Framework web principal
- **Django REST Framework** - API REST para webhooks e sensores
- **LangChain** - Framework para agentes com ferramentas
- **OpenAI GPT-4o-mini** - Modelo de linguagem especializado
- **ChromaDB** - Vector database para RAG com OpenAI Embeddings
- **PostgreSQL** - Dados dos sensores IoT e histórico
- **Redis** - Cache, sessões e buffer de mensagens
- **BeautifulSoup** - Web scraping para dados de mercado
- **OpenWeatherMap API** - Dados meteorológicos em tempo real

**Infrastructure:**

- **Docker & Docker Compose** - Containerização
- **EvolutionAPI** - Gateway WhatsApp
- **Gunicorn** - Servidor WSGI

### Arquitetura TCC

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   EvolutionAPI  │    │   Django API    │
│   Agricultor    │◄──►│   Gateway       │◄──►│   TCC           │
│                 │    │                 │    │   ┌─────────┐   │
└─────────────────┘    └─────────────────┘    │   │ Agente  │   │
                                              │   │  + 4    │   │
┌─────────────────┐    ┌─────────────────┐    │   │Ferramen.│   │
│   Sensores IoT  │    │  OpenWeatherMap │    │   └─────────┘   │
│ Solo/Clima/NPK  │◄──►│   API Clima     │◄──►│   ┌─────────┐   │
│                 │    │                 │    │   │Histórico│   │
└─────────────────┘    └─────────────────┘    │   │Sensores │   │
                                              │   └─────────┘   │
┌─────────────────┐    ┌─────────────────┐    └─────────────────┘
│   PostgreSQL    │    │     Redis       │           ▲    ▲
│   Dados IoT     │◄──►│   Cache +       │◄──────────┘    │
│                 │    │   Sessões       │                │
└─────────────────┘    └─────────────────┘                │
                                                          │
┌─────────────────┐    ┌─────────────────┐                │
│   ChromaDB      │    │  Web Scraping   │◄───────────────┘
│ Base Conhecimen │◄──►│ Cotações/News   │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🚀 Tecnologias e Dependências

### Dependências Principais

| Tecnologia            | Versão                  | Propósito Agrícola               |
| --------------------- | ----------------------- | -------------------------------- |
| Python                | ≥3.11,<3.15             | Runtime principal                |
| Django                | ^5.2.6                  | Framework web + sensores IoT     |
| Django REST Framework | ^3.16.1                 | API REST para webhooks           |
| OpenAI                | ^1.107.0                | TCC - IA agrícola                |
| LangChain             | ^0.3.27                 | Agente com ferramentas           |
| LangChain-OpenAI      | ^0.3.33                 | Integração GPT-4o-mini           |
| LangChain-Chroma      | ^0.2.6                  | RAG - base conhecimento agrícola |
| BeautifulSoup4        | ^4.12.3                 | Web scraping - cotações/notícias |
| Requests              | ^2.32.3                 | HTTP client - APIs externas      |
| Redis                 | ^6.4.0                  | Cache + buffer mensagens         |
| PostgreSQL            | psycopg2-binary ^2.9.10 | Dados sensores + histórico       |
| Python-decouple       | ^3.8                    | Configuração segura              |

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

# Prompt (personalize conforme necessário)
AI_SYSTEM_PROMPT='Você é um assistente técnico agrícola virtual...'  # Ver .env.example para o prompt completo
```

### 3. Prepare a Base de Conhecimento Agrícola

Adicione documentos técnicos na pasta `rag_files/`:

```bash
rag_files/
├── manual_cultivo_milho.pdf
├── controle_pragas_soja.pdf
├── boas_praticas_irrigacao.txt
├── tabela_adubacao_npk.csv
└── calendario_agricola.txt
```

**Tipos de Documentos Recomendados:**

- **Manuais Técnicos** (PDF) - Cultivo, manejo, equipamentos
- **Guias de Pragas** (PDF/TXT) - Identificação e controle
- **Tabelas Técnicas** (CSV) - Adubação, espaçamento, doses
- **Calendários Agrícolas** (TXT) - Épocas de plantio/colheita
- **Boletins Técnicos** (PDF) - Pesquisas, novas variedades

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

## 🛠️ Ferramentas do TCC

O TCC possui 4 ferramentas especializadas para auxiliar os agricultores:

### 1. 📚 `rag_search` - Base de Conhecimento Agrícola

**Tecnologia**: ChromaDB + OpenAI Embeddings  
**Uso**: Consulta documentos técnicos, manuais e boas práticas agrícolas

**Exemplos:**

- "Qual o espaçamento ideal para plantio de milho safrinha?"
- "Como identificar e controlar a lagarta-do-cartucho no milho?"
- "Técnicas de irrigação por gotejamento para hortaliças"

### 2. 📊 `sql_select` - Dados dos Sensores IoT

**Tecnologia**: PostgreSQL + Django ORM  
**Uso**: Consulta histórico de sensores de solo, clima e nutrientes

**Dados Disponíveis:**

- Umidade do solo (%), temperatura (°C), pH
- NPK - Nitrogênio, Fósforo, Potássio (ppm)
- Condutividade elétrica, salinidade, TDS

**Exemplos:**

- "Qual foi a média de umidade do solo na semana passada?"
- "Mostre o pH do solo nos últimos 7 dias"
- "Níveis de NPK desta semana comparado com o mês anterior"

### 3. 🌤️ `weather_search` - Dados Meteorológicos

**Tecnologia**: OpenWeatherMap API  
**Uso**: Condições climáticas para decisões agrícolas

**Exemplos:**

- "Condições de vento para aplicação de defensivos hoje?"
- "Umidade relativa ideal para plantio de hortaliças?"
- "Previsão de chuva - devo adiar a colheita?"

### 4. 🌐 `web_scraping` - Mercado e Cotações

**Tecnologia**: BeautifulSoup + Requests  
**Uso**: Preços atuais e notícias do agronegócio

**Exemplos:**

- "Preço atual da saca de milho na CEPEA/ESALQ"
- "Cotação da arroba do boi gordo no mercado"
- "Notícias sobre nova cultivar de soja resistente à seca"

## 🎯 Uso do Sistema

### API Endpoints

| Endpoint                | Método | Descrição                       |
| ----------------------- | ------ | ------------------------------- |
| `/api/chatbot/webhook/` | POST   | Webhook para mensagens WhatsApp |
| `/api/sensors/webhook/` | POST   | Webhook para sensores (futuro)  |
| `/admin/`               | GET    | Painel administrativo Django    |
| `/api/schema/`          | GET    | Documentação OpenAPI            |
| `/ht/`                  | GET    | Health check dos serviços       |

### Fluxo de Funcionamento do TCC

1. **📱 Agricultor no WhatsApp** → Envia dúvida técnica
2. **🔗 EvolutionAPI** → Recebe e encaminha via webhook
3. **🤖 TCC Processa:**
   - Analisa contexto da pergunta
   - Identifica ferramentas necessárias
   - Executa consultas apropriadas:
     - 📚 RAG → Busca conhecimento técnico
     - 📊 SQL → Consulta sensores IoT
     - 🌤️ Weather → Dados meteorológicos
     - 🌐 Scraping → Cotações/notícias
4. **🧠 OpenAI** → Gera resposta técnica personalizada
5. **💾 Redis** → Salva histórico da propriedade
6. **📤 Resposta** → Enviada via WhatsApp ao agricultor

### Processamento da Base de Conhecimento

Os documentos agrícolas são processados e otimizados para busca:

- **Chunking**: 1000 caracteres com sobreposição de 200
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vectorstore**: ChromaDB para busca semântica
- **Indexação**: Automática ao reiniciar o sistema
- **Busca**: Similaridade vetorial + contexto agrícola

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
backend/
├── 📁 chatbot/              # TCC - Módulo principal
│   ├── chains.py           # Agente LangChain + Ferramentas
│   ├── config.py          # Configurações (incluindo AI_SYSTEM_PROMPT)
│   ├── evolution_api.py   # Cliente WhatsApp
│   ├── memory.py          # Histórico por propriedade
│   ├── prompts.py         # Prompt do TCC
│   ├── tools.py           # 4 Ferramentas (RAG, SQL, Weather, Scraping)
│   ├── vectorstore.py     # ChromaDB - Base conhecimento
│   └── views.py           # Webhooks e API
├── 📁 sensors/             # Módulo sensores IoT
│   ├── models.py          # Modelo dados sensores
│   └── views.py           # Webhook sensores
├── 📁 core/               # Django core settings
├── 📁 rag_files/          # 📚 Documentos técnicos agrícolas
│   └── processed/         # Documentos processados
├── 📁 vectorstore/        # 🗄️ ChromaDB storage
├── docker-compose.yml     # Containers (Django + Redis + PostgreSQL)
├── Dockerfile            # Imagem Python otimizada
├── pyproject.toml        # Poetry - dependências
└── .env.example          # Variáveis (incluindo prompt personalizado)
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

**❌ "TCC não encontra informações técnicas"**

```bash
# Verifique se há documentos agrícolas processados
ls -la rag_files/processed/

# Adicione mais documentos técnicos em rag_files/
# Reinicie o container para reprocessar
docker-compose restart api
```

**❌ "Dados dos sensores não aparecem"**

```bash
# Verifique se há dados na tabela sensors_sensordata
docker-compose exec db psql -U postgres -d tcc -c "SELECT COUNT(*) FROM sensors_sensordata;"

# Teste a ferramenta SQL diretamente no Django shell
docker-compose exec api python manage.py shell
>>> from chatbot.tools import SQLSelectTool
>>> tool = SQLSelectTool()
>>> tool._run("SELECT COUNT(*) FROM sensors_sensordata")
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
curl http://localhost:8000/ht/
```

## 📊 Monitoramento

### Health Checks Disponíveis

- **Database**: Conectividade PostgreSQL
- **Cache**: Conectividade Redis
- **Migrations**: Status das migrações Django

### Métricas de Performance

O sistema inclui health checks em:

```
http://localhost:8000/ht/
```

## 🌱 Customização do TCC

### Personalizando o Prompt

Edite a variável `AI_SYSTEM_PROMPT` no arquivo `.env` para:

- Adaptar a linguagem para sua região
- Incluir cultivos específicos da sua área
- Personalizar exemplos para seus clientes
- Adicionar informações sobre sua propriedade

### Adicionando Novas Ferramentas

1. **Crie uma nova ferramenta** em `chatbot/tools.py`:

```python
class MinhaFerramentaTool(BaseTool):
    name: str = "minha_ferramenta"
    description: str = "Descrição detalhada..."

    def _run(self, parametros) -> str:
        # Sua lógica aqui
        return resultado
```

2. **Adicione à lista** em `get_tools()`:

```python
def get_tools() -> List[BaseTool]:
    return [
        RAGSearchTool(),
        WeatherTool(),
        WebScrapingTool(),
        SQLSelectTool(),
        MinhaFerramentaTool()  # Nova ferramenta
    ]
```

### Expandindo a Base de Dados

Para adicionar novos tipos de sensores:

1. **Modifique o modelo** em `sensors/models.py`
2. **Crie migrations**: `python manage.py makemigrations`
3. **Aplique**: `python manage.py migrate`
4. **Atualize** a descrição da ferramenta `sql_select`
