/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_OPENAI_API_KEY: string;
  readonly VITE_OPENAI_MODEL_NAME: string;
  readonly VITE_OPENAI_MODEL_TEMPERATURE: string;
  readonly VITE_WHATSAPP_PHONE_NUMBER: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
