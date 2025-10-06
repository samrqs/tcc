import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { config } from "@/lib/config";
import { ArrowLeft, Eye, EyeOff, Leaf } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Register = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [ddi, setDdi] = useState("55");
  const [ddd, setDdd] = useState("11");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !name ||
      !email ||
      !ddi ||
      !ddd ||
      !phone ||
      !password ||
      !confirmPassword
    ) {
      toast.error("Todos os campos são obrigatórios");
      return;
    }

    if (ddi.length < 1 || ddd.length < 2 || phone.length < 8) {
      toast.error("Digite um número de telefone válido");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("As senhas não coincidem");
      return;
    }

    if (password.length < 6) {
      toast.error("A senha deve ter pelo menos 6 caracteres");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error("Digite um email válido");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${config.api.baseUrl}/users/register/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          phone: `${ddi}${ddd}${phone}`,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Conta criada com sucesso! Fazendo login...");

        // Fazer login automático após o cadastro
        const loginResult = await login(email, password);

        if (loginResult.success) {
          toast.success("Login realizado com sucesso!");
          navigate("/");
        } else {
          toast.error(
            "Conta criada, mas houve erro no login automático. Tente fazer login manualmente."
          );
          navigate("/login");
        }
      } else if (data.email && Array.isArray(data.email)) {
        // Erro de email já existe
        toast.error("Este email já está cadastrado.", {
          description: "Tente fazer login ou use outro email.",
          action: {
            label: "Fazer Login",
            onClick: () => navigate("/login"),
          },
        });
      } else if (data.phone && Array.isArray(data.phone)) {
        // Erro de telefone já existe
        toast.error("Este telefone já está cadastrado");
      } else if (data.password && Array.isArray(data.password)) {
        // Erro de senha
        toast.error(
          data.password[0] || "Erro na senha. Verifique os requisitos."
        );
      } else if (data.message) {
        // Mensagem de erro personalizada
        toast.error(data.message);
      } else if (data.detail) {
        // Mensagem de erro do Django
        toast.error(data.detail);
      } else {
        // Erro genérico
        toast.error(
          "Erro ao criar conta. Verifique os dados e tente novamente."
        );
      }
    } catch (error) {
      console.error("Erro ao registrar:", error);
      toast.error("Erro de conexão. Verifique sua internet e tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-xl border-0 bg-white/90 backdrop-blur-sm">
        <div className="text-center mb-8">
          <Link
            to="/"
            className="inline-flex items-center gap-2 mb-6 text-primary hover:text-primary/80 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar ao início
          </Link>

          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-3 bg-primary/10 rounded-lg">
              <Leaf className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Criar Conta
          </h1>
          <p className="text-muted-foreground text-sm">
            Crie sua conta no FarmerAssist para ter acesso ilimitado ao nosso
            assistente de agricultura familiar
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome Completo</Label>
            <Input
              id="name"
              type="text"
              placeholder="Seu nome completo"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isLoading}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label>Telefone</Label>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <Input
                  type="text"
                  placeholder="DDI"
                  value={ddi}
                  onChange={(e) => setDdi(e.target.value.replace(/\D/g, ""))}
                  disabled={isLoading}
                  className="w-full text-center"
                  maxLength={3}
                />
              </div>
              <div>
                <Input
                  type="text"
                  placeholder="DDD"
                  value={ddd}
                  onChange={(e) => setDdd(e.target.value.replace(/\D/g, ""))}
                  disabled={isLoading}
                  className="w-full text-center"
                  maxLength={2}
                />
              </div>
              <div>
                <Input
                  type="text"
                  placeholder="Número"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
                  disabled={isLoading}
                  className="w-full"
                  maxLength={9}
                />
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Mínimo 6 caracteres"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="w-full pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full w-10 p-0 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirmar Senha</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Digite a senha novamente"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                className="w-full pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full w-10 p-0 hover:bg-transparent"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={isLoading}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90"
            disabled={isLoading}
          >
            {isLoading ? "Criando conta..." : "Criar Conta"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Já tem uma conta?{" "}
            <Link
              to="/login"
              className="text-primary hover:underline font-medium"
            >
              Fazer login
            </Link>
          </p>

          <p className="text-xs text-muted-foreground">
            Ao criar uma conta, você concorda com nossos{" "}
            <span className="text-primary hover:underline cursor-pointer">
              Termos de Uso
            </span>{" "}
            e{" "}
            <span className="text-primary hover:underline cursor-pointer">
              Política de Privacidade
            </span>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Register;
