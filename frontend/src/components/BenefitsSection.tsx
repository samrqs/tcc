import { DollarSign, BarChart, Shield, Sprout } from "lucide-react";

const BenefitsSection = () => {
  const benefits = [
    {
      icon: DollarSign,
      title: "Economia",
      description: "Reduza custos com fertilizantes e água através do uso otimizado baseado em dados reais",
      stat: "Até 40% de economia"
    },
    {
      icon: BarChart,
      title: "Produtividade",
      description: "Aumente a produção com manejo adequado e decisões no momento certo",
      stat: "+30% de produção"
    },
    {
      icon: Shield,
      title: "Sustentabilidade",
      description: "Práticas agrícolas mais sustentáveis com uso consciente de recursos naturais",
      stat: "Menor impacto ambiental"
    },
    {
      icon: Sprout,
      title: "Qualidade",
      description: "Produtos de maior qualidade através do cultivo em condições ideais",
      stat: "Melhor qualidade"
    }
  ];

  return (
    <section id="beneficios" className="py-20 bg-background">
      <div className="container px-4 mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-foreground">
            Benefícios Comprovados
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Resultados reais para agricultores familiares que buscam crescimento sustentável
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <div 
                key={index} 
                className="text-center p-6 rounded-xl hover:bg-muted/50 transition-all"
              >
                <div className="mb-4 inline-block p-5 bg-primary/10 rounded-full">
                  <Icon className="h-10 w-10 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-foreground">{benefit.title}</h3>
                <p className="text-muted-foreground mb-4">{benefit.description}</p>
                <div className="inline-block px-4 py-2 bg-accent/10 rounded-full">
                  <span className="text-accent font-semibold">{benefit.stat}</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-16 bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-8 md:p-12 text-center">
          <h3 className="text-2xl md:text-3xl font-bold mb-4 text-foreground">
            Transforme sua agricultura com tecnologia
          </h3>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Junte-se a centenas de agricultores familiares que já melhoraram seus resultados com nossa solução
          </p>
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;
