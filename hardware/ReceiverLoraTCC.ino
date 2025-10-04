#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ========== CONFIGURAÇÃO LORA ==========
#define LORA_SCK     5
#define LORA_MISO    19  
#define LORA_MOSI    27
#define LORA_SS      18
#define LORA_RST     14
#define LORA_DIO0    26
#define BAND    915E6

// ========== CONFIGURAÇÃO WIFI ==========
const char* ssid = "";
const char* password = "";

// ========== CONFIGURAÇÃO ENDPOINT ==========
const char* serverURL = "http://IP:PORT/api/sensors/webhook/";
const char* authToken = "Bearer TokenAcess";

// ========== ESTATÍSTICAS LORA ==========
unsigned long totalPacketsReceived = 0;
unsigned long totalPacketsSent = 0;
unsigned long successfulHTTPPosts = 0;
unsigned long failedHTTPPosts = 0;
unsigned long lastStatsTime = 0;
const long statsInterval = 30000; // Exibir estatísticas a cada 30 segundos

// Variáveis para qualidade do sinal
float avgRSSI = 0;
float avgSNR = 0;
int minRSSI = -200;
int maxRSSI = 0;
int packetCountForStats = 0;

void setup() {
  Serial.begin(115200);
  
  // Conecta WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
  
  // Inicializa LoRa
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(BAND)) {
    Serial.println("Falha ao iniciar LoRa Receiver!");
    while (1);
  }
  
  // Configuração adicional do LoRa para melhor performance
  LoRa.setSyncWord(0x12); // Sincronização personalizada
  LoRa.enableCrc();       // Habilita verificação CRC
  
  Serial.println("Receiver LoRa+HTTP pronto!");
  Serial.print("Tentando conectar em: ");
  Serial.println(serverURL);
  
  lastStatsTime = millis();
}

void loop() {
  // Verifica conexão WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado! Reconectando...");
    WiFi.reconnect();
    delay(5000);
    return;
  }
  
  // Verifica se há pacotes LoRa
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    totalPacketsReceived++;
    
    String receivedData = "";
    
    // Lê os dados recebidos
    while (LoRa.available()) {
      receivedData += (char)LoRa.read();
    }
    
    // Obtém métricas de qualidade do sinal
    float rssi = LoRa.packetRssi();
    float snr = LoRa.packetSnr();
    
    // Atualiza estatísticas de qualidade do sinal
    updateSignalStats(rssi, snr);
    
    Serial.print("Pacote #");
    Serial.print(totalPacketsReceived);
    Serial.print(" | RSSI: ");
    Serial.print(rssi);
    Serial.print(" dBm | SNR: ");
    Serial.print(snr);
    Serial.println(" dB");
    Serial.println("Dados recebidos: " + receivedData);
    
    // Processa e envia para o endpoint
    processAndSendData(receivedData);
  }
  
  // Exibe estatísticas periodicamente
  if (millis() - lastStatsTime > statsInterval) {
    displayStatistics();
    lastStatsTime = millis();
  }
  
  delay(100);
}

// ========== ATUALIZA ESTATÍSTICAS DE SINAL ==========
void updateSignalStats(float rssi, float snr) {
  // Atualiza RSSI mínimo e máximo
  if (rssi < minRSSI) minRSSI = rssi;
  if (rssi > maxRSSI) maxRSSI = rssi;
  
  // Calcula média móvel para RSSI e SNR
  avgRSSI = (avgRSSI * packetCountForStats + rssi) / (packetCountForStats + 1);
  avgSNR = (avgSNR * packetCountForStats + snr) / (packetCountForStats + 1);
  
  packetCountForStats++;
}

// ========== EXIBE ESTATÍSTICAS ==========
void displayStatistics() {
  Serial.println("\n========== ESTATÍSTICAS LORA ==========");
  Serial.print("Pacotes recebidos: ");
  Serial.println(totalPacketsReceived);
  
  Serial.print("Taxa de recebimento: ");
  Serial.print((totalPacketsReceived * 1000.0) / (millis() / 1000.0));
  Serial.println(" pacotes/minuto");
  
  Serial.print("Sucesso HTTP: ");
  Serial.print(successfulHTTPPosts);
  Serial.print(" | Falhas HTTP: ");
  Serial.println(failedHTTPPosts);
  
  if (totalPacketsReceived > 0) {
    Serial.print("Taxa de sucesso HTTP: ");
    Serial.print((successfulHTTPPosts * 100.0) / totalPacketsReceived);
    Serial.println("%");
  }
  
  Serial.println("--- Qualidade do Sinal ---");
  Serial.print("RSSI Médio: ");
  Serial.print(avgRSSI);
  Serial.print(" dBm | Min: ");
  Serial.print(minRSSI);
  Serial.print(" dBm | Max: ");
  Serial.print(maxRSSI);
  Serial.println(" dBm");
  
  Serial.print("SNR Médio: ");
  Serial.print(avgSNR);
  Serial.println(" dB");
  
  // Interpretação da qualidade do sinal
  Serial.print("Qualidade: ");
  if (avgRSSI > -80) {
    Serial.println("EXCELENTE");
  } else if (avgRSSI > -100) {
    Serial.println("BOA");
  } else if (avgRSSI > -120) {
    Serial.println("FRACA");
  } else {
    Serial.println("RUIM");
  }
  
  Serial.println("=======================================\n");
}

// ========== FUNÇÃO PARA PROCESSAR E ENVIAR DADOS ==========
void processAndSendData(String rawData) {
  totalPacketsSent++;
  
  // Converte JSON string para objeto
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, rawData);
  
  if (error) {
    Serial.print("Erro ao parsear JSON: ");
    Serial.println(error.c_str());
    failedHTTPPosts++;
    return;
  }
  
  // Cria novo JSON com os nomes em português
  DynamicJsonDocument payload(1024);
  
  payload["umidade"] = doc["h"].as<float>();
  payload["temperatura"] = doc["t"].as<float>();
  payload["condutividade"] = doc["c"].as<float>();
  payload["ph"] = doc["ph"].as<float>();
  payload["nitrogenio"] = doc["n"].as<float>();
  payload["fosforo"] = doc["p"].as<float>();
  payload["potassio"] = doc["k"].as<float>();
  payload["salinidade"] = doc["s"].as<float>();
  payload["tds"] = doc["tds"].as<float>();
  
  // Adiciona métricas de qualidade
  // payload["rssi"] = LoRa.packetRssi();
  // payload["snr"] = LoRa.packetSnr();
  // payload["packet_number"] = totalPacketsReceived;
  
  // Converte para string JSON
  String jsonString;
  serializeJson(payload, jsonString);
  
  Serial.println("JSON para enviar: " + jsonString);
  
  // Envia via HTTP POST
  HTTPClient http;
  
  http.begin(serverURL);
  http.addHeader("Authorization", authToken);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("User-Agent", "ESP32-LoRa-Sensor");
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    if (httpResponseCode == 200 || httpResponseCode == 201) {
      successfulHTTPPosts++;
      Serial.print("✓ HTTP Success: ");
    } else {
      failedHTTPPosts++;
      Serial.print("⚠ HTTP Warning: ");
    }
    Serial.println(httpResponseCode);
  } else {
    failedHTTPPosts++;
    Serial.print("✗ HTTP Error: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}