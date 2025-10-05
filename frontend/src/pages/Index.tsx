import Hero from "@/components/Hero";
import ProductSection from "@/components/ProductSection";
import BenefitsSection from "@/components/BenefitsSection";
import ChatBot from "@/components/ChatBot";
import { Leaf } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Leaf className="h-6 w-6 text-primary" />
            </div>
            <span className="text-xl font-bold text-foreground">FarmerAssist</span>
          </div>
          <div className="hidden md:flex gap-6 text-sm font-medium">
            <a href="#produto" className="text-muted-foreground hover:text-primary transition-colors">
              Produto
            </a>
            <a href="#beneficios" className="text-muted-foreground hover:text-primary transition-colors">
              Benefícios
            </a>
          </div>
        </div>
      </nav>

      <div className="pt-16">
        <Hero />
        <ProductSection />
        <BenefitsSection />
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
