# SNES Smart Home — Complete Pin Mapping

Reference document for all hardware signals across the 5-sheet KiCad schematic.

---

## 1. SNES 62-Pin Edge Connector (P1)

Standard SHVC-001 cartridge edge connector. Gold fingers, 2.50 mm pitch, 1.2 mm PCB thickness.

### Signal Summary

| Category        | Count | Pins                          |
|:----------------|:------|:------------------------------|
| Power (+5V)     | 2     | 27, 58                        |
| Ground (GND)    | 2     | 5, 36                         |
| Data (D0-D7)    | 8     | 19-22, 50-53                  |
| Address (A0-A15)| 16    | 6-17, 37-40                   |
| Bank (A16-A23)  | 8     | 41-48                         |
| Control         | 6     | 18, 23, 26, 49, 54, 57        |
| CIC             | 4     | 24, 25, 55, 56                |
| NC / Reserved   | 18    | 1-4, 7-16, 28-35, 51-52 (alt) |

### Complete Pin Table (1-62, Top Side)

| Pin | Signal        | Direction  | Description                          |
|:----|:--------------|:-----------|:-------------------------------------|
| 1   | NC            | —          | No connect                           |
| 2   | NC            | —          | No connect                           |
| 3   | NC            | —          | No connect                           |
| 4   | NC            | —          | No connect                           |
| 5   | **GND**       | Power      | Ground                               |
| 6   | SNES_A0       | Input →    | Address bus bit 0                    |
| 7   | SNES_A1       | Input →    | Address bus bit 1                    |
| 8   | SNES_A2       | Input →    | Address bus bit 2                    |
| 9   | SNES_A3       | Input →    | Address bus bit 3                    |
| 10  | SNES_A4       | Input →    | Address bus bit 4                    |
| 11  | SNES_A5       | Input →    | Address bus bit 5                    |
| 12  | SNES_A6       | Input →    | Address bus bit 6                    |
| 13  | SNES_A7       | Input →    | Address bus bit 7                    |
| 14  | SNES_A8       | Input →    | Address bus bit 8                    |
| 15  | SNES_A9       | Input →    | Address bus bit 9                    |
| 16  | SNES_A10      | Input →    | Address bus bit 10                   |
| 17  | SNES_A11      | Input →    | Address bus bit 11                   |
| 18  | **/IRQ**      | Output ←   | Interrupt request (active low)        |
| 19  | SNES_D0       | Bidir ↔    | Data bus bit 0                       |
| 20  | SNES_D1       | Bidir ↔    | Data bus bit 1                       |
| 21  | SNES_D2       | Bidir ↔    | Data bus bit 2                       |
| 22  | SNES_D3       | Bidir ↔    | Data bus bit 3                       |
| 23  | **/RD**       | Input →    | Read strobe (active low)             |
| 24  | CIC_DAT1      | I/O ↔      | CIC data line 1 (lockout)            |
| 25  | CIC_RST       | Output ←   | CIC reset                            |
| 26  | **/RESET**    | Input →    | System reset (active low)            |
| 27  | **+5V_SNES**  | Power      | +5V from console                     |
| 28  | NC            | —          | No connect                           |
| 29  | NC            | —          | No connect                           |
| 30  | NC            | —          | No connect                           |
| 31  | NC            | —          | No connect                           |
| 32  | NC            | —          | No connect                           |
| 33  | NC            | —          | No connect                           |
| 34  | NC            | —          | No connect                           |
| 35  | NC            | —          | No connect                           |
| 36  | **GND**       | Power      | Ground                               |
| 37  | SNES_A12      | Input →    | Address bus bit 12                   |
| 38  | SNES_A13      | Input →    | Address bus bit 13                   |
| 39  | SNES_A14      | Input →    | Address bus bit 14                   |
| 40  | SNES_A15      | Input →    | Address bus bit 15                   |
| 41  | SNES_A16      | Input →    | Bank address bit 0 (A16)             |
| 42  | SNES_A17      | Input →    | Bank address bit 1 (A17)             |
| 43  | SNES_A18      | Input →    | Bank address bit 2 (A18)             |
| 44  | SNES_A19      | Input →    | Bank address bit 3 (A19)             |
| 45  | SNES_A20      | Input →    | Bank address bit 4 (A20)             |
| 46  | SNES_A21      | Input →    | Bank address bit 5 (A21)             |
| 47  | SNES_A22      | Input →    | Bank address bit 6 (A22)             |
| 48  | SNES_A23      | Input →    | Bank address bit 7 (A23)             |
| 49  | **/ROMSEL**   | Input →    | ROM chip select /CART (active low)   |
| 50  | SNES_D4       | Bidir ↔    | Data bus bit 4                       |
| 51  | SNES_D5       | Bidir ↔    | Data bus bit 5                       |
| 52  | SNES_D6       | Bidir ↔    | Data bus bit 6                       |
| 53  | SNES_D7       | Bidir ↔    | Data bus bit 7                       |
| 54  | **/WR**       | Input →    | Write strobe (active low)            |
| 55  | CIC_DAT2      | I/O ↔      | CIC data line 2 (console)            |
| 56  | CIC_CLK       | Output ←   | CIC clock (76 kHz)                   |
| 57  | **PHI2**      | Input →    | CPU clock (3.58 MHz NTSC / 3.52 PAL)|
| 58  | **+5V_SNES**  | Power      | +5V from console                     |
| 59  | NC            | —          | No connect                           |
| 60  | NC            | —          | No connect                           |
| 61  | NC            | —          | No connect                           |
| 62  | NC            | —          | No connect                           |

---

## 2. PIC12F629 SuperCIC Pin Mapping (U1)

The PIC12F629 implements the SuperCIC lockout bypass, enabling the cartridge to work on both lockout and non-lockout consoles (NTSC/PAL auto-detect).

### SOIC-8 Package

| Pin | Signal       | Direction | Description                              |
|:----|:-------------|:----------|:-----------------------------------------|
| 1   | VDD          | Power     | +3V3 (from SY8089 buck regulator)        |
| 2   | RA5 / CIC_DAT1 | I/O ↔  | Bidirectional CIC data (to SNES pin 24)  |
| 3   | RA4 / CIC_DAT2 | I/O ↔  | Bidirectional CIC data (to SNES pin 55)  |
| 4   | RA3 / CIC_RST  | Input   | CIC reset from console (SNES pin 25)     |
| 5   | RA2 / CIC_CLK  | Output  | CIC clock to console (SNES pin 56)       |
| 6   | RA1           | NC       | Unused (or debug LED)                    |
| 7   | RA0           | NC       | Unused (or NTSC/PAL select jumper)       |
| 8   | VSS          | Power     | GND                                      |

### SuperCIC Operation

1. On power-up, the PIC emulates the CIC lockout chip handshake.
2. Console asserts /RESET → PIC drives CIC_CLK at 76 kHz.
3. CIC_DAT1 and CIC_DAT2 exchange challenge/response tokens.
4. If handshake succeeds → console releases /ROMSEL and bus access begins.
5. NTSC/PAL auto-detected from CIC_CLK frequency (76.0 kHz NTSC / 76.1 kHz PAL).

---

## 3. Inter-Sheet Signal Routing

All signals between schematic sheets pass through hierarchical labels. The table below maps every cross-sheet signal.

### Sheet 1 → Sheet 2 (SNES Bus → Level Shifters)

| Signal       | SNES Pin | U2/U3 Input | U2/U3 Output | Target IC |
|:-------------|:---------|:------------|:-------------|:----------|
| SNES_A0      | 6        | 74LVC541 U2 | BUS_A0       | RP2350, U5 |
| SNES_A1      | 7        | 74LVC541 U2 | BUS_A1       | RP2350, U5 |
| SNES_A2      | 8        | 74LVC541 U2 | BUS_A2       | RP2350, U5 |
| SNES_A3      | 9        | 74LVC541 U2 | BUS_A3       | RP2350, U5 |
| SNES_A4      | 10       | 74LVC541 U2 | BUS_A4       | RP2350, U5 |
| SNES_A5      | 11       | 74LVC541 U2 | BUS_A5       | RP2350, U5 |
| SNES_A6      | 12       | 74LVC541 U2 | BUS_A6       | RP2350, U5 |
| SNES_A7      | 13       | 74LVC541 U2 | BUS_A7       | RP2350, U5 |
| SNES_A8      | 14       | 74LVC541 U3 | BUS_A8       | RP2350, U5 |
| SNES_A9      | 15       | 74LVC541 U3 | BUS_A9       | RP2350, U5 |
| SNES_A10     | 16       | 74LVC541 U3 | BUS_A10      | RP2350, U5 |
| SNES_A11     | 17       | 74LVC541 U3 | BUS_A11      | RP2350, U5 |
| SNES_A12     | 37       | 74LVC541 U3 | BUS_A12      | RP2350     |
| SNES_A13     | 38       | 74LVC541 U3 | BUS_A13      | RP2350     |
| SNES_A14     | 39       | 74LVC541 U3 | BUS_A14      | RP2350     |
| SNES_A15     | 40       | 74LVC541 U3 | BUS_A15      | RP2350     |
| /RD          | 23       | 74LVC541 U2 | BUS_RD       | RP2350, U4 |
| /WR          | 54       | 74LVC541 U2 | BUS_WR       | RP2350     |
| /ROMSEL      | 49       | 74LVC541 U3 | BUS_ROMSEL   | RP2350     |
| PHI2         | 57       | 74LVC541 U3 | BUS_PHI2     | RP2350     |
| SNES_D0-D3   | 19-22    | SN74LVC8T245 U4 | BUS_D0-D3 | RP2350, U5 |
| SNES_D4-D7   | 50-53    | SN74LVC8T245 U4 | BUS_D4-D7 | RP2350, U5 |

**Direction control:** U4 DIR pin = SNES /RD (read → SNES→BUS direction for active reads).

### Sheet 2 → Sheet 3 (Level Shifters → RP2350)

| Signal        | Source      | RP2350 GPIO | Function               |
|:--------------|:------------|:------------|:-----------------------|
| BUS_D0        | U4          | GPIO0       | Data bus bit 0         |
| BUS_D1        | U4          | GPIO1       | Data bus bit 1         |
| BUS_D2        | U4          | GPIO2       | Data bus bit 2         |
| BUS_D3        | U4          | GPIO3       | Data bus bit 3         |
| BUS_D4        | U4          | GPIO4       | Data bus bit 4         |
| BUS_D5        | U4          | GPIO5       | Data bus bit 5         |
| BUS_D6        | U4          | GPIO6       | Data bus bit 6         |
| BUS_D7        | U4          | GPIO7       | Data bus bit 7         |
| BUS_A0        | U2          | GPIO8       | Address bus bit 0      |
| BUS_A1        | U2          | GPIO9       | Address bus bit 1      |
| BUS_A2        | U2          | GPIO10      | Address bus bit 2      |
| BUS_A3        | U2          | GPIO11      | Address bus bit 3      |
| BUS_A4        | U2          | GPIO12      | Address bus bit 4      |
| BUS_A5        | U2          | GPIO13      | Address bus bit 5      |
| BUS_A6        | U2          | GPIO14      | Address bus bit 6      |
| BUS_A7        | U2          | GPIO15      | Address bus bit 7      |
| BUS_A8        | U3          | GPIO16      | Address bus bit 8      |
| BUS_A9        | U3          | GPIO17      | Address bus bit 9      |
| BUS_A10       | U3          | GPIO18      | Address bus bit 10     |
| BUS_A11       | U3          | GPIO19      | Address bus bit 11     |
| BUS_A12       | U3          | GPIO20      | Address bus bit 12     |
| BUS_A13       | U3          | GPIO21      | Address bus bit 13     |
| BUS_A14       | U3          | GPIO22      | Address bus bit 14     |
| BUS_A15       | U3          | GPIO23      | Address bus bit 15     |
| BUS_/RD       | U2          | GPIO24      | Read strobe (active low)|
| BUS_/WR       | U2          | GPIO25      | Write strobe (active low)|
| BUS_/ROMSEL   | U3          | GPIO26      | ROM chip select        |
| BUS_PHI2      | U3          | GPIO27      | CPU clock (3.58 MHz)   |
| BUS_/IRQ      | RP2350      | GPIO28      | Interrupt to SNES      |

### Sheet 3 → Sheet 4 (RP2350 ↔ ESP32-C6)

| Signal      | RP2350 GPIO | ESP32-C6 Pin | Interface | Function           |
|:------------|:------------|:-------------|:----------|:-------------------|
| SPI_SCK     | GPIO29      | SPI_CLK      | SPI0      | SPI clock          |
| SPI_MOSI    | GPIO30      | SPI_MOSI     | SPI0      | Master Out Slave In|
| SPI_MISO    | GPIO31      | SPI_MISO     | SPI0      | Master In Slave Out|
| SPI_CS      | GPIO32      | SPI_CS       | SPI0      | Chip select        |
| UART_TX     | GPIO33      | UART_RX      | UART0     | RP2350 → ESP32     |
| UART_RX     | GPIO34      | UART_TX      | UART0     | ESP32 → RP2350     |

### Sheet 3 → Sheet 5 (RP2350 ↔ Peripherals)

| Signal     | RP2350 GPIO | Peripheral       | Interface | Function           |
|:-----------|:------------|:-----------------|:----------|:-------------------|
| I2C_SDA    | GPIO35      | DS3231, Qwiic    | I2C0      | Data line          |
| I2C_SCL    | GPIO36      | DS3231, Qwiic    | I2C0      | Clock line         |
| SD_SCK     | GPIO37      | MicroSD J4       | SPI1      | SD clock           |
| SD_MOSI    | GPIO38      | MicroSD J4       | SPI1      | SD data in         |
| SD_MISO    | GPIO39      | MicroSD J4       | SPI1      | SD data out        |
| SD_CS      | GPIO40      | MicroSD J4       | SPI1      | SD chip select     |
| RS485_TX   | GPIO41      | SP3485 U11       | UART1     | RS-485 transmit    |
| RS485_RX   | GPIO42      | SP3485 U11       | UART1     | RS-485 receive     |
| RS485_DE   | GPIO41 (shared) | SP3485 U11  | GPIO      | Driver Enable      |

### Sheet 3 — Status & Configuration GPIOs

| Signal       | RP2350 GPIO | Function                          |
|:-------------|:------------|:----------------------------------|
| LED_STATUS   | GPIO43      | WS2812B RGB status LED            |
| LED_WIFI     | GPIO44      | Wi-Fi connection indicator        |
| LED_HEARTBEAT| GPIO45      | Firmware alive indicator          |
| JUMP_BOOTSEL | GPIO46      | BOOTSEL button input (active low) |
| JUMP_RST     | GPIO47      | RESET button input (active low)   |

---

## 4. Power Domain Mapping

### Domain: +5V_SNES (Console Supply)

| Source        | Pin(s)        | Distribution                               |
|:--------------|:--------------|:-------------------------------------------|
| SNES Pin 27   | +5V_SNES      | → PTC Fuse F1 (1.5A) → Schottky D4 (SS34) |
| SNES Pin 58   | +5V_SNES      | → PTC Fuse F1 (1.5A) → Schottky D4 (SS34) |

**After protection:**
| Consumer                  | Input         | Notes                              |
|:--------------------------|:--------------|:-----------------------------------|
| SY8089 Buck (U9)          | 5V input      | Converts to +3V3                   |
| 74LVC541 U2               | VCC (5V side) | SNES-side supply                   |
| 74LVC541 U3               | VCC (5V side) | SNES-side supply                   |
| SN74LVC8T245 U4           | VCCA (5V side)| SNES-side supply                   |
| SST39VF040 U5             | VCC           | Parallel Flash boot ROM            |
| PIC12F629 U1              | —             | Powered from +3V3, not +5V        |

### Domain: +3V3 (Regulated Supply)

| Source        | Consumer                  | Notes                              |
|:--------------|:--------------------------|:-----------------------------------|
| SY8089 (U9)  | RP2350B (U6)              | Core + IO supply                   |
| SY8089 (U9)  | W25Q128 (U7)              | QSPI Flash                         |
| SY8089 (U9)  | ESP32-C6 (U8)             | Wi-Fi/BLE module                   |
| SY8089 (U9)  | 74LVC541 U2               | 3.3V-side supply                   |
| SY8089 (U9)  | 74LVC541 U3               | 3.3V-side supply                   |
| SY8089 (U9)  | SN74LVC8T245 U4           | 3.3V-side supply (VCCB)           |
| SY8089 (U9)  | DS3231 (U10)              | RTC                                |
| SY8089 (U9)  | SP3485 (U11)              | RS-485 transceiver                 |
| SY8089 (U9)  | MicroSD (J4)              | SD card slot                       |
| SY8089 (U9)  | I2C pullups (4.7k)        | SDA/SCL bias                       |
| CR1220 (BT1) | DS3231 VBAT               | RTC battery backup                 |

### Domain: GND (Common Ground)

| Source        | Pin(s)         | Distribution                      |
|:--------------|:---------------|:----------------------------------|
| SNES Pin 5    | GND            | Common ground plane               |
| SNES Pin 36   | GND            | Common ground plane               |

All ICs share the same GND plane (4-layer PCB, In1 = solid GND).

### Power Tree Diagram

```text
SNES +5V_SNES (Pins 27, 58)
  │
  ├── F1 (PTC 1.5A) ── D4 (SS34 Schottky) ──┬── +5V protected
  │                                           │
  │     ┌─────────────────────────────────────┤
  │     │                                     │
  │     ▼                                     ▼
  │  U9 SY8089 Buck                     U2, U3, U4 (5V side)
  │  5V → 3.3V 2.0A                    U5 SST39VF040 Flash
  │     │
  │     ▼
  │  +3V3 Rail
  │     ├── U6 RP2350B
  │     ├── U7 W25Q128 QSPI
  │     ├── U8 ESP32-C6
  │     ├── U10 DS3231 RTC
  │     ├── U11 SP3485 RS-485
  │     ├── J4 MicroSD
  │     ├── U2, U3, U4 (3.3V side)
  │     ├── I2C pullups (4.7k)
  │     └── BT1 CR1220 → DS3231 VBAT (backup)
  │
GND (Pins 5, 36) ── Common ground plane (In1)
```

---

## 5. 74LVC Level Shifter Details

### U2 — 74LVC541APW (Octal Buffer, Unidirectional)

Translates SNES-side 5V signals to 3.3V bus for RP2350. Unidirectional (SNES → BUS).

| 74LVC541 Pin | Input (5V) | Output (3.3V) | 74LVC541 Pin |
|:-------------|:-----------|:---------------|:-------------|
| 2 (1A1)      | SNES_A0    | BUS_A0         | 18 (1Y4)     |
| 3 (1A2)      | SNES_A1    | BUS_A1         | 17 (1Y3)     |
| 4 (1A3)      | SNES_A2    | BUS_A2         | 16 (1Y2)     |
| 5 (1A4)      | SNES_A3    | BUS_A3         | 15 (1Y1)     |
| 7 (2A1)      | SNES_A4    | BUS_A4         | 13 (2Y4)     |
| 8 (2A2)      | SNES_A5    | BUS_A5         | 12 (2Y3)     |
| 9 (2A3)      | SNES_A6    | BUS_A6         | 11 (2Y2)     |
| 10 (2A4)     | SNES_A7    | BUS_A7         | 10 (2Y1)     |

OE1 (pin 1) = GND (always enabled)
OE2 (pin 19) = GND (always enabled)

### U3 — 74LVC541APW (Octal Buffer, Unidirectional)

| 74LVC541 Pin | Input (5V)  | Output (3.3V) | 74LVC541 Pin |
|:-------------|:------------|:---------------|:-------------|
| 2 (1A1)      | SNES_A8     | BUS_A8         | 18 (1Y4)     |
| 3 (1A2)      | SNES_A9     | BUS_A9         | 17 (1Y3)     |
| 4 (1A3)      | SNES_A10    | BUS_A10        | 16 (1Y2)     |
| 5 (1A4)      | SNES_A11    | BUS_A11        | 15 (1Y1)     |
| 7 (2A1)      | SNES_A12    | BUS_A12        | 13 (2Y4)     |
| 8 (2A2)      | SNES_A13    | BUS_A13        | 12 (2Y3)     |
| 9 (2A3)      | SNES_A14    | BUS_A14        | 11 (2Y2)     |
| 10 (2A4)     | SNES_A15    | BUS_A15        | 10 (2Y1)     |

OE1 (pin 1) = GND, OE2 (pin 19) = GND

### U4 — SN74LVC8T245 (Bidirectional Transceiver)

8-bit bidirectional data bus translator. Direction controlled by /RD.

| 74LVC8T245 Pin | Side A (5V)  | Side B (3.3V) | 74LVC8T245 Pin |
|:---------------|:-------------|:---------------|:---------------|
| 2 (A0)         | SNES_D0      | BUS_D0         | 23 (B0)        |
| 3 (A1)         | SNES_D1      | BUS_D1         | 22 (B1)        |
| 4 (A2)         | SNES_D2      | BUS_D2         | 21 (B2)        |
| 5 (A3)         | SNES_D3      | BUS_D3         | 20 (B3)        |
| 6 (A4)         | SNES_D4      | BUS_D4         | 19 (B4)        |
| 7 (A5)         | SNES_D5      | BUS_D5         | 18 (B5)        |
| 8 (A6)         | SNES_D6      | BUS_D6         | 17 (B6)        |
| 9 (A7)         | SNES_D7      | BUS_D7         | 16 (B7)        |

| Control Pin | Signal     | Function                            |
|:------------|:-----------|:------------------------------------|
| 1 (DIR)     | BUS_RD     | Direction: H = A→B, L = B→A        |
| 11 (OE)     | GND        | Always enabled                      |

**DIR logic:** When /RD is LOW (active read), DIR = LOW → B→A (BUS→SNES). When /RD is HIGH, DIR = HIGH → A→B (SNES→BUS for writes).

---

## 6. SST39VF040 Flash Memory Map (U5)

| BUS_A0-A18 | BUS_D0-D7 | RP2350 GPIO | Function         |
|:-----------|:----------|:------------|:-----------------|
| BUS_A0     | BUS_D0    | GPIO0       | Data bit 0       |
| BUS_A1     | BUS_D1    | GPIO1       | Data bit 1       |
| BUS_A2     | BUS_D2    | GPIO2       | Data bit 2       |
| BUS_A3     | BUS_D3    | GPIO3       | Data bit 3       |
| BUS_A4     | BUS_D4    | GPIO4       | Data bit 4       |
| BUS_A5     | BUS_D5    | GPIO5       | Data bit 5       |
| BUS_A6     | BUS_D6    | GPIO6       | Data bit 6       |
| BUS_A7     | BUS_D7    | GPIO7       | Data bit 7       |
| BUS_A0-A17 | —         | GPIO8-25    | Address bus      |
| BUS_A18    | —         | GPIO26      | Address bit 18   |

Flash control: CE (chip enable), OE (output enable), WE (write enable) — active low.

---

## 7. GPIO Allocation Summary (RP2350B — 48 GPIOs Used)

| GPIO Range | Count | Function                          | Direction   |
|:-----------|:------|:----------------------------------|:------------|
| 0-7        | 8     | Data bus (BUS_D0-D7)              | Bidir ↔     |
| 8-23       | 16    | Address bus (BUS_A0-A15)          | Input →     |
| 24         | 1     | BUS_/RD                           | Input →     |
| 25         | 1     | BUS_/WR                           | Input →     |
| 26         | 1     | BUS_/ROMSEL                       | Input →     |
| 27         | 1     | BUS_PHI2                          | Input →     |
| 28         | 1     | BUS_/IRQ                          | Output ←    |
| 29-32      | 4     | SPI0 to ESP32 (SCK,MOSI,MISO,CS) | Bidir ↔     |
| 33-34      | 2     | UART0 to ESP32 (TX, RX)           | Bidir ↔     |
| 35-36      | 2     | I2C0 (SDA, SCL)                   | Bidir ↔     |
| 37-40      | 4     | SPI1 MicroSD (SCK,MOSI,MISO,CS)  | Bidir ↔     |
| 41-42      | 2     | UART1 RS-485 (TX, RX)             | Bidir ↔     |
| 43         | 1     | WS2812B RGB LED                   | Output →    |
| 44-45      | 2     | Status LEDs (WiFi, Heartbeat)     | Output →    |
| 46-47      | 2     | Button inputs (BOOTSEL, RST)      | Input →     |
| **Total**  | **48**|                                   |             |
