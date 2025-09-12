from langchain_core.prompts import ChatPromptTemplate

template = "Você é um atendente de IA, contexto:{context}, pergunta:{question}"
prompt = ChatPromptTemplate.from_template(template)
