import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { ArrowLeft, Eye, EyeOff, Leaf } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error("Email e senha são obrigatórios");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error("Digite um email válido");
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(email, password);

      if (result.success) {
        toast.success("Login realizado com sucesso!");
        navigate("/");
      } else {
        toast.error(result.error || "Erro ao fazer login. Tente novamente.");
      }
    } catch (error) {
      console.error("Erro ao fazer login:", error);
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
          <h1 className="text-2xl font-bold text-foreground mb-2">Entrar</h1>
          <p className="text-muted-foreground text-sm">
            Faça login na sua conta do FarmerAssist
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
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
            <Label htmlFor="password">Senha</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Sua senha"
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

          <Button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90"
            disabled={isLoading}
          >
            {isLoading ? "Entrando..." : "Entrar"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Não tem uma conta?{" "}
            <Link
              to="/register"
              className="text-primary hover:underline font-medium"
            >
              Criar conta
            </Link>
          </p>
        </div>

        <div className="mt-4 text-center text-xs text-muted-foreground">
          <p>
            Esqueceu sua senha?{" "}
            <span className="text-primary hover:underline cursor-pointer">
              Clique aqui
            </span>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Login;
