# Diretrizes de Fabricação PCBWay para Cartucho SNES / Super Famicom

Ao configurar o pedido de fabricação da placa de circuito impresso na **PCBWay** (ou JLCPCB), utilize obrigatoriamente os seguintes parâmetros:

---

### 1. Especificações Críticas da Placa

| Parâmetro | Valor Recomendado | Motivo / Observação Crítica |
| :--- | :--- | :--- |
| **Layers (Camadas)** | **4 Layers** | Necessário para integridade de sinal do barramento de 21MHz, plano contínuo de GND e impedância RF do ESP32-C6. |
| **PCB Thickness (Espessura)** | **1.2 mm** (ou 1.25 mm) | **CRÍTICO:** O conector original do Super Famicom / SNES foi desenhado para PCBs de **1.2 mm**. Placas comuns de 1.6 mm são muito grossas e danificam/empenam as lâminas do slot do console. Placas de 0.8 mm ficam frouxas. |
| **Surface Finish (Acabamento)** | **ENIG (Electroless Nickel Immersion Gold)** ou **Hard Gold (Gold Fingers)** | Ouro de imersão resistente à abrasão das inserções e oxidação ao longo dos anos. |
| **Gold Fingers (Dedos de Ouro)** | **Yes** | Selecione para aplicar banho de ouro reforçado nos 62 contatos de borda. |
| **Edge Chamfering / Beveling** | **Yes, 30° Chamfer** (30 graus) | **CRÍTICO:** Faz o chanfro em ângulo de 30° na borda inferior dos contatos, permitindo que o cartucho deslize suavemente para dentro do slot do console sem engasgar ou arrancar os pads. |
| **Connector Pitch** | **2.50 mm** (Métrico) | Conferir que o footprint usa passo de 2.50 mm (não 2.54 mm). |
| **Solder Mask (Máscara de Solda)** | Azul / Preto Fosco / Cinza | Estética de sua preferência. |
| **Silkscreen (Serigrafia)** | Branco | Texto em alta legibilidade. |
| **Copper Weight (Cobre)** | 1 oz (externo) / 0.5 oz (interno) | Padrão industrial. |
| **Material** | FR-4 Standard (Tg 150-170) | Alta estabilidade térmica durante reflow. |

---

### 2. Stackup Sugerido de 4 Camadas (1.2mm)

```text
Camada 1 (Top):     Sinais de alta velocidade, componentes SMD, antena RF
Camada 2 (In1):     Plano de Terra Sólido (GND)
Camada 3 (In2):     Plano de Alimentação (+3.3V Digital + 5V SNES)
Camada 4 (Bottom):  Sinais de controle, barramento secundário, contatos de borda traseiros
```

---

### 3. Cuidados Especiais no Roteamento & Layout

1. **Antena do ESP32-C6:**
   - Posicione o módulo ESP32-C6-MINI na borda superior do cartucho (longe do conector de 62 pinos).
   - Mantenha a área sob a antena do módulo completamente livre de cobre (sem trilhas e sem planos de GND em todas as 4 camadas).
2. **Diferencial RS-485:**
   - Trilhas A e B roteadas em par diferencial com impedância de 120 ohms acoplada.
3. **Barramento de Dados (D0..D7):**
   - Comprimento casado entre os buffers 74LVC e o RP2350/Flash.
4. **Desacoplamento do Buck Converter:**
   - Posicione C_IN1, L1 e C_OUT1 o mais próximo possível dos pinos do SY8089 para minimizar o loop de comutação de 1.5 MHz.
