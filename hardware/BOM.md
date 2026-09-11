# Super Famicom / SNES Smart Home Cartridge V1.0
## Bill of Materials (BOM) & Component Sourcing Guide

Esta lista de materiais foi dimensionada com foco em **alta disponibilidade global** e montagem SMT turnkey na **PCBWay** ou **JLCPCB**, com códigos de componentes LCSC para compra simplificada.

---

### Tabela de Componentes Principais (ICs & Módulos)

| Item | Designator | Componente / MPN | Package | Fabricante | Código LCSC | Qtd | Função / Descrição | Preço Est. (USD) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **U6** | **RP2350B** | QFN-80 (10x10mm) | Raspberry Pi | SC1409 / Distr. | 1 | Dual ARM Cortex-M33 @ 150MHz+, 520KB SRAM, Mailbox | ~$1.20 |
| 2 | **U7** | **W25Q128JVSIQ** | SOIC-8-208mil | Winbond | **C97521** | 1 | 16MB (128Mbit) QSPI NOR Flash para RP2350 | ~$0.65 |
| 3 | **U8** | **ESP32-C6-MINI-1-N4** | SMD Module (13.2x16.6mm) | Espressif | **C5248554** | 1 | Coprocessador Wi-Fi 6 + BLE 5 + Thread/Zigbee com antena | ~$1.95 |
| 4 | **U5** | **SST39VF040-70-4C-WHE** | TSOP-32 (8x14mm) | Microchip | **C129525** | 1 | 4Mbit (512KB x 8) Parallel NOR Flash (Boot ROM) | ~$1.80 |
| 5 | **U2, U3** | **74LVC541APW** | TSSOP-20 | Nexperia / TI | **C5975** | 2 | Buffer Octal 5V -> 3.3V para barramento de endereços/controle | ~$0.30 |
| 6 | **U4** | **SN74LVC8T245PWR** | TSSOP-24 | Texas Instruments | **C6207** | 1 | Transceiver Bidirecional 8-bit 5V <-> 3.3V para barramento de dados | ~$0.45 |
| 7 | **U1** | **PIC12F629-I/SN** | SOIC-8 | Microchip | **C20967** | 1 | SuperCIC Lockout bypass universal (NTSC/PAL auto-detect) | ~$0.55 |
| 8 | **U9** | **SY8089AAAC** | SOT-23-5 | Silergy | **C28674** | 1 | Regulador Buck Síncrono 5V -> 3.3V 2.0A (eficiência >92%) | ~$0.25 |
| 9 | **U10** | **DS3231MZ+** | SOIC-8 | Analog Devices / Maxim | **C16719** | 1 | RTC de altíssima precisão (+-5ppm) com ressonador MEMS interno | ~$1.60 |
| 10 | **U11** | **SP3485CN-L/TR** | SOIC-8 | MaxLinear | **C6960** | 1 | Transceiver RS-485 3.3V Half-Duplex (Modbus RTU / automação) | ~$0.40 |
| 11 | **D1, D2** | **USBLC6-2SC6** | SOT-23-6 | STMicroelectronics | **C7519** | 2 | Diodo TVS proteção ESD para USB D+/D- e barramento | ~$0.20 |
| 12 | **D3** | **WS2812B-2020** | SMD 2020 | Worldsemi | **C2890040** | 1 | LED RGB endereçável para status de Wi-Fi e conexão HA | ~$0.10 |
| 13 | **D4** | **SS34** | SMA / DO-214AC | MDD / Yangjie | **C46104** | 1 | Diodo Schottky 3A 40V proteção de alimentação reversa | ~$0.08 |
| 14 | **F1** | **1206L150PR** | SMD 1206 | Littelfuse | **C70267** | 1 | Fusível rearmável PTC 1.5A 6V | ~$0.12 |

---

### Conectores & Eletromecânicos

| Item | Designator | Componente | Descrição / Detalhe | Código LCSC | Qtd | Preço Est. (USD) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 15 | **P1** | **SNES Edge Fingers** | Conector de borda 62 pinos (2x31), passo **2.50 mm**, ENIG 30° chanfro | Integrado no PCB | 1 | Incluso na PCB |
| 16 | **J1** | **TYPE-C-31-M-12** | Conector USB-C 16-pinos SMD para flashing UF2 e debug serial | **C165948** | 1 | ~$0.25 |
| 17 | **J4** | **TF-01A** | Slot MicroSD Push-Pull SMD | **C91145** | 1 | ~$0.30 |
| 18 | **J5** | **KF2EDG-3.5-3P** | Borne parafuso 3.5mm 3 pinos (A, B, GND) para barramento RS-485 | **C8389** | 1 | ~$0.25 |
| 19 | **J6** | **JST SH 1.0mm 4P** | Conector Qwiic / STEMMA QT horizontal (3.3V, GND, SDA, SCL) | **C145920** | 1 | ~$0.15 |
| 20 | **BT1** | **CR1220 Holder** | Suporte SMD para bateria moeda CR1220 3V (backup do RTC) | **C70377** | 1 | ~$0.20 |
| 21 | **SW1..SW4** | **TS-1187A-C-A-B** | Micro chaves tácteis SMD 3x4x2.0mm (BOOTSEL, RESET, ESP_BOOT, ESP_EN) | **C318884** | 4 | ~$0.05 cad |
| 22 | **Y1** | **12.000 MHz 3225** | Cristal SMD 3225 12MHz 10ppm 18pF para RP2350 | **C16280** | 1 | ~$0.15 |

---

### Passivos Críticos (Indutores, Capacitores e Resistores)

| Designator | Valor | Package | Código LCSC | Função |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | **2.2uH / 3.0A** | SMD CD32 / 0805 | **C144887** | Indutor do conversor Buck SY8089 |
| **C_IN1, C_OUT1**| **47uF 10V Tântalo/Cerâmica** | SMD 1206 / 3528 | **C13063** | Filtro de entrada 5V e saída 3.3V |
| **C_OUT2, C_IN2**| **22uF 10V X7R** | SMD 0805 | **C15849** | Filtro cerâmico do Buck e ESP32 |
| **C_DEC (x12)** | **100nF (0.1uF) 16V X7R**| SMD 0402/0603 | **C14663** | Desacoplamento para cada pino de VDD dos ICs |
| **C_XTAL (x2)** | **15pF 50V C0G** | SMD 0402/0603 | **C1554** | Capacitores de carga do cristal de 12MHz |
| **R_FB1** | **100k 1%** | SMD 0402/0603 | **C25744** | Resistor Feedback superior do Buck SY8089 |
| **R_FB2** | **22k 1%** | SMD 0402/0603 | **C25765** | Resistor Feedback inferior (Vout = 0.6V * (1 + 100/22) = 3.32V) |
| **R_CC1, R_CC2** | **5.1k 1%** | SMD 0402/0603 | **C25905** | Pulldown dos pinos CC1/CC2 do USB-C |
| **R_USB1, R_USB2**| **27R 1%** | SMD 0402/0603 | **C25114** | Resistores série amortecimento D+/D- USB |
| **R_PU (x8)** | **10k 5%** | SMD 0402/0603 | **C25804** | Pullups de Reset, Chip Enable e Flash CS |
| **R_I2C1, R_I2C2**| **4.7k 5%** | SMD 0402/0603 | **C25900** | Pullups dos barramentos I2C (SDA, SCL) |
| **R_TERM** | **120R 1%** | SMD 0603 | **C22787** | Resistor de terminação da linha RS-485 |

---

### Resumo de Custo Unitário Estimado

- **Circuito Integrado + Módulos:** ~$8.80
- **Conectores + Mecânica + Passivos:** ~$3.20
- **PCB 4 camadas 1.2mm ENIG (Lote 5-10 un.):** ~$2.50 / placa
- **Custo total estimado por protótipo montado:** **~$14.50 USD**
