import { ArrowRight } from "lucide-react";
import { Button } from "./ui/button";
import heroImage from "@/assets/hero-farming.jpg";

const Hero = () => {
  const scrollToProduct = () => {
    document.getElementById('produto')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6)), url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      />
      
      <div className="container relative z-10 px-4 py-20 mx-auto text-center text-white">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in">
          Agricultura Familiar<br />
          <span className="text-accent">Inteligente</span>
        </h1>
        
        <p className="text-lg md:text-xl lg:text-2xl mb-8 max-w-3xl mx-auto text-gray-100 animate-fade-in">
          Tecnologia de medição de solo que transforma dados em decisões precisas para sua lavoura
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in">
          <Button 
            size="lg"
            onClick={scrollToProduct}
            className="bg-primary hover:bg-primary/90 text-white px-8 py-6 text-lg shadow-lg hover:shadow-xl transition-all"
          >
            Conheça Nossa Solução
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          
          <Button 
            size="lg"
            variant="outline"
            onClick={() => document.getElementById('beneficios')?.scrollIntoView({ behavior: 'smooth' })}
            className="bg-white/10 hover:bg-white/20 text-white border-white/30 backdrop-blur-sm px-8 py-6 text-lg"
          >
            Saiba Mais
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
