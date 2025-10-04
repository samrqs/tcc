#include <ModbusMaster.h>
#include <SPI.h>
#include <LoRa.h>

// ========== CONFIGURAÇÃO MODBUS ==========
#define MAX485_RE_DE      18
#define MAX485_RX         16
#define MAX485_TX         17
#define SLAVE_ADDR 1

ModbusMaster node;

// ========== CONFIGURAÇÃO LORA ==========
#define LORA_SCK     5
#define LORA_MISO    19  
#define LORA_MOSI    27
#define LORA_SS      18
#define LORA_RST     14
#define LORA_DIO0    26
#define BAND    915E6

// ========== ESTRUTURA DE DADOS ==========
struct SensorData {
  float humidity;
  float temperature;
  float conductivity;
  float ph;
  float nitrogen;
  float phosphorus;
  float potassium;
  float salinity;
  float tds;
};

// ========== ESTATÍSTICAS DE TRANSMISSÃO ==========
unsigned long totalPacketsSent = 0;
unsigned long lastStatsTime = 0;
const long statsInterval = 30000; // Exibir estatísticas a cada 30 segundos

void setup() {
  // Serial para debug
  Serial.begin(115200);
  
  // ========== INICIALIZA MODBUS ==========
  pinMode(MAX485_RE_DE, OUTPUT);
  digitalWrite(MAX485_RE_DE, LOW);
  Serial2.begin(4800, SERIAL_8N1, MAX485_RX, MAX485_TX);
  
  node.begin(SLAVE_ADDR, Serial2);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  // ========== INICIALIZA LORA ==========
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(BAND)) {
    Serial.println("Falha ao iniciar LoRa!");
    while (1);
  }
  
  LoRa.setTxPower(20);
  Serial.println("Sender Modbus+LoRa inicializado!");
  Serial.println("Aguardando dados...");
  
  lastStatsTime = millis();
}

void loop() {
  SensorData data = readModbusData();
  
  if (data.humidity >= 0) { // Se leitura foi bem sucedida
    sendViaLoRa(data);
    printData(data);
    monitorTxQuality();
  }
  
  // Exibe estatísticas periodicamente
  if (millis() - lastStatsTime > statsInterval) {
    displayStatistics();
    lastStatsTime = millis();
  }
  
  delay(10000); // Espera 10 segundos
}

// ========== FUNÇÃO PARA LER DADOS MODBUS ==========
SensorData readModbusData() {
  SensorData data = {-1, -1, -1, -1, -1, -1, -1, -1, -1}; // Valores inválidos inicialmente
  
  uint8_t result = node.readHoldingRegisters(0, 9);
  
  if (result == node.ku8MBSuccess) {
    data.humidity = node.getResponseBuffer(0) * 0.1;
    data.temperature = node.getResponseBuffer(1) * 0.1;
    data.conductivity = node.getResponseBuffer(2);
    data.ph = node.getResponseBuffer(3) * 0.1;
    data.nitrogen = node.getResponseBuffer(4);
    data.phosphorus = node.getResponseBuffer(5);
    data.potassium = node.getResponseBuffer(6);
    data.salinity = node.getResponseBuffer(7);
    data.tds = node.getResponseBuffer(8);
  } else {
    Serial.print("Erro Modbus: 0x");
    Serial.println(result, HEX);
  }
  
  return data;
}

// ========== FUNÇÃO PARA ENVIAR VIA LORA ==========
void sendViaLoRa(SensorData data) {
  LoRa.beginPacket();
  
  // Formato: JSON compacto para economizar bytes
  LoRa.print("{");
  LoRa.print("\"h\":"); LoRa.print(data.humidity); LoRa.print(",");
  LoRa.print("\"t\":"); LoRa.print(data.temperature); LoRa.print(",");
  LoRa.print("\"c\":"); LoRa.print(data.conductivity); LoRa.print(",");
  LoRa.print("\"ph\":"); LoRa.print(data.ph); LoRa.print(",");
  LoRa.print("\"n\":"); LoRa.print(data.nitrogen); LoRa.print(",");
  LoRa.print("\"p\":"); LoRa.print(data.phosphorus); LoRa.print(",");
  LoRa.print("\"k\":"); LoRa.print(data.potassium); LoRa.print(",");
  LoRa.print("\"s\":"); LoRa.print(data.salinity); LoRa.print(",");
  LoRa.print("\"tds\":"); LoRa.print(data.tds);
  LoRa.print("}");
  
  LoRa.endPacket();
  totalPacketsSent++;
  Serial.println("Dados enviados via LoRa!");
}

// ========== MONITORAMENTO DE ENVIO ==========
void monitorTxQuality() {
  // Exibe contagem a cada 5 pacotes
  if (totalPacketsSent % 5 == 0) {
    Serial.print("✓ Pacote #");
    Serial.println(totalPacketsSent);
  }
}

// ========== EXIBE ESTATÍSTICAS ==========
void displayStatistics() {
  Serial.println("\n========== ESTATÍSTICAS TRANSMISSÃO ==========");
  Serial.print("Pacotes enviados: ");
  Serial.println(totalPacketsSent);
  
  Serial.print("Taxa de envio: ");
  Serial.print((totalPacketsSent * 60000.0) / millis());
  Serial.println(" pacotes/minuto");
  
  Serial.print("Tempo de operação: ");
  Serial.print(millis() / 60000);
  Serial.println(" minutos");
  
  // Estimativa de consumo de energia (aproximada)
  float energyUsed = (totalPacketsSent * 0.130); // 130mA durante 1s por pacote
  Serial.print("Energia estimada: ");
  Serial.print(energyUsed, 2);
  Serial.println(" mAh");
  
  Serial.println("=============================================\n");
}

// ========== FUNÇÃO PARA DEBUG ==========
void printData(SensorData data) {
  Serial.println("======== DADOS COLETADOS ========");
  Serial.printf("Umidade: %.1f %%RH\n", data.humidity);
  Serial.printf("Temperatura: %.1f °C\n", data.temperature);
  Serial.printf("Condutividade: %.0f uS/cm\n", data.conductivity);
  Serial.printf("pH: %.1f\n", data.ph);
  Serial.printf("Nitrogênio: %.0f mg/kg\n", data.nitrogen);
  Serial.printf("Fósforo: %.0f mg/kg\n", data.phosphorus);
  Serial.printf("Potássio: %.0f mg/kg\n", data.potassium);
  Serial.printf("Salinidade: %.0f mg/L\n", data.salinity);
  Serial.printf("TDS: %.0f mg/L\n", data.tds);
  Serial.println("=================================");
}

// ========== CONTROLE MAX485 ==========
void preTransmission() {
  digitalWrite(MAX485_RE_DE, HIGH);
}

void postTransmission() {
  digitalWrite(MAX485_RE_DE, LOW);
}