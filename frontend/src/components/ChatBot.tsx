import { useAuth } from "@/hooks/use-auth";
import { config } from "@/lib/config";
import {
  Loader2,
  MessageCircle,
  MessageSquare,
  Send,
  UserPlus,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Input } from "./ui/input";

// Função para formatar número do WhatsApp
const formatWhatsAppNumber = (phoneNumber: string) => {
  // Remove todos os caracteres não numéricos
  const cleaned = phoneNumber.replace(/\D/g, "");
  if (cleaned.length >= 13) {
    return `+${cleaned.slice(0, 2)} ${cleaned.slice(2, 4)} ${cleaned.slice(
      4,
      9
    )}-${cleaned.slice(9)}`;
  }
  return phoneNumber;
};

type Message = {
  role: "user" | "assistant";
  content: string;
};

const MAX_QUESTIONS = 3; // limite de perguntas

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Olá! Sou seu assistente de agricultura familiar. Como posso ajudar com questões sobre solo, plantio ou cultivo?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [isLimitReached, setIsLimitReached] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Carrega o contador da sessão na inicialização
  useEffect(() => {
    const savedQuestionCount = sessionStorage.getItem("chatbot_question_count");
    const savedIsLimitReached = sessionStorage.getItem("chatbot_limit_reached");

    if (savedQuestionCount) {
      const count = parseInt(savedQuestionCount, 10);
      setQuestionCount(count);
      setIsLimitReached(
        count >= MAX_QUESTIONS || savedIsLimitReached === "true"
      );
    }
  }, []);

  // Salva o contador na sessão sempre que mudar
  useEffect(() => {
    sessionStorage.setItem("chatbot_question_count", questionCount.toString());
    sessionStorage.setItem("chatbot_limit_reached", isLimitReached.toString());
  }, [questionCount, isLimitReached]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Verifica se atingiu o limite após cada pergunta
  useEffect(() => {
    if (questionCount >= MAX_QUESTIONS && !isLimitReached) {
      setIsLimitReached(true);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: user
            ? `Você atingiu o limite de perguntas do chatbot da web! 🌱\n\nPara ter acesso completo ao nosso assistente técnico agrícola com:\n\n📊 Dados de sensores IoT em tempo real\n🌤️ Informações meteorológicas\n📚 Base completa de conhecimento agrícola\n🌐 Cotações e notícias do agronegócio\n\n📱 Fale conosco no WhatsApp: ${formatWhatsAppNumber(
                config.whatsapp.phoneNumber
              )}`
            : `Você atingiu o limite de perguntas gratuitas! 🌱\n\nPara continuar usando nosso assistente de agricultura familiar, você pode:\n\n📱 Falar conosco no WhatsApp: ${formatWhatsAppNumber(
                config.whatsapp.phoneNumber
              )}\n✅ Criar uma conta gratuita`,
        },
      ]);
    }
  }, [questionCount, isLimitReached, user]);

  const streamChat = async (userMessage: Message) => {
    const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";
    const OPENAI_API_KEY = config.openai.apiKey;
    const OPENAI_MODEL = config.openai.modelName;

    if (!OPENAI_API_KEY) {
      toast.error("Chave da OpenAI não configurada");
      return;
    }

    try {
      const response = await fetch(OPENAI_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: OPENAI_MODEL,
          messages: [
            {
              role: "system",
              content:
                "Você é um assistente especializado em agricultura familiar e análise de solo. Forneça respostas **curtas, objetivas e práticas** sobre plantio, qualidade do solo, pH, nutrientes, irrigação e melhores práticas agrícolas. Use linguagem acessível para agricultores familiares. Foque em soluções sustentáveis e de baixo custo.",
            },
            ...messages,
            userMessage,
          ],
          stream: true,
          temperature: config.openai.temperature,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error?.message || "Erro ao processar mensagem"
        );
      }

      if (!response.body) throw new Error("Sem resposta do servidor");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      const updateAssistant = (chunk: string) => {
        assistantContent += chunk;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return prev.map((m, i) =>
              i === prev.length - 1 ? { ...m, content: assistantContent } : m
            );
          }
          return [...prev, { role: "assistant", content: assistantContent }];
        });
      };

      let done = false;
      let buffer = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        buffer += decoder.decode(value || new Uint8Array(), { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.slice(6).trim();
          if (jsonStr === "[DONE]") {
            done = true;
            break;
          }

          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) updateAssistant(content);
          } catch {
            // ignora erros de parse
          }
        }
      }

      // processa qualquer sobra no buffer
      if (buffer.trim()) {
        try {
          const parsed = JSON.parse(buffer);
          const content = parsed.choices?.[0]?.delta?.content;
          if (content) updateAssistant(content);
        } catch {
          // ignora erros de parse do buffer final
        }
      }
    } catch (error) {
      console.error("Erro no chat:", error);
      toast.error(
        error instanceof Error ? error.message : "Erro ao enviar mensagem"
      );
      setMessages((prev) => prev.slice(0, -1));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || isLimitReached) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      await streamChat(userMessage);
      // incrementa contador para todos os usuários
      setQuestionCount((prev) => prev + 1);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg bg-primary hover:bg-primary/90 z-50 p-0"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {isOpen && (
        <Card className="fixed bottom-6 right-6 w-[90vw] sm:w-96 h-[600px] flex flex-col shadow-2xl z-50 border-border">
          <div className="flex items-center justify-between p-4 border-b bg-primary text-white rounded-t-lg">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              <div>
                <h3 className="font-semibold">FarmerAssist</h3>
                {!isLimitReached && (
                  <p className="text-xs text-primary-foreground/80">
                    Perguntas: {questionCount}/{MAX_QUESTIONS}
                  </p>
                )}
                {isLimitReached && (
                  <p className="text-xs text-primary-foreground/80">
                    Use o WhatsApp para mais recursos ↓
                  </p>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 p-0 hover:bg-primary/80 text-white"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-card text-foreground border"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && !isLimitReached && (
              <div className="flex justify-start">
                <div className="bg-card border rounded-lg p-3">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {isLimitReached ? (
            <div className="p-4 border-t bg-background space-y-3">
              <div className="text-center text-sm text-muted-foreground mb-3">
                Limite de perguntas atingido
              </div>

              {user ? (
                <div className="space-y-3">
                  <div className="text-center text-xs text-muted-foreground">
                    <p className="font-medium text-primary mb-2">
                      💡 No WhatsApp você tem acesso a:
                    </p>
                    <ul className="text-left space-y-1">
                      <li>📊 Dados de sensores IoT em tempo real</li>
                      <li>🌤️ Informações meteorológicas detalhadas</li>
                      <li>📚 Base completa de conhecimento agrícola</li>
                      <li>🌐 Cotações e notícias do agronegócio</li>
                    </ul>
                  </div>
                  <Button
                    onClick={() =>
                      window.open(
                        `https://api.whatsapp.com/send?phone=${config.whatsapp.phoneNumber}`,
                        "_blank"
                      )
                    }
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Continuar no WhatsApp
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      onClick={() => navigate("/login")}
                      variant="outline"
                      className="w-full"
                    >
                      Entrar
                    </Button>
                    <Button
                      onClick={() => navigate("/register")}
                      className="w-full bg-primary hover:bg-primary/90"
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Criar Conta
                    </Button>
                  </div>
                  <Button
                    onClick={() =>
                      window.open(
                        `https://api.whatsapp.com/send?phone=${config.whatsapp.phoneNumber}`,
                        "_blank"
                      )
                    }
                    variant="outline"
                    className="w-full"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Falar no WhatsApp
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 border-t bg-background space-y-3">
              <form onSubmit={handleSubmit}>
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Digite sua pergunta..."
                    disabled={isLoading || isLimitReached}
                    className="flex-1"
                  />
                  <Button
                    type="submit"
                    size="sm"
                    disabled={isLoading || !input.trim() || isLimitReached}
                    className="bg-primary hover:bg-primary/90"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </form>
              {user && (
                <Button
                  onClick={() =>
                    window.open(
                      `https://api.whatsapp.com/send?phone=${config.whatsapp.phoneNumber}`,
                      "_blank"
                    )
                  }
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Continuar no WhatsApp
                </Button>
              )}
            </div>
          )}
        </Card>
      )}
    </>
  );
};

export default ChatBot;
