## ⚙️ Componentes de Hardware Utilizados

| Quantidade | Componente | Função |
|-------------|-------------|--------|
| 2 | **ESP32 LoRa com OLED V2 (Heltec)** | Comunicação LoRa e controle do sistema |
| 1 | **Sensor RS485 (Temp, Umidade, pH, NPK e Salinidade)** | Coleta de dados do solo |
| 1 | **Módulo MAX485 UART** | Conversão de sinal RS485 ↔ UART para comunicação com o sensor |
| 1 | **Protoboard 400 pontos** | Montagem dos circuitos de teste e prototipagem |
| 1 | **Fonte chaveada 12V 1A** | Alimentação sensor RS485 |

---

## 🧠 Arquitetura Básica

| Etapa | Componente                      | Função                                                  |
| ----- | ------------------------------- | ------------------------------------------------------- |
| 🌾    | **Sensores RS485**              | Captura dados do solo (pH, umidade, temperatura, NPK)   |
| 🔌    | **Módulo MAX485**               | Faz a conversão do sinal RS485 → UART                   |
| 📡    | **ESP32 LoRa V2 (Transmissor)** | Envia os dados via rede LoRa                            |
| 📶    | **ESP32 LoRa V2 (Receptor)**    | Recebe os dados LoRa e envia para o servidor            |
| 💬    | **Plataforma / WhatsApp**       | Exibe as informações e permite interação com o produtor |

O **sensor RS485** coleta os dados do solo, o **MAX485** faz a conversão de sinal para o **ESP32 LoRa**, que transmite as informações via **LoRa** para outro módulo ESP32 receptor.

---

## 💻 Configuração do Ambiente Arduino IDE

### 1. Instalar a Arduino IDE
Baixe e instale a **Arduino IDE** mais recente:  
🔗 [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)

---

### 2. Adicionar o Gerenciador de Placas da Heltec

1. Abra a Arduino IDE  
2. Vá em **Arquivo → Preferências**  
3. No campo **URLs Adicionais para Gerenciador de Placas**, adicione o seguinte link:
https://resource.heltec.cn/download/package_heltec_esp32_index.json

4. Clique em **OK** para salvar.

---

### 3. Instalar o Gerenciador de Placas

1. Vá em **Ferramentas → Placa → Gerenciador de Placas...**
2. Procure por **Heltec ESP32 Series Dev-Boards**
3. Clique em **Instalar**

---

### 4. Selecionar a Placa Correta

Após a instalação, selecione a placa:

> **Ferramentas → Placa → Heltec ESP32 → WiFi LoRa 32(V2)**

---

### 5. Instalar Bibliotecas Necessárias

Vá em **Sketch → Incluir Biblioteca → Gerenciar Bibliotecas...** e instale:

- **Heltec ESP32 Dev-Boards** (by Heltec Automation)
- **LoRa** (by Sandeep Mistry)
- **ArduinoJson** (by Benoit Blanchon)

---

## 🧰 Drivers Necessários (Reconhecimento da Placa)

Para que o computador reconheça o **ESP32 LoRa V2 da Heltec**, é necessário instalar o **driver CP210x**.

1. Acesse o site oficial da Silicon Labs:  
🔗 [https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

2. Baixe o driver compatível com o seu sistema operacional (Windows, macOS ou Linux)

3. Após instalar, conecte o ESP32 e verifique se ele aparece como uma porta serial na IDE  
*(Exemplo: COM3 no Windows ou /dev/ttyUSB0 no Linux)*

---

## 📁 Estrutura dos Arquivos `.ino`

Os arquivos `.ino` contêm o código-fonte para o funcionamento do sistema.  
Abra o arquivo principal no Arduino IDE e certifique-se de que todas as bibliotecas estejam corretamente instaladas.

> **Dica:** mantenha o nome da pasta igual ao nome do arquivo `.ino`, pois o Arduino IDE exige isso para compilar corretamente.

---

## 🔌 Ligações de Hardware (Exemplo)

| ESP32 LoRa V2 | Módulo MAX485 | Descrição |
|----------------|----------------|-----------|
| 3V3 | VCC | Alimentação |
| GND | GND | Terra |
| GPIO17 | RO | Recepção RS485 |
| GPIO16 | DI | Transmissão RS485 |
| GPIO4 | DE/RE (ligados juntos) | Habilitação do driver |

Ter uma fonte de alimentação separada para o sensor RS485 entre 12 a 30V.
---

## 🚀 Upload do Código

1. Conecte o **ESP32 LoRa V2** via cabo USB  
2. Selecione a porta correta em:  
   > **Ferramentas → Porta → COMx (Windows)** ou **/dev/ttyUSBx (Linux)**  
3. Clique em **→ Upload** (ícone de seta na IDE)

Após o upload, o código será gravado no microcontrolador.

---

## 📡 Comunicação LoRa

O projeto utiliza o protocolo **LoRa** para comunicação entre módulos.  
Certifique-se de configurar as mesmas **frequências** e **chaves** em ambos os dispositivos (transmissor e receptor).

---

## 🧾 Créditos

**Autor:** Leonardo Arouche  
**Hardware:** Heltec ESP32 LoRa V2, MAX485, Sensor RS485  
**Linguagem:** C++ (Arduino)  
**IDE:** Arduino IDE  
**Propósito:** Democratizar o acesso à agricultura inteligente de baixo custo 🌿

---

## 📜 Licença
Este projeto é distribuído sob a licença **MIT**, permitindo uso livre para fins acadêmicos e comerciais, com atribuição de crédito ao autor.

---

