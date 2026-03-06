# Frontend — Sistema de Monitoramento Agrícola 🌱

Este diretório contém a aplicação **frontend** do sistema de monitoramento agrícola baseado em **IoT e Inteligência Artificial**, responsável pela interface do usuário, configurações dos atributos dos sensores, alertas e interação com os serviços de backend e IA.

A aplicação foi desenvolvida utilizando **React + Vite + TypeScript**, com componentes modernos baseados em **Shadcn UI** e **Radix UI**, além de estilização com **TailwindCSS**.

---

# Stack Tecnológica

## Frontend

| Tecnologia           | Versão  | Descrição                                         |
| -------------------- | ------- | ------------------------------------------------- |
| React                | 18.3.1  | Biblioteca principal para construção da interface |
| Vite                 | 5.4.20  | Bundler e servidor de desenvolvimento             |
| TypeScript           | 5.8.3   | Tipagem estática para maior segurança no código   |
| TailwindCSS          | 3.4.17  | Framework de estilização utilitária               |
| React Router DOM     | 6.30.1  | Gerenciamento de rotas da aplicação               |
| TanStack React Query | 5.83.0  | Gerenciamento de estado e requisições assíncronas |
| React Hook Form      | 7.61.1  | Gerenciamento de formulários                      |
| Zod                  | 3.25.76 | Validação de dados                                |
| Recharts             | 2.15.4  | Criação de gráficos para visualização de dados    |
| Shadcn UI            | latest  | Biblioteca de componentes baseada em Radix UI     |
| Radix UI             | latest  | Componentes acessíveis e desacoplados             |

---

# Infraestrutura

A aplicação frontend pode ser executada em ambiente de desenvolvimento local ou em container utilizando **Docker**.

Componentes principais de infraestrutura:

* **Node.js**
* **Docker**
* **Nginx** (para servir a aplicação em produção)

Arquivos relacionados:

* `Dockerfile`
* `docker-compose.yaml`
* `nginx.conf`

---

# Tecnologias e Dependências

## Dependências principais

As dependências principais utilizadas no projeto incluem:

| Tecnologia           | Versão  | Propósito no sistema agrícola           |
| -------------------- | ------- | --------------------------------------- |
| React                | 18.3.1  | Construção da interface da aplicação    |
| React Router DOM     | 6.30.1  | Navegação entre páginas                 |
| TanStack React Query | 5.83.0  | Gerenciamento de dados vindos da API    |
| React Hook Form      | 7.61.1  | Manipulação de formulários              |
| Zod                  | 3.25.76 | Validação de dados de entrada           |
| Recharts             | 2.15.4  | Visualização gráfica de dados agrícolas |
| TailwindCSS          | 3.4.17  | Estilização responsiva                  |
| Lucide React         | 0.462.0 | Biblioteca de ícones                    |

---

# Dependências de Desenvolvimento

Ferramentas utilizadas para desenvolvimento e qualidade do código:

- **Vite** ^5.4.20 - Bundler e dev server
- **TypeScript** ^5.8.3 - TTipagem estática
- **ESLint** ^9.32.0- Padronização e análise de código
- **PostCSS** ^8.5.6 - Processamento de CSS
- **Autoprefixer** ^10.4.21 - CCompatibilidade de CSS entre navegadores
- **TailwindCSS** ^3.4.17 - Framework de CSS

---

# Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

* **Node.js 18+**
* **NPM ou Yarn**
* **Git**

Opcional para ambiente containerizado:

* **Docker**
* **Docker Compose**

---

# Instalação e Configuração

## 1 — Clonar o repositório

```bash
git clone https://github.com/samrqs/tcc
cd tcc
cd frontend
```

---

## 2 — Instalar dependências

```bash
npm install
```

ou

```bash
yarn install
```

---

# Configuração de Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`.

Exemplo:

```env
VITE_OPENAI_API_KEY=

VITE_OPENAI_MODEL_NAME="gpt-4o-mini"

VITE_OPENAI_MODEL_TEMPERATURE=0

VITE_API_BASE_URL=

VITE_WHATSAPP_PHONE_NUMBER=
```

Descrição das variáveis:

| Variável                      | Descrição                         |
| ----------------------------- | --------------------------------- |
| VITE_OPENAI_API_KEY           | Chave de acesso à API da OpenAI   |
| VITE_OPENAI_MODEL_NAME        | Modelo utilizado pelo chatbot     |
| VITE_OPENAI_MODEL_TEMPERATURE | Nível de criatividade da IA       |
| VITE_API_BASE_URL             | URL da API backend                |
| VITE_WHATSAPP_PHONE_NUMBER    | Número de integração com WhatsApp |

---

# Executar o Projeto

## Ambiente de Desenvolvimento

```bash
npm run dev
```

A aplicação será iniciada em:

```
http://localhost:5173
```

---

# Build para Produção

```bash
npm run build
```

Os arquivos compilados serão gerados na pasta:

```
dist/
```

---

# Visualizar Build

```bash
npm run preview
```

---

# Estrutura do Projeto

```
frontend
 ├── src
 │   ├── components
 │   ├── pages
 │   ├── hooks
 │   ├── services
 │   ├── utils
 │   └── styles
 │
 ├── public
 ├── Dockerfile
 ├── docker-compose.yaml
 ├── nginx.conf
 ├── package.json
 └── vite.config.ts
```

---

# Scripts Disponíveis

| Script          | Descrição                                |
| --------------- | ---------------------------------------- |
| npm run dev     | Inicia o servidor de desenvolvimento     |
| npm run build   | Gera build de produção                   |
| npm run preview | Executa preview da build                 |
| npm run lint    | Executa verificação de código com ESLint |

---

# Docker (Opcional)

Para executar utilizando Docker:

```bash
docker-compose up --build
```

A aplicação será disponibilizada conforme configuração do `docker-compose.yaml`.

---

# Licença

Projeto acadêmico desenvolvido para **Trabalho de Conclusão de Curso (TCC)**.
