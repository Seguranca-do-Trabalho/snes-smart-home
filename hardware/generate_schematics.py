#!/usr/bin/env python3
import os, uuid

HW_DIR = os.path.dirname(os.path.abspath(__file__))

def uid():
    return str(uuid.uuid4())

# 1. Main root schematic
root_uuid = uid()
s1_uuid = uid()
s2_uuid = uid()
s3_uuid = uid()
s4_uuid = uid()
s5_uuid = uid()

root_sch = f"""(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "{root_uuid}")
	(paper "A3")
	(title_block
		(title "Super Famicom Smart Home & Diagnostics Cartridge")
		(date "2026-09-10")
		(rev "V1.0")
		(company "SNES SmartHome Project")
		(comment 1 "RP2350B + ESP32-C6 + Parallel Flash + Level Shifting")
		(comment 2 "Targeted for PCBWay 4-Layer 1.2mm ENIG 30-deg Bevel")
	)
	(sheet
		(at 38.1 44.45)
		(size 76.2 38.1)
		(fields_autoplaced yes)
		(stroke (width 0.1524) (type solid))
		(fill (color 0 0 0 0.0000))
		(uuid "{s1_uuid}")
		(property "Sheetname" "01_SNES_BUS_AND_CIC"
			(at 38.1 43.18 0)
			(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))
		)
		(property "Sheetfile" "01_SNES_BUS_AND_CIC.kicad_sch"
			(at 38.1 83.82 0)
			(effects (font (size 1.27 1.27)) (justify left top))
		)
	)
	(sheet
		(at 139.7 44.45)
		(size 76.2 38.1)
		(fields_autoplaced yes)
		(stroke (width 0.1524) (type solid))
		(fill (color 0 0 0 0.0000))
		(uuid "{s2_uuid}")
		(property "Sheetname" "02_LEVEL_SHIFTERS_AND_FLASH"
			(at 139.7 43.18 0)
			(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))
		)
		(property "Sheetfile" "02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch"
			(at 139.7 83.82 0)
			(effects (font (size 1.27 1.27)) (justify left top))
		)
	)
	(sheet
		(at 241.3 44.45)
		(size 76.2 38.1)
		(fields_autoplaced yes)
		(stroke (width 0.1524) (type solid))
		(fill (color 0 0 0 0.0000))
		(uuid "{s3_uuid}")
		(property "Sheetname" "03_RP2350_SUBSYSTEM"
			(at 241.3 43.18 0)
			(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))
		)
		(property "Sheetfile" "03_RP2350_SUBSYSTEM.kicad_sch"
			(at 241.3 83.82 0)
			(effects (font (size 1.27 1.27)) (justify left top))
		)
	)
	(sheet
		(at 88.9 101.6)
		(size 76.2 38.1)
		(fields_autoplaced yes)
		(stroke (width 0.1524) (type solid))
		(fill (color 0 0 0 0.0000))
		(uuid "{s4_uuid}")
		(property "Sheetname" "04_ESP32C6_WIFI_IOT"
			(at 88.9 100.33 0)
			(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))
		)
		(property "Sheetfile" "04_ESP32C6_WIFI_IOT.kicad_sch"
			(at 88.9 140.97 0)
			(effects (font (size 1.27 1.27)) (justify left top))
		)
	)
	(sheet
		(at 190.5 101.6)
		(size 76.2 38.1)
		(fields_autoplaced yes)
		(stroke (width 0.1524) (type solid))
		(fill (color 0 0 0 0.0000))
		(uuid "{s5_uuid}")
		(property "Sheetname" "05_PERIPHERALS_AND_POWER"
			(at 190.5 100.33 0)
			(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))
		)
		(property "Sheetfile" "05_PERIPHERALS_AND_POWER.kicad_sch"
			(at 190.5 140.97 0)
			(effects (font (size 1.27 1.27)) (justify left top))
		)
	)
	(text "SUPER FAMICOM / SNES SMART HOME INTERFACE CARTRIDGE V1.0\\n\\nSystem Overview:\\n- Sheet 1: 62-Pin SNES Bus Edge Connector (2.50mm pitch, 1.2mm PCB) + SuperCIC PIC12F629\\n- Sheet 2: 74LVC541 + SN74LVC8T245 Level Shifters + 4Mbit Parallel Boot Flash (SST39VF040)\\n- Sheet 3: RP2350B MCU Subsystem (Dual Cortex-M33, 520KB SRAM Mailbox, 16MB QSPI, USB-C)\\n- Sheet 4: ESP32-C6-MINI-1 Wi-Fi 6 / BLE / 802.15.4 Module (Home Assistant REST/WS, MQTT)\\n- Sheet 5: Peripherals (MicroSD SPI, DS3231MZ RTC, SP3485 RS-485, Qwiic I2C) + SY8089 5V->3.3V 2A Buck"
		(at 38.1 160.0 0)
		(effects (font (size 2.0 2.0)) (justify left top))
		(uuid "{uid()}")
	)
	(sheet_instances
		(path "/" (page "1"))
		(path "/{s1_uuid}" (page "2"))
		(path "/{s2_uuid}" (page "3"))
		(path "/{s3_uuid}" (page "4"))
		(path "/{s4_uuid}" (page "5"))
		(path "/{s5_uuid}" (page "6"))
	)
)
"""

with open(os.path.join(HW_DIR, "snes_smarthome_cartridge.kicad_sch"), "w") as f:
    f.write(root_sch)

# 2. Helper to create sub-sheets
def make_subsheet(filename, title, contents):
    s = f"""(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "{uid()}")
	(paper "A3")
	(title_block
		(title "{title}")
		(date "2026-09-10")
		(rev "V1.0")
		(company "SNES SmartHome Project")
	)
{contents}
)
"""
    with open(os.path.join(HW_DIR, filename), "w") as f:
        f.write(s)

# Sheet 1: SNES Bus & CIC
s1_content = f"""
	(text "SHEET 1: SNES 62-PIN CARTRIDGE CONNECTOR & SUPERCIC\\n\\nPinout Specifications:\\n- Pitch: 2.50mm Metric Pitch (DO NOT USE 2.54mm!)\\n- PCB Thickness: 1.20mm ENIG with 30-degree Beveling\\n\\nSignals:\\n- Power: Pins 27, 58 = +5V_SNES, Pins 5, 36 = GND\\n- Data: Pins 19-22 = SNES_D0..SNES_D3, Pins 50-53 = SNES_D4..SNES_D7\\n- Address: Pins 17..6 = SNES_A0..SNES_A11, Pins 37..40 = SNES_A12..SNES_A15\\n- Bank Address: Pins 41..48 = SNES_A16..SNES_A23\\n- Control: Pin 23 = /RD, Pin 54 = /WR, Pin 49 = /ROMSEL (/CART), Pin 26 = /RESET, Pin 57 = PHI2, Pin 18 = /IRQ\\n\\nLockout Bypass:\\n- U1: PIC12F629-I/SN running open-source SuperCIC firmware\\n  Pin 1: VDD (+5V_SNES), Pin 8: GND\\n  Pin 3: CIC_CLK (Edge Pin 56)\\n  Pin 4: CIC_RST (Edge Pin 25)\\n  Pin 5: CIC_DAT1 (Edge Pin 24)\\n  Pin 6: CIC_DAT2 (Edge Pin 55)\\n  Pin 7: Mode/Status LED / Region select\\n\\nDecoupling & Protection:\\n- C1: 100nF 0603 X7R on U1 VDD\\n- D1, D2: SRV05-4 / USBLC6 TVS protection diode arrays on data & control bus"
		(at 30 30 0)
		(effects (font (size 2.2 2.2)) (justify left top))
		(uuid "{uid()}")
	)
"""
make_subsheet("01_SNES_BUS_AND_CIC.kicad_sch", "SNES 62-Pin Cartridge Connector & SuperCIC", s1_content)

# Sheet 2: Level Shifters & Flash
s2_content = f"""
	(text "SHEET 2: VOLTAGE LEVEL SHIFTERS & BOOT FLASH ROM\\n\\nLevel Shifting Architecture (5V TTL <-> 3.3V CMOS):\\n1. Address & Control Bus (SNES -> Cartridge, Unidirectional 5V -> 3.3V):\\n   - U2: 74LVC541APW (TSSOP-20) for SNES_A0..SNES_A7, /RD, /WR\\n   - U3: 74LVC541APW (TSSOP-20) for SNES_A8..SNES_A15, /ROMSEL, PHI2\\n   - Inputs are 5V tolerant when powered at 3.3V. Propagation delay: ~3.0 ns\\n   - /OE1, /OE2 tied to GND (always enabled)\\n\\n2. Bidirectional Data Bus (SNES <-> Cartridge, 5V <-> 3.3V):\\n   - U4: SN74LVC8T245PWR (TSSOP-24 Dual-Supply Bus Transceiver)\\n   - VCCA = +5V_SNES, VCCB = +3.3V\\n   - Port A = SNES_D0..SNES_D7, Port B = BUS_D0..BUS_D7\\n   - DIR controlled by SNES_/RD: LOW = Read (B -> A), HIGH = Write (A -> B)\\n   - /OE controlled by Cartridge Address Decoder Logic (Active on /ROMSEL or SRAM/Mailbox select)\\n\\n3. Boot Flash ROM (Parallel NOR Flash):\\n   - U5: SST39VF040-70-4C-WHE (512K x 8, TSOP-32, 70ns access time)\\n   - Address inputs connected to buffered 3.3V address bus (BUS_A0..BUS_A18)\\n   - Data outputs connected to buffered 3.3V data bus (BUS_D0..BUS_D7)\\n   - /CE connected to /ROMSEL_3V3\\n   - /OE connected to /RD_3V3\\n   - /WE pulled to 3.3V via 10k resistor (hardware write protected, jumperable for in-system update)"
		(at 30 30 0)
		(effects (font (size 2.2 2.2)) (justify left top))
		(uuid "{uid()}")
	)
"""
make_subsheet("02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch", "Level Shifters & Parallel Flash ROM", s2_content)

# Sheet 3: RP2350 Subsystem
s3_content = f"""
	(text "SHEET 3: RP2350B DUAL-CORE MCU SUBSYSTEM\\n\\nMCU Selection: Raspberry Pi RP2350B (QFN-80)\\n- 48 GPIOs allow dedicated bus taps and rich peripheral connectivity\\n- Dual ARM Cortex-M33 cores @ 150MHz (overclockable to 250MHz+)\\n- 520KB on-chip SRAM: perfectly hosts the Home Assistant Mailbox & dynamic snapshot\\n- 12 PIO State Machines for real-time bus interception, cycle-accurate timing\\n\\nPin Allocation:\\n- GPIO0..GPIO7: BUS_D0..BUS_D7 (Bidirectional data bus for SRAM/mailbox access)\\n- GPIO8..GPIO23: BUS_A0..BUS_A15 (Address bus snooping & decoding)\\n- GPIO24: BUS_/RD, GPIO25: BUS_/WR, GPIO26: BUS_/ROMSEL, GPIO27: BUS_PHI2\\n- GPIO28: BUS_/IRQ (Open-drain to SNES /IRQ line for instant event notification)\\n- GPIO29..GPIO32: SPI0 to ESP32-C6 (SCK, MOSI, MISO, CS)\\n- GPIO33, GPIO34: UART0 to ESP32-C6 (TX, RX)\\n- GPIO35, GPIO36: I2C0 to RTC & Qwiic / STEMMA QT (SDA, SCL)\\n- GPIO37..GPIO40: MicroSD (SPI1: SCK, MOSI, MISO, CS)\\n- GPIO41, GPIO42: RS-485 (TX, RX, DE/RE direction)\\n- GPIO43..GPIO47: Status LEDs, Jumper inputs\\n\\nQSPI Flash Memory:\\n- U7: Winbond W25Q128JVSIQ (16MB / 128Mbit SPI/QSPI NOR Flash, SOIC-8 208mil)\\n- Connected to RP2350 QSPI pins with 10k pullups on CSn\\n\\nOscillator & Power:\\n- Y1: 12.000 MHz SMD 3225 Crystal + 2x 15pF C0G capacitors\\n- Core DVDD (1.1V): Internal regulator with 1uF + 100nF decoupling\\n- IOVDD (3.3V): Decoupled with 100nF per VDD pin + 10uF bulk\\n\\nUSB-C Programming & Diagnostics:\\n- J1: USB4110 / Type-C 16-pin connector with 5.1k pulldowns on CC1/CC2\\n- USBLC6-2SC6 ESD protection on D+/D- + 27 ohm series resistors\\n- BOOTSEL & RESET tactile buttons for UF2 drag-and-drop firmware upgrades"
		(at 30 30 0)
		(effects (font (size 2.2 2.2)) (justify left top))
		(uuid "{uid()}")
	)
"""
make_subsheet("03_RP2350_SUBSYSTEM.kicad_sch", "RP2350B MCU Subsystem & Mailbox", s3_content)

# Sheet 4: ESP32-C6 Subsystem
s4_content = f"""
	(text "SHEET 4: ESP32-C6 WI-FI 6 / BLE / THREAD COPROCESSOR\\n\\nModule: Espressif ESP32-C6-MINI-1 (or ESP32-C6-WROOM-1)\\n- 32-bit RISC-V single-core @ 160MHz, 512KB SRAM, 4MB/8MB Flash\\n- Wi-Fi 6 (2.4 GHz 802.11ax), Bluetooth 5 (LE), IEEE 802.15.4 (Thread/Zigbee)\\n- Built-in certified PCB antenna (placed at the top edge of cartridge with keepout)\\n\\nRole in SNES Smart Home:\\n- Connects to local Wi-Fi and establishes Home Assistant session\\n- Handles TLS encryption, JSON / WebSocket / REST parsing, or MQTT\\n- Translates Home Assistant states into compact binary protocol (SH 01 + CRC16)\\n- Pushes snapshot to RP2350 mailbox via high-speed SPI / UART\\n- Receives command packets from RP2350 and dispatches HA service calls\\n\\nInterface to RP2350:\\n- SPI: ESP_MOSI (GPIO19), ESP_MISO (GPIO20), ESP_SCK (GPIO21), ESP_CS (GPIO18)\\n- UART: ESP_TX (GPIO16) -> RP2350_RX, ESP_RX (GPIO17) <- RP2350_TX\\n- Handshake IRQ: ESP_INT (GPIO22) to alert RP2350 of new states\\n\\nPower & Decoupling:\\n- 3.3V with 10uF ceramic + 100nF ceramic + bulk 47uF tantalum nearby\\n- CHIP_PU with 10k pullup and 1uF delay capacitor for clean power-on reset\\n- Tactile buttons: BOOT (GPIO9) and RESET (CHIP_PU) for firmware flashing\\n- Onboard Status Indicator: WS2812B / SK6812MINI addressable RGB LED"
		(at 30 30 0)
		(effects (font (size 2.2 2.2)) (justify left top))
		(uuid "{uid()}")
	)
"""
make_subsheet("04_ESP32C6_WIFI_IOT.kicad_sch", "ESP32-C6 Wi-Fi 6 / IoT Coprocessor", s4_content)

# Sheet 5: Peripherals & Power
s5_content = f"""
	(text "SHEET 5: PERIPHERALS (MICROSD, RTC, RS-485, I2C) & 5V->3.3V BUCK\\n\\n1. Power Supply Subsystem (High Efficiency Synchronous Buck):\\n   - Input: +5V_SNES from cartridge edge (pins 27, 58)\\n   - Reverse polarity / overcurrent protection: SS34 Schottky diode / PTC resettable fuse (1.5A)\\n   - U9: Silergy SY8089AAAC (or AP62200 / TPS62088) Synchronous Step-Down DC-DC Converter\\n     Package: SOT-23-5, 1.5MHz switching frequency, 94% efficiency, 2.0A continuous output\\n     Inductor: L1 = 2.2uH SMD high-current power inductor (CDRH3D16 or 0805)\\n     Feedback: R1 = 100k, R2 = 22k for calibrated 3.30V VCC rail\\n     Input filter: 10uF 0805 X7R + 47uF low-ESR tantalum\\n     Output filter: 22uF 0805 X7R + 47uF low-ESR tantalum\\n     Much cooler than linear regulators (AMS1117), preserves SNES internal power brick!\\n\\n2. MicroSD Card Socket:\\n   - J4: Push-Pull MicroSD connector, connected via SPI/SDIO to RP2350\\n   - Enables logging, configuration files (wifi.txt / ha_config.json), and sound/ROM assets\\n   - 10k pullups on CS and CMD lines, dedicated 100nF + 10uF decoupling\\n\\n3. High-Precision RTC (Real-Time Clock):\\n   - U10: Maxim DS3231MZ+ (SOIC-8) with integrated MEMS resonator, +-5ppm accuracy\\n   - I2C connected to RP2350 (SCL, SDA with 4.7k pullups to 3.3V)\\n   - BT1: CR1220 3V coin cell battery clip for timekeeping when console is powered off\\n\\n4. RS-485 Industrial / Home Automation Bus:\\n   - U11: SP3485CN-L (SOIC-8, 3.3V half-duplex RS-485 transceiver)\\n   - Connected to RP2350 UART + direction control pin\\n   - J5: 3-pin 3.5mm screw terminal block (A, B, GND) with 120 ohm termination jumper\\n   - SM712 bidirectional TVS diode array for lightning & ESD protection on RS-485 differential lines\\n\\n5. External Sensor / Display Expansion:\\n   - J6: Qwiic / STEMMA QT 4-pin 1.0mm JST-SH connector (GND, 3.3V, SDA, SCL)\\n   - Plug-and-play connection for external BME280, OLED, or radar sensors"
		(at 30 30 0)
		(effects (font (size 2.2 2.2)) (justify left top))
		(uuid "{uid()}")
	)
"""
make_subsheet("05_PERIPHERALS_AND_POWER.kicad_sch", "Peripherals (MicroSD, RTC, RS-485, I2C) & Power", s5_content)

print("Generated all hierarchical KiCad schematics successfully!")
