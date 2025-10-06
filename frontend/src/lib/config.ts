// Configurações da aplicação
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL,
  },
  openai: {
    apiKey: import.meta.env.VITE_OPENAI_API_KEY,
    modelName: import.meta.env.VITE_OPENAI_MODEL_NAME,
    temperature: Number(import.meta.env.VITE_OPENAI_MODEL_TEMPERATURE),
  },
  whatsapp: {
    phoneNumber: import.meta.env.VITE_WHATSAPP_PHONE_NUMBER,
  },
} as const;
