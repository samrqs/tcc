import { useState } from "react";

type Parameter = {
  name: string;
  label: string;
  unit: string | null;
  ideal: string;
  min: string;
  max: string;
};

const defaultParams: Parameter[] = [
  { name: "umidade", label: "Umidade", unit: "%", ideal: "", min: "", max: "" },
  { name: "temperatura", label: "Temperatura", unit: "°C", ideal: "", min: "", max: "" },
  { name: "ph", label: "pH", unit: null, ideal: "", min: "", max: "" },
  { name: "nitrogenio", label: "Nitrogênio", unit: "mg/kg", ideal: "", min: "", max: "" },
  { name: "fosforo", label: "Fósforo", unit: "mg/kg", ideal: "", min: "", max: "" },
  { name: "potassio", label: "Potássio", unit: "mg/kg", ideal: "", min: "", max: "" },
  { name: "salinidade", label: "Salinidade", unit: "dS/m", ideal: "", min: "", max: "" },
  { name: "tds", label: "TDS", unit: "ppm", ideal: "", min: "", max: "" }
];

const SoilConfigForm = () => {
  const [parameters, setParameters] = useState<Parameter[]>(defaultParams);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (index: number, field: keyof Parameter, value: string) => {
    const updated = [...parameters];
    updated[index][field] = value;
    setParameters(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const payload = {
      userId: 1,
      sensorId: null,
      parameters: parameters.map(p => ({
        name: p.name,
        ideal: parseFloat(p.ideal),
        min: parseFloat(p.min),
        max: parseFloat(p.max),
        unit: p.unit
      }))
    };

    try {
      const res = await fetch("http://localhost:3000/api/soil/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      setMessage(res.ok ? "✅ Configurações salvas com sucesso!" : "❌ Erro ao salvar");
    } catch {
      setMessage("❌ Falha ao conectar com a API");
    }

    setLoading(false);
  };

  return (
    <section id="soloconfig" className="py-20 bg-background">
      <div className="max-w-4xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-10 text-foreground">
          Configuração dos Parâmetros do Solo
        </h2>

        <form onSubmit={handleSubmit} className="space-y-8">
          {parameters.map((p, index) => (
            <div key={p.name} className="p-6 rounded-xl border bg-muted/30">
              <h3 className="text-xl font-semibold mb-4 text-foreground">
                {p.label} {p.unit && `(${p.unit})`}
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Ideal</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                    value={p.ideal}
                    required
                    onChange={(e) => handleChange(index, "ideal", e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Mínimo</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                    value={p.min}
                    required
                    onChange={(e) => handleChange(index, "min", e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Máximo</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                    value={p.max}
                    required
                    onChange={(e) => handleChange(index, "max", e.target.value)}
                  />
                </div>
              </div>
            </div>
          ))}

          <div className="text-center">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 rounded-lg bg-primary text-primary-foreground text-lg font-medium hover:opacity-90 transition"
            >
              {loading ? "Salvando..." : "Salvar Configurações"}
            </button>
          </div>

          {message && (
            <p className="text-center text-lg font-medium mt-4">
              {message}
            </p>
          )}
        </form>
      </div>
    </section>
  );
};

export default SoilConfigForm;
