# PCBWay Fabrication Guidelines for SNES / Super Famicom Cartridge

When configuring the PCB fabrication order on **PCBWay** (or JLCPCB), you must use the following parameters:

---

### 1. Critical Board Specifications

| Parameter | Recommended Value | Reason / Critical Note |
| :--- | :--- | :--- |
| **Layers** | **4 Layers** | Required for 21MHz bus signal integrity, continuous GND plane, and ESP32-C6 RF impedance. |
| **PCB Thickness** | **1.2 mm** (or 1.25 mm) | **CRITICAL:** The original Super Famicom / SNES connector was designed for **1.2 mm** PCBs. Standard 1.6 mm boards are too thick and will damage/warp the console slot blades. 0.8 mm boards are too loose. |
| **Surface Finish** | **ENIG (Electroless Nickel Immersion Gold)** or **Hard Gold (Gold Fingers)** | Abrasion-resistant immersion gold for insertions and oxidation protection over years of use. |
| **Gold Fingers** | **Yes** | Select to apply reinforced gold plating on the 62 edge contacts. |
| **Edge Chamfering / Beveling** | **Yes, 30° Chamfer** (30 degrees) | **CRITICAL:** Creates a 30° angle chamfer on the bottom edge of the contacts, allowing the cartridge to slide smoothly into the console slot without snagging or lifting pads. |
| **Connector Pitch** | **2.50 mm** (Metric) | Verify the footprint uses a 2.50 mm pitch (not 2.54 mm). |
| **Solder Mask** | Blue / Matte Black / Gray | Your preferred aesthetic. |
| **Silkscreen** | White | High legibility text. |
| **Copper Weight** | 1 oz (outer) / 0.5 oz (inner) | Industrial standard. |
| **Material** | FR-4 Standard (Tg 150-170) | High thermal stability during reflow. |

---

### 2. Suggested 4-Layer Stackup (1.2mm)

```text
Layer 1 (Top):     High-speed signals, SMD components, RF antenna
Layer 2 (In1):     Solid Ground Plane (GND)
Layer 3 (In2):     Power Plane (+3.3V Digital + 5V SNES)
Layer 4 (Bottom):  Control signals, secondary bus, rear edge contacts
```

---

### 3. Special Routing & Layout Considerations

1. **ESP32-C6 Antenna:**
   - Position the ESP32-C6-MINI module on the top edge of the cartridge (away from the 62-pin connector).
   - Keep the area under the module antenna completely free of copper (no traces and no GND planes on all 4 layers).
2. **RS-485 Differential:**
   - Route A and B traces as a differential pair with 120 ohm coupled impedance.
3. **Data Bus (D0..D7):**
   - Matched length between the 74LVC buffers and the RP2350/Flash.
4. **Buck Converter Decoupling:**
   - Place C_IN1, L1, and C_OUT1 as close as possible to the SY8089 pins to minimize the 1.5 MHz switching loop.
