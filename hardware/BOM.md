# Super Famicom / SNES Smart Home Cartridge V1.0

## Bill of Materials (BOM) & Component Sourcing Guide

This bill of materials was sized with a focus on **global high availability** and turnkey SMT assembly at **PCBWay** or **JLCPCB**, with LCSC component codes for simplified purchasing.

---

### Main Components Table (ICs & Modules)

| Item | Designator | Component / MPN         | Package                  | Manufacturer             | LCSC Code     | Qty | Function / Description                                                  | Est. Price (USD) |
|:---- |:---------- |:------------------------ |:------------------------ |:---------------------- |:--------------- |:--- |:------------------------------------------------------------------- |:---------------- |
| 1    | **U6**     | **RP2350B**              | QFN-80 (10x10mm)         | Raspberry Pi           | SC1409 / Distr. | 1   | Dual ARM Cortex-M33 @ 150MHz+, 520KB SRAM, Mailbox                  | ~$1.20           |
| 2    | **U7**     | **W25Q128JVSIQ**         | SOIC-8-208mil            | Winbond                | **C97521**      | 1   | 16MB (128Mbit) QSPI NOR Flash for RP2350                           | ~$0.65           |
| 3    | **U8**     | **ESP32-C6-MINI-1-N4**   | SMD Module (13.2x16.6mm) | Espressif              | **C5248554**    | 1   | Wi-Fi 6 + BLE 5 + Thread/Zigbee co-processor with antenna            | ~$1.95           |
| 4    | **U5**     | **SST39VF040-70-4C-WHE** | TSOP-32 (8x14mm)         | Microchip              | **C129525**     | 1   | 4Mbit (512KB x 8) Parallel NOR Flash (Boot ROM)                     | ~$1.80           |
| 5    | **U2, U3** | **74LVC541APW**          | TSSOP-20                 | Nexperia / TI          | **C5975**       | 2   | Octal Buffer 5V -> 3.3V for address/control bus                     | ~$0.30           |
| 6    | **U4**     | **SN74LVC8T245PWR**      | TSSOP-24                 | Texas Instruments      | **C6207**       | 1   | 8-bit Bidirectional Transceiver 5V <-> 3.3V for data bus            | ~$0.45           |
| 7    | **U1**     | **PIC12F629-I/SN**       | SOIC-8                   | Microchip              | **C20967**      | 1   | SuperCIC Lockout bypass universal (NTSC/PAL auto-detect)            | ~$0.55           |
| 8    | **U9**     | **SY8089AAAC**           | SOT-23-5                 | Silergy                | **C28674**      | 1   | Synchronous Buck Regulator 5V -> 3.3V 2.0A (efficiency >92%)        | ~$0.25           |
| 9    | **U10**    | **DS3231MZ+**            | SOIC-8                   | Analog Devices / Maxim | **C16719**      | 1   | Ultra-high precision RTC (+-5ppm) with internal MEMS resonator      | ~$1.60           |
| 10   | **U11**    | **SP3485CN-L/TR**        | SOIC-8                   | MaxLinear              | **C6960**       | 1   | RS-485 3.3V Half-Duplex Transceiver (Modbus RTU / automation)      | ~$0.40           |
| 11   | **D1, D2** | **USBLC6-2SC6**          | SOT-23-6                 | STMicroelectronics     | **C7519**       | 2   | TVS diode ESD protection for USB D+/D- and bus                      | ~$0.20           |
| 12   | **D3**     | **WS2812B-2020**         | SMD 2020                 | Worldsemi              | **C2890040**    | 1   | Addressable RGB LED for Wi-Fi status and HA connection              | ~$0.10           |
| 13   | **D4**     | **SS34**                 | SMA / DO-214AC           | MDD / Yangjie          | **C46104**      | 1   | 3A 40V Schottky diode reverse power protection                      | ~$0.08           |
| 14   | **F1**     | **1206L150PR**           | SMD 1206                 | Littelfuse             | **C70267**      | 1   | PTC Resettable Fuse 1.5A 6V                                         | ~$0.12           |

---

### Connectors & Electromechanical

| Item | Designator   | Component            | Description / Detail                                                    | LCSC Code      | Qty | Est. Price (USD) |
|:---- |:------------ |:--------------------- |:---------------------------------------------------------------------- |:---------------- |:--- |:---------------- |
| 15   | **P1**       | **SNES Edge Fingers** | 62-pin (2x31) edge connector, **2.50 mm** pitch, ENIG 30° chamfer | Integrated in PCB | 1   | Included in PCB   |
| 16   | **J1**       | **TYPE-C-31-M-12**    | 16-pin SMD USB-C connector for UF2 flashing and serial debug           | **C165948**      | 1   | ~$0.25           |
| 17   | **J4**       | **TF-01A**            | Push-Pull MicroSD SMD Slot                                             | **C91145**       | 1   | ~$0.30           |
| 18   | **J5**       | **KF2EDG-3.5-3P**     | 3.5mm 3-pin screw terminal (A, B, GND) for RS-485 bus                  | **C8389**        | 1   | ~$0.25           |
| 19   | **J6**       | **JST SH 1.0mm 4P**   | Horizontal Qwiic / STEMMA QT connector (3.3V, GND, SDA, SCL)          | **C145920**      | 1   | ~$0.15           |
| 20   | **BT1**      | **CR1220 Holder**     | SMD holder for CR1220 3V coin cell (RTC backup)                        | **C70377**       | 1   | ~$0.20           |
| 21   | **SW1..SW4** | **TS-1187A-C-A-B**    | SMD tactile switches 3x4x2.0mm (BOOTSEL, RESET, ESP_BOOT, ESP_EN)    | **C318884**      | 4   | ~$0.05 ea.       |
| 22   | **Y1**       | **12.000 MHz 3225**   | SMD 3225 12MHz 10ppm 18pF crystal for RP2350                          | **C16280**       | 1   | ~$0.15           |

---

### Critical Passives (Inductors, Capacitors, and Resistors)

| Designator         | Value                         | Package         | LCSC Code | Function                                                          |
|:------------------ |:----------------------------- |:--------------- |:----------- |:--------------------------------------------------------------- |
| **L1**             | **2.2uH / 3.0A**              | SMD CD32 / 0805 | **C144887** | SY8089 Buck converter inductor                                  |
| **C_IN1, C_OUT1**  | **47uF 10V Tantalum/Ceramic** | SMD 1206 / 3528 | **C13063**  | 5V input and 3.3V output filter                                 |
| **C_OUT2, C_IN2**  | **22uF 10V X7R**              | SMD 0805        | **C15849**  | Buck and ESP32 ceramic filter                                   |
| **C_DEC (x12)**    | **100nF (0.1uF) 16V X7R**     | SMD 0402/0603   | **C14663**  | Decoupling for each IC VDD pin                                  |
| **C_XTAL (x2)**    | **15pF 50V C0G**              | SMD 0402/0603   | **C1554**   | 12MHz crystal load capacitors                                   |
| **R_FB1**          | **100k 1%**                   | SMD 0402/0603   | **C25744**  | SY8089 Buck upper feedback resistor                             |
| **R_FB2**          | **22k 1%**                    | SMD 0402/0603   | **C25765**  | Lower feedback resistor (Vout = 0.6V * (1 + 100/22) = 3.32V)   |
| **R_CC1, R_CC2**   | **5.1k 1%**                   | SMD 0402/0603   | **C25905**  | USB-C CC1/CC2 pin pulldown                                      |
| **R_USB1, R_USB2** | **27R 1%**                    | SMD 0402/0603   | **C25114**  | USB D+/D- series damping resistors                              |
| **R_PU (x8)**      | **10k 5%**                    | SMD 0402/0603   | **C25804**  | Reset, Chip Enable, and Flash CS pullups                        |
| **R_I2C1, R_I2C2** | **4.7k 5%**                   | SMD 0402/0603   | **C25900**  | I2C bus (SDA, SCL) pullups                                      |
| **R_TERM**         | **120R 1%**                   | SMD 0603        | **C22787**  | RS-485 line termination resistor                                |

---

### Estimated Unit Cost Summary

- **ICs + Modules:** ~$8.80
- **Connectors + Mechanical + Passives:** ~$3.20
- **4-layer 1.2mm ENIG PCB (Batch 5-10 pcs):** ~$2.50 / board
- **Total estimated cost per assembled prototype:** **~$14.50 USD**
