import { Gauge, Leaf, Droplets, TrendingUp } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import productImage from "@/assets/dispositivo-sensor-de-solo.jpg";

const ProductSection = () => {
  const features = [
    {
      icon: Gauge,
      title: "Medição Precisa",
      description: "Sensores de alta precisão para análise completa do solo"
    },
    {
      icon: Leaf,
      title: "Nutrientes",
      description: "Identifique deficiências e otimize a adubação"
    },
    {
      icon: Droplets,
      title: "Umidade",
      description: "Controle inteligente de irrigação e economia de água"
    },
    {
      icon: TrendingUp,
      title: "Produtividade",
      description: "Aumente sua produção com decisões baseadas em dados"
    }
  ];

  return (
    <section id="produto" className="py-20 bg-muted/30">
      <div className="container px-4 mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-foreground">
            Medidor de Solo Inteligente
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Tecnologia acessível para agricultura familiar de precisão
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div className="order-2 md:order-1">
            <img 
              src={productImage} 
              alt="Dispositivo de medição de solo"
              className="rounded-2xl shadow-lg w-full h-auto"
            />
          </div>

          <div className="order-1 md:order-2 space-y-6">
            <h3 className="text-2xl md:text-3xl font-bold text-foreground">
              Como Funciona?
            </h3>
            <p className="text-muted-foreground text-lg">
              Nosso dispositivo utiliza sensores avançados para medir pH, umidade, 
              temperatura e nutrientes do solo em tempo real. Os dados são processados 
              instantaneamente e você recebe recomendações personalizadas através do 
              nosso chatbot inteligente.
            </p>
            <ul className="space-y-3 text-muted-foreground">
              <li className="flex items-start">
                <span className="text-primary mr-2">✓</span>
                <span>Instalação simples e rápida</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-2">✓</span>
                <span>Resultados em tempo real</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-2">✓</span>
                <span>Recomendações personalizadas via IA</span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-2">✓</span>
                <span>Custo acessível para agricultura familiar</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-border hover:shadow-lg transition-all">
                <CardContent className="p-6 text-center">
                  <div className="mb-4 inline-block p-4 bg-primary/10 rounded-full">
                    <Icon className="h-8 w-8 text-primary" />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-foreground">{feature.title}</h4>
                  <p className="text-muted-foreground text-sm">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ProductSection;
