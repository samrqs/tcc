import { config } from "@/lib/config";
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
  {
    name: "umidade",
    label: "Umidade",
    unit: "%",
    ideal: "60",
    min: "40",
    max: "80",
  },
  {
    name: "temperatura",
    label: "Temperatura",
    unit: "°C",
    ideal: "25",
    min: "15",
    max: "35",
  },
  { name: "ph", label: "pH", unit: null, ideal: "6.5", min: "5.5", max: "7.5" },
  {
    name: "nitrogenio",
    label: "Nitrogênio",
    unit: "mg/kg",
    ideal: "50",
    min: "30",
    max: "70",
  },
  {
    name: "fosforo",
    label: "Fósforo",
    unit: "mg/kg",
    ideal: "40",
    min: "20",
    max: "60",
  },
  {
    name: "potassio",
    label: "Potássio",
    unit: "mg/kg",
    ideal: "150",
    min: "100",
    max: "200",
  },
  {
    name: "condutividade",
    label: "Condutividade",
    unit: "dS/m",
    ideal: "2",
    min: "1",
    max: "4",
  },
  {
    name: "salinidade",
    label: "Salinidade",
    unit: "dS/m",
    ideal: "2",
    min: "0.5",
    max: "4",
  },
  {
    name: "tds",
    label: "TDS",
    unit: "ppm",
    ideal: "1000",
    min: "500",
    max: "2000",
  },
];

const SoilConfigForm = ({ accessToken }: { accessToken: string }) => {
  const [parameters, setParameters] = useState<Parameter[]>(defaultParams);
  const [cultivo, setCultivo] = useState("");
  const [area, setArea] = useState("");
  const [dataPlantio, setDataPlantio] = useState("");
  const [alertasAtivos, setAlertasAtivos] = useState(true);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (
    index: number,
    field: keyof Parameter,
    value: string
  ) => {
    const updated = [...parameters];
    updated[index][field] = value;
    setParameters(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    // Função auxiliar para obter valores dos parâmetros
    const getParamValue = (
      paramName: string,
      field: "ideal" | "min" | "max"
    ): number => {
      const param = parameters.find((p) => p.name === paramName);
      return param ? parseFloat(param[field]) || 0 : 0;
    };

    const payload = {
      cultivo: cultivo,
      area: area,
      data_plantio: dataPlantio,
      umidade_min: getParamValue("umidade", "min"),
      umidade_ideal: getParamValue("umidade", "ideal"),
      umidade_max: getParamValue("umidade", "max"),
      temperatura_min: getParamValue("temperatura", "min"),
      temperatura_ideal: getParamValue("temperatura", "ideal"),
      temperatura_max: getParamValue("temperatura", "max"),
      ph_min: getParamValue("ph", "min"),
      ph_ideal: getParamValue("ph", "ideal"),
      ph_max: getParamValue("ph", "max"),
      nitrogenio_min: getParamValue("nitrogenio", "min"),
      nitrogenio_ideal: getParamValue("nitrogenio", "ideal"),
      nitrogenio_max: getParamValue("nitrogenio", "max"),
      fosforo_min: getParamValue("fosforo", "min"),
      fosforo_ideal: getParamValue("fosforo", "ideal"),
      fosforo_max: getParamValue("fosforo", "max"),
      potassio_min: getParamValue("potassio", "min"),
      potassio_ideal: getParamValue("potassio", "ideal"),
      potassio_max: getParamValue("potassio", "max"),
      condutividade_min: getParamValue("condutividade", "min"),
      condutividade_ideal: getParamValue("condutividade", "ideal"),
      condutividade_max: getParamValue("condutividade", "max"),
      salinidade_min: getParamValue("salinidade", "min"),
      salinidade_ideal: getParamValue("salinidade", "ideal"),
      salinidade_max: getParamValue("salinidade", "max"),
      tds_min: getParamValue("tds", "min"),
      tds_ideal: getParamValue("tds", "ideal"),
      tds_max: getParamValue("tds", "max"),
      alertas_ativos: alertasAtivos,
    };

    try {
      const res = await fetch(`${config.api.baseUrl}/sensors/crop/alerts/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });

      setMessage(
        res.ok ? "✅ Configurações salvas com sucesso!" : "❌ Erro ao salvar"
      );
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
          {/* Informações Gerais */}
          <div className="p-6 rounded-xl border bg-muted/30">
            <h3 className="text-xl font-semibold mb-4 text-foreground">
              Informações Gerais
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium">Cultivo</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                  value={cultivo}
                  required
                  placeholder="Ex: Milho, Soja, Tomate"
                  onChange={(e) => setCultivo(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Área</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                  value={area}
                  required
                  placeholder="Ex: Lote A, Setor 1"
                  onChange={(e) => setArea(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Data de Plantio</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 mt-1 rounded-md bg-background border"
                  value={dataPlantio}
                  required
                  onChange={(e) => setDataPlantio(e.target.value)}
                />
              </div>

              <div className="flex items-center pt-6">
                <input
                  type="checkbox"
                  id="alertas"
                  className="w-4 h-4 rounded border-gray-300"
                  checked={alertasAtivos}
                  onChange={(e) => setAlertasAtivos(e.target.checked)}
                />
                <label htmlFor="alertas" className="ml-2 text-sm font-medium">
                  Alertas ativos
                </label>
              </div>
            </div>
          </div>

          {/* Parâmetros */}
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
                    onChange={(e) =>
                      handleChange(index, "ideal", e.target.value)
                    }
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
            <p className="text-center text-lg font-medium mt-4">{message}</p>
          )}
        </form>
      </div>
    </section>
  );
};

export default SoilConfigForm;
