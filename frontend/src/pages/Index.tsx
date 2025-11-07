import BenefitsSection from "@/components/BenefitsSection";
import ChatBot from "@/components/ChatBot";
import Hero from "@/components/Hero";
import ProductSection from "@/components/ProductSection";
import SoilConfigForm from "@/components/SoilConfigForm";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { Leaf, LogOut } from "lucide-react";

const Index = () => {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Leaf className="h-6 w-6 text-primary" />
            </div>
            <span className="text-xl font-bold text-foreground">
              FarmerAssist
            </span>
          </div>
          {/* Desktop Navigation */}
          <div className="hidden md:flex gap-6 text-sm font-medium items-center">
            <a
              href="#produto"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Produto
            </a>
            <a
              href="#beneficios"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Benefícios
            </a>
            <a
              href="#soloconfig"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Configuração Solo
            </a>
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-primary font-medium">
                  Olá, {user.name || user.email}!
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                  className="flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Sair
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <a
                  href="/login"
                  className="text-primary hover:text-primary/80 transition-colors font-medium"
                >
                  Entrar
                </a>
                <a
                  href="/register"
                  className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Criar Conta
                </a>
              </div>
            )}
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden">
            {user ? (
              <div className="flex flex-col items-end text-right">
                <span className="text-primary font-medium text-sm">
                  Olá,{" "}
                  {user.name
                    ? user.name.split(" ")[0]
                    : user.email.split("@")[0]}
                  !
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-xs h-6 px-2 mt-1"
                >
                  Sair
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <a
                  href="/login"
                  className="text-primary hover:text-primary/80 transition-colors text-sm font-medium"
                >
                  Entrar
                </a>
                <a
                  href="/register"
                  className="bg-primary text-white px-3 py-2 rounded-lg hover:bg-primary/90 transition-colors text-sm"
                >
                  Criar Conta
                </a>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="pt-16">
        <Hero />
        <ProductSection />
        <BenefitsSection />
        <SoilConfigForm />
      </div>

      <footer className="bg-muted/30 border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; 2025 FarmerAssist.</p>
        </div>
      </footer>

      <ChatBot />
    </div>
  );
};

export default Index;
