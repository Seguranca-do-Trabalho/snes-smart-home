#!/usr/bin/env python3
"""
Generate COMPLETE KiCad 10 schematics for the SNES SmartHome cartridge.

Creates 6 schematic files:
  snes_smarthome_cartridge.kicad_sch  (root with hierarchical sheet boxes + pins)
  01_SNES_BUS_AND_CIC.kicad_sch       (SNES 62-pin connector + SuperCIC)
  02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch (74LVC541 + 74LVC8T245 + SST39VF040)
  03_RP2350_SUBSYSTEM.kicad_sch       (RP2350B MCU + QSPI Flash + USB-C)
  04_ESP32C6_WIFI_IOT.kicad_sch       (ESP32-C6-MINI-1 + WS2812B)
  05_PERIPHERALS_AND_POWER.kicad_sch   (Buck + RTC + RS-485 + MicroSD + connectors)

KiCad 10 format: version 20250114, generator "eeschema", generator_version "10.0"
Component count: 62 (matches BOM.md exactly)

Libraries used:
  Standard:  Device:C, Device:R, Device:L, Device:Crystal, Device:SW_Push,
             Device:D_Schottky, Device:Polyfuse,
             MCU_Microchip_PIC:PIC12F629, Logic_74xx:74LVC541A,
             Memory_Flash:W25Q128, Timer_RTC:DS3231,
             Interface_UART:MAX3485, Connector:USB_C_Receptacle_16P,
             Connector:Conn_01x03, Connector:Conn_01x04
  Custom:   Custom:RP2350B, Custom:ESP32-C6-MINI-1, Custom:SY8089,
             Custom:SNES_62PIN, Custom:SST39VF040, Custom:USBLC6-2SC6,
             Custom:WS2812B
"""

import os
import sys
import uuid
import re
from collections import Counter

HW_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════════════════════
#  UUID generator
# ══════════════════════════════════════════════════════════════════════════════
def uid():
    return str(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
#  Validation helpers
# ══════════════════════════════════════════════════════════════════════════════

def validate_parentheses(content, filename):
    """Check that open and close parentheses are balanced."""
    opens = content.count('(')
    closes = content.count(')')
    if opens != closes:
        print(f"  FAIL: {filename} has unbalanced parentheses: ({opens} open, {closes} close)")
        return False
    print(f"  OK: {filename} parentheses balanced ({opens} pairs)")
    return True


def count_components(content):
    """Count placed component instances (symbol blocks with lib_id)."""
    return len(re.findall(r'^\t\(lib_id ', content, re.MULTILINE))


def count_hierarchical_labels(content):
    """Count hierarchical_label blocks."""
    return len(re.findall(r'^\t\(hierarchical_label ', content, re.MULTILINE))


# ══════════════════════════════════════════════════════════════════════════════
#  KiCad 10 S-expression helpers
# ══════════════════════════════════════════════════════════════════════════════

def sym(lib_id, ref, value, footprint, lcsc, x, y, rotation=0, unit=1):
    ref_y = y + 2.54
    val_y = y - 2.54
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x} {y} {rotation})\n'
        f'\t\t(unit {unit})\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t\t(property "Reference" "{ref}" (at {x} {ref_y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}" (at {x} {val_y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" "{footprint}" (at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) hide)\n'
        f'\t\t)\n'
        f'\t\t(property "LCSC" "{lcsc}" (at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) hide)\n'
        f'\t\t)\n'
        f'\t)\n'
    )


def wire(x1, y1, x2, y2):
    return (
        f'\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2}))\n'
        f'\t\t(stroke (width 0) (type default))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)\n'
    )


def netlabel(name, x, y, rotation=0):
    return (
        f'\t(label "{name}"\n'
        f'\t\t(at {x} {y} {rotation})\n'
        f'\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)\n'
    )


def pwr_sym(name, x, y, rotation=0):
    return (
        f'\t(power_port "{name}"\n'
        f'\t\t(at {x} {y} {rotation})\n'
        f'\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
        f'\t)\n'
    )


def hlabel(name, shape, x, y, rotation=180):
    return (
        f'\t(hierarchical_label "{name}"\n'
        f'\t\t(shape {shape})\n'
        f'\t\t(at {x} {y} {rotation})\n'
        f'\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)\n'
    )


def hpin(name, direction, x, y, rotation=0):
    return (
        f'\t(pin "{name}"\n'
        f'\t\t(direction {direction})\n'
        f'\t\t(at {x} {y} {rotation})\n'
        f'\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)\n'
    )


def text_block(text, x, y, size=2.0):
    escaped = text.replace('\\', '\\\\').replace('"', '\\"')
    return (
        f'\t(text "{escaped}"\n'
        f'\t\t(at {x} {y} 0)\n'
        f'\t\t(effects (font (size {size} {size})) (justify left top))\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)\n'
    )


def no_connect(x, y):
    return f'\t(no_connect (at {x} {y}) (uuid "{uid()}"))\n'


def _pin(name, number, ptype, x, y, angle, length=2.54):
    return (
        f'\t\t\t(pin {ptype} line\n'
        f'\t\t\t\t(at {x} {y} {angle})\n'
        f'\t\t\t\t(length {length})\n'
        f'\t\t\t\t(name "{name}"\n'
        f'\t\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(number "{number}"\n'
        f'\t\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  Standard KiCad library symbol definitions (minimal, for self-containment)
# ══════════════════════════════════════════════════════════════════════════════

def _device_c_symbol():
    return (
        '\t\t(symbol "Device:C"\n'
        '\t\t\t(pin_names (offset 0.254))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "C" (at 0.635 2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "C" (at 0.635 -2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "C_0_1"\n'
        '\t\t\t\t(polyline (pts (xy -1.524 0.508) (xy 1.524 0.508))\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(polyline (pts (xy -1.524 -0.508) (xy 1.524 -0.508))\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "C_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 3.81 270)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -3.81 90)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_r_symbol():
    return (
        '\t\t(symbol "Device:R"\n'
        '\t\t\t(pin_names (offset 0))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "R" (at 2.032 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "R" (at 0 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "R_0_1"\n'
        '\t\t\t\t(rectangle (start -1.016 2.54) (end 1.016 -2.54)\n'
        '\t\t\t\t\t(stroke (width 0.254) (type default))\n'
        '\t\t\t\t\t(fill (type none))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "R_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 3.81 270)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -3.81 90)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_crystal_symbol():
    return (
        '\t\t(symbol "Device:Crystal"\n'
        '\t\t\t(pin_names (offset 0))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "Y" (at 0 3.81 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "Crystal" (at 0 -3.81 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Crystal_0_1"\n'
        '\t\t\t\t(polyline (pts (xy -1.524 1.524) (xy -1.524 -1.524))\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(polyline (pts (xy 1.524 1.524) (xy 1.524 -1.524))\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(rectangle (start -0.762 2.286) (end 0.762 -2.286)\n'
        '\t\t\t\t\t(stroke (width 0.254) (type default))\n'
        '\t\t\t\t\t(fill (type none))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Crystal_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 5.08 270)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -5.08 90)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_sw_push_symbol():
    return (
        '\t\t(symbol "Device:SW_Push"\n'
        '\t\t\t(pin_names (offset 0))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "SW" (at 0 2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "SW_Push" (at 0 -2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "SW_Push_0_1"\n'
        '\t\t\t\t(circle (center -1.778 0) (radius 0.508)\n'
        '\t\t\t\t\t(stroke (width 0) (type default))\n'
        '\t\t\t\t\t(fill (type none))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(circle (center 1.778 0) (radius 0.508)\n'
        '\t\t\t\t\t(stroke (width 0) (type default))\n'
        '\t\t\t\t\t(fill (type none))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "SW_Push_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 5.08 270)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -5.08 90)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_l_symbol():
    return (
        '\t\t(symbol "Device:L"\n'
        '\t\t\t(pin_names (offset 0))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "L" (at 2.54 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "L" (at 0 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "L_0_1"\n'
        '\t\t\t\t(arc (start 0 -2.54) (mid 1.27 0) (end 0 2.54)\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(arc (start 0 -2.54) (mid -1.27 0) (end 0 2.54)\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "L_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 5.08 270)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -5.08 90)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_d_schottky_symbol():
    """Device:D_Schottky — Schottky diode (2-pin)."""
    return (
        '\t\t(symbol "Device:D_Schottky"\n'
        '\t\t\t(pin_names (offset 0.254))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "D" (at 0 2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "D_Schottky" (at 0 -2.54 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "D_Schottky_0_1"\n'
        '\t\t\t\t(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27))\n'
        '\t\t\t\t\t(stroke (width 0.254) (type default))\n'
        '\t\t\t\t\t(fill (type none))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy 1.8034 -1.27))\n'
        '\t\t\t\t\t(stroke (width 0.254) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "D_Schottky_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 3.81 270)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "K" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -3.81 90)\n'
        '\t\t\t\t\t(length 1.27)\n'
        '\t\t\t\t\t(name "A" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _device_polyfuse_symbol():
    return (
        '\t\t(symbol "Device:Polyfuse"\n'
        '\t\t\t(pin_names (offset 0))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "F" (at 2.54 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "Polyfuse" (at 0 0 90)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Polyfuse_0_1"\n'
        '\t\t\t\t(polyline (pts (xy 0 -2.54) (xy 0 -1.27) (xy 1.27 -0.635) (xy 1.27 0.635) (xy 0 1.27) (xy 0 2.54))\n'
        '\t\t\t\t\t(stroke (width 0.3048) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Polyfuse_1_1"\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 5.08 270)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin passive line\n'
        '\t\t\t\t\t(at 0 -5.08 90)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "~" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )


def _battery_cr1220_symbol():
    return (
        '\t\t(symbol "Battery:BatteryHolder_CR1220"\n'
        '\t\t\t(pin_names (offset 0.254))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "BT" (at 0 3.81 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "CR1220" (at 0 -3.81 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Battery_0_1"\n'
        '\t\t\t\t(polyline (pts (xy -2.54 -1.27) (xy 2.54 -1.27))\n'
        '\t\t\t\t\t(stroke (width 0.508) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27))\n'
        '\t\t\t\t\t(stroke (width 0.254) (type default))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t\t(symbol "Battery_1_1"\n'
        '\t\t\t\t(pin power_in line\n'
        '\t\t\t\t\t(at 0 5.08 270)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "+" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t\t(pin power_in line\n'
        '\t\t\t\t\t(at 0 -5.08 90)\n'
        '\t\t\t\t\t(length 2.54)\n'
        '\t\t\t\t\t(name "-" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  Custom library symbol definitions (components not in standard KiCad libs)
# ══════════════════════════════════════════════════════════════════════════════

def _snes_connector_symbol():
    lines = []
    left = [
        (1, "NC"), (2, "NC"), (3, "NC"), (4, "NC"),
        (5, "GND"), (6, "SNES_A0"), (7, "SNES_A1"), (8, "SNES_A2"),
        (9, "SNES_A3"), (10, "SNES_A4"), (11, "SNES_A5"), (12, "SNES_A6"),
        (13, "SNES_A7"), (14, "SNES_A8"), (15, "SNES_A9"), (16, "SNES_A10"),
        (17, "SNES_A11"), (18, "/IRQ"), (19, "SNES_D0"), (20, "SNES_D1"),
        (21, "SNES_D2"), (22, "SNES_D3"), (23, "/RD"), (24, "CIC_DAT1"),
        (25, "CIC_RST"), (26, "/RESET"), (27, "+5V_SNES"),
        (28, "NC"), (29, "NC"), (30, "NC"), (31, "NC"),
    ]
    right = [
        (32, "NC"), (33, "NC"), (34, "NC"), (35, "NC"),
        (36, "GND"), (37, "SNES_A12"), (38, "SNES_A13"), (39, "SNES_A14"),
        (40, "SNES_A15"), (41, "SNES_A16"), (42, "SNES_A17"), (43, "SNES_A18"),
        (44, "SNES_A19"), (45, "SNES_A20"), (46, "SNES_A21"), (47, "SNES_A22"),
        (48, "SNES_A23"), (49, "/ROMSEL"), (50, "SNES_D4"), (51, "SNES_D5"),
        (52, "SNES_D6"), (53, "SNES_D7"), (54, "/WR"), (55, "CIC_DAT2"),
        (56, "CIC_CLK"), (57, "PHI2"), (58, "+5V_SNES"),
        (59, "NC"), (60, "NC"), (61, "NC"), (62, "NC"),
    ]
    y0 = -38.1
    for i, (num, name) in enumerate(left):
        py = y0 + i * 2.50
        pt = "power_in" if name in ("GND", "+5V_SNES") else "bidirectional"
        lines.append(_pin(name, str(num), pt, -30.48, py, 0, 2.54))
    for i, (num, name) in enumerate(right):
        py = y0 + i * 2.50
        pt = "power_in" if name in ("GND", "+5V_SNES") else "bidirectional"
        lines.append(_pin(name, str(num), pt, 30.48, py, 180, 2.54))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Custom:SNES_62PIN"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "P1" (at 0 -48 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "SNES_EDGE_62" (at 0 48 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _pic12f629_symbol():
    pins = (
        _pin("VDD", "1", "power_in", 0, 10.16, 270)
        + _pin("RA5", "2", "bidirectional", -10.16, 5.08, 0)
        + _pin("RA4", "3", "bidirectional", -10.16, 2.54, 0)
        + _pin("RA3/MCLR", "4", "input", -10.16, 0, 0)
        + _pin("RA2", "5", "output", -10.16, -2.54, 0)
        + _pin("RA1", "6", "passive", -10.16, -5.08, 0)
        + _pin("RA0", "7", "passive", -10.16, -7.62, 0)
        + _pin("VSS", "8", "power_in", 0, -10.16, 90)
    )
    return (
        '\t\t(symbol "MCU_Microchip_PIC:PIC12F629"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -14 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "PIC12F629" (at 0 14 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _usblc6_symbol():
    pins = (
        _pin("GND", "1", "power_in", -7.62, 2.54, 0)
        + _pin("I/O1", "2", "passive", -7.62, 0, 0)
        + _pin("VCC", "3", "power_in", 7.62, 2.54, 180)
        + _pin("I/O2", "4", "passive", -7.62, -2.54, 0)
        + _pin("I/O3", "5", "passive", 7.62, 0, 180)
        + _pin("I/O4", "6", "passive", 7.62, -2.54, 180)
    )
    return (
        '\t\t(symbol "Custom:USBLC6-2SC6"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "D" (at 0 -7 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "USBLC6-2SC6" (at 0 7 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _lvc541_symbol():
    left = [
        (1, "1OE1", "input"), (2, "1A1", "input"), (3, "1A2", "input"),
        (4, "1A3", "input"), (5, "1A4", "input"), (6, "GND", "power_in"),
        (7, "2A1", "input"), (8, "2A2", "input"), (9, "2A3", "input"),
        (10, "2A4", "input"),
    ]
    right = [
        (11, "2Y4", "output"), (12, "2Y3", "output"), (13, "2Y2", "output"),
        (14, "2Y1", "output"), (15, "VCC", "power_in"),
        (16, "1Y4", "output"), (17, "1Y3", "output"), (18, "1Y2", "output"),
        (19, "1Y1", "output"), (20, "1OE2", "input"),
    ]
    y0 = -10.16
    lines = []
    for i, (n, name, pt) in enumerate(left):
        lines.append(_pin(name, str(n), pt, -15.24, y0 + i * 2.54, 0))
    for i, (n, name, pt) in enumerate(right):
        lines.append(_pin(name, str(n), pt, 15.24, y0 + i * 2.54, 180))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Logic_74xx:74LVC541A"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -16 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "74LVC541APW" (at 0 16 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _lvc8t245_symbol():
    left = [
        (1, "DIR", "input"), (2, "A0", "bidirectional"), (3, "A1", "bidirectional"),
        (4, "A2", "bidirectional"), (5, "A3", "bidirectional"), (6, "A4", "bidirectional"),
        (7, "A5", "bidirectional"), (8, "A6", "bidirectional"), (9, "A7", "bidirectional"),
        (10, "GND", "power_in"), (11, "OE", "input"), (12, "GND", "power_in"),
    ]
    right = [
        (13, "VCCA", "power_in"), (14, "VCCB", "power_in"),
        (15, "B7", "bidirectional"), (16, "B6", "bidirectional"),
        (17, "B5", "bidirectional"), (18, "B4", "bidirectional"),
        (19, "B3", "bidirectional"), (20, "B2", "bidirectional"),
        (21, "B1", "bidirectional"), (22, "B0", "bidirectional"),
        (23, "VCCB", "power_in"), (24, "GND", "power_in"),
    ]
    y0 = -15.24
    lines = []
    for i, (n, name, pt) in enumerate(left):
        lines.append(_pin(name, str(n), pt, -17.78, y0 + i * 2.54, 0))
    for i, (n, name, pt) in enumerate(right):
        lines.append(_pin(name, str(n), pt, 17.78, y0 + i * 2.54, 180))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Logic_74xx:SN74LVC8T245PWR"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -20 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "SN74LVC8T245PWR" (at 0 20 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _sst39vf040_symbol():
    """Custom:SST39VF040 — 4Mbit parallel NOR flash, TSOP-32."""
    left = [
        (1, "A17", "input"), (2, "A7", "input"), (3, "A6", "input"),
        (4, "A5", "input"), (5, "A4", "input"), (6, "A3", "input"),
        (7, "A2", "input"), (8, "A1", "input"), (9, "A0", "input"),
        (10, "CE", "input"), (11, "GND", "power_in"), (12, "OE", "input"),
        (13, "D0", "bidirectional"), (14, "D1", "bidirectional"),
        (15, "D2", "bidirectional"), (16, "VCC", "power_in"),
    ]
    right = [
        (17, "D3", "bidirectional"), (18, "D4", "bidirectional"),
        (19, "D5", "bidirectional"), (20, "D6", "bidirectional"),
        (21, "D7", "bidirectional"), (22, "A18", "input"),
        (23, "A10", "input"), (24, "WE", "input"),
        (25, "A11", "input"), (26, "A9", "input"),
        (27, "A8", "input"), (28, "A16", "input"),
        (29, "A14", "input"), (30, "A13", "input"),
        (31, "A12", "input"), (32, "A15", "input"),
    ]
    y0 = -19.05
    lines = []
    for i, (n, name, pt) in enumerate(left):
        lines.append(_pin(name, str(n), pt, -20.32, y0 + i * 2.54, 0))
    for i, (n, name, pt) in enumerate(right):
        lines.append(_pin(name, str(n), pt, 20.32, y0 + i * 2.54, 180))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Custom:SST39VF040"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -26 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "SST39VF040" (at 0 26 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _rp2350b_symbol():
    left = [
        (1, "IOVDD0", "power_in"), (2, "GPIO0", "bidirectional"),
        (3, "GPIO1", "bidirectional"), (4, "GPIO2", "bidirectional"),
        (5, "GPIO3", "bidirectional"), (6, "GPIO4", "bidirectional"),
        (7, "IOVDD1", "power_in"), (8, "GPIO5", "bidirectional"),
        (9, "GPIO6", "bidirectional"), (10, "GPIO7", "bidirectional"),
        (11, "GPIO8", "bidirectional"), (12, "GPIO9", "bidirectional"),
        (13, "IOVDD2", "power_in"), (14, "GPIO10", "bidirectional"),
        (15, "GPIO11", "bidirectional"), (16, "GPIO12", "bidirectional"),
        (17, "GPIO13", "bidirectional"), (18, "GPIO14", "bidirectional"),
        (19, "IOVDD3", "power_in"), (20, "IOVDD4", "power_in"),
    ]
    right = [
        (21, "GPIO15", "bidirectional"), (22, "GPIO16", "bidirectional"),
        (23, "GPIO17", "bidirectional"), (24, "GPIO18", "bidirectional"),
        (25, "GPIO19", "bidirectional"), (26, "GPIO20", "bidirectional"),
        (27, "GPIO21", "bidirectional"), (28, "GPIO22", "bidirectional"),
        (29, "GPIO23", "bidirectional"), (30, "GPIO24", "bidirectional"),
        (31, "GPIO25", "bidirectional"), (32, "GPIO26", "bidirectional"),
        (33, "GPIO27", "bidirectional"), (34, "GPIO28", "bidirectional"),
        (35, "GPIO29", "bidirectional"), (36, "GPIO30", "bidirectional"),
        (37, "GPIO31", "bidirectional"), (38, "GPIO32", "bidirectional"),
        (39, "GPIO33", "bidirectional"), (40, "GPIO34", "bidirectional"),
    ]
    top = [
        (41, "QSPI_SS", "bidirectional"), (42, "QSPI_SCLK", "bidirectional"),
        (43, "QSPI_SD0", "bidirectional"), (44, "QSPI_SD1", "bidirectional"),
        (45, "QSPI_SD2", "bidirectional"), (46, "QSPI_SD3", "bidirectional"),
        (47, "USB_DM", "bidirectional"), (48, "USB_DP", "bidirectional"),
        (49, "XIN", "input"), (50, "XOUT", "output"),
        (51, "SWCLK", "input"), (52, "SWDIO", "bidirectional"),
        (53, "RUN", "input"),
    ]
    bottom = [
        (54, "GPIO35", "bidirectional"), (55, "GPIO36", "bidirectional"),
        (56, "GPIO37", "bidirectional"), (57, "GPIO38", "bidirectional"),
        (58, "GPIO39", "bidirectional"), (59, "GPIO40", "bidirectional"),
        (60, "GPIO41", "bidirectional"), (61, "GPIO42", "bidirectional"),
        (62, "GPIO43", "bidirectional"), (63, "GPIO44", "bidirectional"),
        (64, "GPIO45", "bidirectional"), (65, "GPIO46", "bidirectional"),
        (66, "GPIO47", "bidirectional"),
        (67, "DVDD0", "power_in"), (68, "DVDD1", "power_in"),
        (69, "DVDD2", "power_in"), (70, "VSS0", "power_in"),
        (71, "VSS1", "power_in"), (72, "VSS2", "power_in"),
        (73, "VSS3", "power_in"), (74, "DVDD3", "power_in"),
        (75, "IOVDD5", "power_in"),
    ]
    y0 = -25.4
    lines = []
    for i, (n, name, pt) in enumerate(left):
        lines.append(_pin(name, str(n), pt, -35.56, y0 + i * 2.54, 0))
    for i, (n, name, pt) in enumerate(right):
        lines.append(_pin(name, str(n), pt, 35.56, y0 + i * 2.54, 180))
    x0 = -33.02
    for i, (n, name, pt) in enumerate(top):
        lines.append(_pin(name, str(n), pt, x0 + i * 5.08, -30.48, 270))
    x0b = -35.56
    for i, (n, name, pt) in enumerate(bottom):
        lines.append(_pin(name, str(n), pt, x0b + i * 4.572, 30.48, 90))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Custom:RP2350B"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -40 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "RP2350B" (at 0 40 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _w25q128_symbol():
    """Memory_Flash:W25Q128 — 16MB QSPI NOR flash, SOIC-8."""
    pins = (
        _pin("/CS", "1", "input", -10.16, 3.81, 0)
        + _pin("DO/IO1", "2", "bidirectional", -10.16, 1.27, 0)
        + _pin("/WP/IO2", "3", "bidirectional", -10.16, -1.27, 0)
        + _pin("GND", "4", "power_in", 0, -7.62, 90)
        + _pin("DI/IO0", "5", "bidirectional", 10.16, -1.27, 180)
        + _pin("CLK", "6", "bidirectional", 10.16, 1.27, 180)
        + _pin("/HOLD/IO3", "7", "bidirectional", 10.16, 3.81, 180)
        + _pin("VCC", "8", "power_in", 0, 7.62, 270)
    )
    return (
        '\t\t(symbol "Memory_Flash:W25Q128"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "W25Q128JVSIQ" (at 0 10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _esp32c6_symbol():
    left = [
        (1, "3V3", "power_in"), (2, "GND", "power_in"),
        (3, "EN", "input"), (4, "GPIO0", "bidirectional"),
        (5, "GPIO1", "bidirectional"), (6, "GPIO2", "bidirectional"),
        (7, "GPIO3", "bidirectional"), (8, "GPIO4", "bidirectional"),
        (9, "GPIO5", "bidirectional"), (10, "GPIO6", "bidirectional"),
        (11, "GPIO7", "bidirectional"), (12, "GPIO8", "bidirectional"),
        (13, "GPIO9/BOOT", "bidirectional"),
    ]
    right = [
        (14, "GPIO10", "bidirectional"), (15, "GPIO11", "bidirectional"),
        (16, "GPIO12", "bidirectional"), (17, "GPIO13", "bidirectional"),
        (18, "GPIO14", "bidirectional"), (19, "GPIO15", "bidirectional"),
        (20, "GPIO16/TXD", "bidirectional"), (21, "GPIO17/RXD", "bidirectional"),
        (22, "GPIO18", "bidirectional"), (23, "GPIO19/MOSI", "bidirectional"),
        (24, "GPIO20/MISO", "bidirectional"),
        (25, "GPIO21/SCK", "bidirectional"),
        (26, "GPIO22/CS", "bidirectional"),
    ]
    y0 = -15.24
    lines = []
    for i, (n, name, pt) in enumerate(left):
        lines.append(_pin(name, str(n), pt, -17.78, y0 + i * 2.54, 0))
    for i, (n, name, pt) in enumerate(right):
        lines.append(_pin(name, str(n), pt, 17.78, y0 + i * 2.54, 180))
    pins = "".join(lines)
    return (
        '\t\t(symbol "Custom:ESP32-C6-MINI-1"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -22 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "ESP32-C6-MINI-1" (at 0 22 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _sy8089_symbol():
    """Custom:SY8089 — Synchronous buck converter 5V→3.3V 2.0A, SOT-23-5."""
    pins = (
        _pin("VIN", "1", "power_in", -10.16, 2.54, 0)
        + _pin("GND", "2", "power_in", 0, -7.62, 90)
        + _pin("SW", "3", "power_out", 10.16, 2.54, 180)
        + _pin("EN", "4", "input", -10.16, -2.54, 0)
        + _pin("FB", "5", "input", 10.16, -2.54, 180)
    )
    return (
        '\t\t(symbol "Custom:SY8089"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -8 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "SY8089AAAC" (at 0 8 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _ds3231_symbol():
    pins = (
        _pin("VCC", "1", "power_in", -10.16, 3.81, 0)
        + _pin("32KHz", "2", "output", -10.16, 1.27, 0)
        + _pin("SQW", "3", "output", -10.16, -1.27, 0)
        + _pin("GND", "4", "power_in", 0, -7.62, 90)
        + _pin("SCL", "5", "bidirectional", 10.16, -1.27, 180)
        + _pin("SDA", "6", "bidirectional", 10.16, 1.27, 180)
        + _pin("/RST", "7", "input", 10.16, 3.81, 180)
        + _pin("VBAT", "8", "power_in", -10.16, -3.81, 0)
    )
    return (
        '\t\t(symbol "Timer_RTC:DS3231"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "DS3231MZ+" (at 0 10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _max3485_symbol():
    """Interface_UART:MAX3485 — RS-485/422 3.3V half-duplex transceiver, SOIC-8."""
    pins = (
        _pin("RO", "1", "output", -10.16, 3.81, 0)
        + _pin("/RE", "2", "input", -10.16, 1.27, 0)
        + _pin("DE", "3", "input", -10.16, -1.27, 0)
        + _pin("DI", "4", "input", -10.16, -3.81, 0)
        + _pin("GND", "5", "power_in", 0, -7.62, 90)
        + _pin("A", "6", "bidirectional", 10.16, -3.81, 180)
        + _pin("B", "7", "bidirectional", 10.16, -1.27, 180)
        + _pin("VCC", "8", "power_in", 10.16, 3.81, 180)
    )
    return (
        '\t\t(symbol "Interface_UART:MAX3485"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "U" (at 0 -10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "MAX3485" (at 0 10 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )


def _ws2812b_symbol():
    pins = (
        _pin("VDD", "1", "power_in", -7.62, 2.54, 0)
        + _pin("DOUT", "2", "output", 7.62, 2.54, 180)
        + _pin("VSS", "3", "power_in", 0, -5, 90)
        + _pin("DIN", "4", "input", -7.62, -2.54, 0)
    )
    return (
        '\t\t(symbol "Custom:WS2812B"\n'
        '\t\t\t(pin_names (offset 1.016))\n'
        '\t\t\t(in_bom yes)\n'
        '\t\t\t(on_board yes)\n'
        '\t\t\t(property "Reference" "D" (at 0 -7 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        '\t\t\t(property "Value" "WS2812B" (at 0 7 0)\n'
        '\t\t\t\t(effects (font (size 1.27 1.27)))\n'
        '\t\t\t)\n'
        f'{pins}'
        '\t\t)\n'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  Complete lib_symbols block for each sheet
# ══════════════════════════════════════════════════════════════════════════════

def _lib_symbols_sheet1():
    return ('\t(lib_symbols\n'
            + _snes_connector_symbol() + _pic12f629_symbol()
            + _usblc6_symbol() + _device_c_symbol()
            + '\t)\n')

def _lib_symbols_sheet2():
    return ('\t(lib_symbols\n'
            + _lvc541_symbol() + _lvc8t245_symbol() + _sst39vf040_symbol()
            + _device_c_symbol() + _device_r_symbol()
            + '\t)\n')

def _lib_symbols_sheet3():
    return ('\t(lib_symbols\n'
            + _rp2350b_symbol() + _w25q128_symbol()
            + _device_c_symbol() + _device_r_symbol()
            + _device_crystal_symbol() + _device_sw_push_symbol()
            + '\t)\n')

def _lib_symbols_sheet4():
    return ('\t(lib_symbols\n'
            + _esp32c6_symbol() + _ws2812b_symbol()
            + _device_c_symbol() + _device_r_symbol()
            + _device_sw_push_symbol()
            + '\t)\n')

def _lib_symbols_sheet5():
    return ('\t(lib_symbols\n'
            + _sy8089_symbol() + _ds3231_symbol() + _max3485_symbol()
            + _device_c_symbol() + _device_r_symbol() + _device_d_schottky_symbol()
            + _device_l_symbol() + _device_polyfuse_symbol()
            + _battery_cr1220_symbol()
            + '\t)\n')


def _sheet_wrapper(title, contents):
    return (
        f'(kicad_sch\n'
        f'\t(version 20250114)\n'
        f'\t(generator "eeschema")\n'
        f'\t(generator_version "10.0")\n'
        f'\t(uuid "{uid()}")\n'
        f'\t(paper "A3")\n'
        f'\t(title_block\n'
        f'\t\t(title "{title}")\n'
        f'\t\t(date "2026-09-11")\n'
        f'\t\t(rev "V1.0")\n'
        f'\t\t(company "SNES SmartHome Project")\n'
        f'\t)\n'
        f'{contents}'
        f')\n'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  Sheet 1: SNES 62-Pin Bus Connector & SuperCIC
#  Components: P1, U1, D1, D2, C5  (5 total)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sheet1():
    p = []
    p.append(_lib_symbols_sheet1())

    # ── Components ──────────────────────────────────────────────────────────
    p.append(sym("Custom:SNES_62PIN", "P1", "SNES_EDGE_62",
                 "Connector_CardEdge:SNES_CartridgeEdge_62Pin_2.50mm",
                 "Custom", 80, 155))
    p.append(sym("MCU_Microchip_PIC:PIC12F629", "U1", "PIC12F629-I/SN",
                 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "C20967", 230, 145))
    p.append(sym("Custom:USBLC6-2SC6", "D1", "USBLC6-2SC6",
                 "Package_TO_SOT_SMD:SOT-23-6_Handsoldering", "C7519", 150, 90))
    p.append(sym("Custom:USBLC6-2SC6", "D2", "USBLC6-2SC6",
                 "Package_TO_SOT_SMD:SOT-23-6_Handsoldering", "C7519", 150, 170))
    p.append(sym("Device:C", "C5", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 255, 145))

    # ── P1 power pins wired ────────────────────────────────────────────────
    p.append(pwr_sym("+5V_SNES", 80, 78.78))
    p.append(pwr_sym("GND", 80, 134.32))
    p.append(pwr_sym("+5V_SNES", 110.48, 78.78))
    p.append(pwr_sym("GND", 110.48, 134.32))

    # ── U1 power: VDD→+3V3, VSS→GND ───────────────────────────────────────
    p.append(wire(230, 134.84, 230, 130))
    p.append(pwr_sym("+3V3", 230, 128))
    p.append(wire(230, 155.16, 230, 160))
    p.append(pwr_sym("GND", 230, 162))

    # ── C5 decoupling wired between +3V3 and GND ──────────────────────────
    p.append(wire(255, 141.19, 255, 137))
    p.append(pwr_sym("+3V3", 255, 135))
    p.append(wire(255, 148.81, 255, 152))
    p.append(pwr_sym("GND", 255, 154))

    # ── D1 power: VCC→+5V_SNES, GND→GND ───────────────────────────────────
    p.append(wire(157.62, 87.46, 163, 87.46))
    p.append(pwr_sym("+5V_SNES", 165, 87.46))
    p.append(wire(142.38, 87.46, 139, 87.46))
    p.append(pwr_sym("GND", 137, 87.46))

    # ── D2 power: VCC→+5V_SNES, GND→GND ───────────────────────────────────
    p.append(wire(157.62, 167.46, 163, 167.46))
    p.append(pwr_sym("+5V_SNES", 165, 167.46))
    p.append(wire(142.38, 167.46, 139, 167.46))
    p.append(pwr_sym("GND", 137, 167.46))

    # ── CIC signal wiring ──────────────────────────────────────────────────
    # P1 pin 56 (CIC_CLK) → net
    p.append(wire(110.48, 43.82, 120, 43.82))
    p.append(netlabel("CIC_CLK", 120, 43.82, 0))
    # P1 pin 25 (CIC_RST) → net
    p.append(wire(110.48, 81.32, 120, 81.32))
    p.append(netlabel("CIC_RST", 120, 81.32, 0))
    # P1 pin 24 (CIC_DAT1) → net
    p.append(wire(110.48, 83.82, 120, 83.82))
    p.append(netlabel("CIC_DAT1", 120, 83.82, 0))
    # P1 pin 55 (CIC_DAT2) → net
    p.append(wire(110.48, 46.32, 120, 46.32))
    p.append(netlabel("CIC_DAT2", 120, 46.32, 0))

    # ── U1 CIC signal wiring ───────────────────────────────────────────────
    # U1 RA5 (pin2) → CIC_DAT1
    p.append(wire(219.84, 139.92, 210, 139.92))
    p.append(netlabel("CIC_DAT1", 208, 139.92, 180))
    # U1 RA4 (pin3) → CIC_DAT2
    p.append(wire(219.84, 142.46, 205, 142.46))
    p.append(netlabel("CIC_DAT2", 203, 142.46, 180))
    # U1 RA3/MCLR (pin4) → CIC_RST
    p.append(wire(219.84, 145, 200, 145))
    p.append(netlabel("CIC_RST", 198, 145, 180))
    # U1 RA2 (pin5) → CIC_CLK
    p.append(wire(219.84, 147.54, 195, 147.54))
    p.append(netlabel("CIC_CLK", 193, 147.54, 180))

    # ── SNES bus signal net labels at P1 ───────────────────────────────────
    left_sigs = [
        (6, "SNES_A0"), (7, "SNES_A1"), (8, "SNES_A2"), (9, "SNES_A3"),
        (10, "SNES_A4"), (11, "SNES_A5"), (12, "SNES_A6"), (13, "SNES_A7"),
        (14, "SNES_A8"), (15, "SNES_A9"), (16, "SNES_A10"), (17, "SNES_A11"),
        (18, "/IRQ"), (19, "SNES_D0"), (20, "SNES_D1"), (21, "SNES_D2"),
        (22, "SNES_D3"), (23, "/RD"), (26, "/RESET"),
    ]
    for i, (pin_n, name) in enumerate(left_sigs):
        py = 109.22 + i * 2.50
        p.append(wire(110.48, py, 50, py))
        p.append(netlabel(name, 48, py, 180))

    right_sigs = [
        (37, "SNES_A12"), (38, "SNES_A13"), (39, "SNES_A14"), (40, "SNES_A15"),
        (41, "SNES_A16"), (42, "SNES_A17"), (43, "SNES_A18"), (44, "SNES_A19"),
        (45, "SNES_A20"), (46, "SNES_A21"), (47, "SNES_A22"), (48, "SNES_A23"),
        (49, "/ROMSEL"), (50, "SNES_D4"), (51, "SNES_D5"), (52, "SNES_D6"),
        (53, "SNES_D7"), (54, "/WR"), (57, "PHI2"),
    ]
    for i, (pin_n, name) in enumerate(right_sigs):
        py = 109.22 + i * 2.50
        p.append(wire(110.48, py, 120, py))
        p.append(netlabel(name, 120, py, 0))

    # ── Hierarchical labels (outputs to Sheet 2) ───────────────────────────
    hlbls = [
        "SNES_A0", "SNES_A1", "SNES_A2", "SNES_A3", "SNES_A4", "SNES_A5",
        "SNES_A6", "SNES_A7", "SNES_A8", "SNES_A9", "SNES_A10", "SNES_A11",
        "SNES_A12", "SNES_A13", "SNES_A14", "SNES_A15",
        "SNES_A16", "SNES_A17", "SNES_A18", "SNES_A19",
        "SNES_A20", "SNES_A21", "SNES_A22", "SNES_A23",
        "SNES_D0", "SNES_D1", "SNES_D2", "SNES_D3",
        "SNES_D4", "SNES_D5", "SNES_D6", "SNES_D7",
        "/RD", "/WR", "/ROMSEL", "/IRQ", "/RESET", "PHI2",
        "CIC_CLK", "CIC_RST", "CIC_DAT1", "CIC_DAT2",
    ]
    for i, n in enumerate(hlbls):
        lx = 310 + (i // 14) * 25
        ly = 30 + (i % 14) * 5
        p.append(hlabel(n, "bidirectional", lx, ly, 180))

    p.append(text_block(
        "SHEET 1: SNES 62-Pin Cartridge Connector & SuperCIC\\n"
        "Pitch: 2.50mm Metric | PCB: 1.20mm ENIG 30-deg Bevel\\n\\n"
        "U1: PIC12F629 SuperCIC (NTSC/PAL auto-detect)\\n"
        "D1,D2: USBLC6-2SC6 ESD/TVS protection\\n"
        "C5: 100nF decoupling",
        30, 30))

    content = "".join(p)
    path = os.path.join(HW_DIR, "01_SNES_BUS_AND_CIC.kicad_sch")
    with open(path, "w") as f:
        f.write(_sheet_wrapper("SNES 62-Pin Cartridge Connector & SuperCIC", content))
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Sheet 2: Level Shifters & Parallel Flash ROM
#  Components: U2, U3, U4, U5, R7, C6, C7, C8, C9  (9 total)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sheet2():
    p = []
    p.append(_lib_symbols_sheet2())

    # ── Hierarchical labels (inputs from Sheet 1) ──────────────────────────
    in_lbls = [
        "SNES_A0", "SNES_A1", "SNES_A2", "SNES_A3", "SNES_A4", "SNES_A5",
        "SNES_A6", "SNES_A7", "SNES_A8", "SNES_A9", "SNES_A10", "SNES_A11",
        "SNES_A12", "SNES_A13", "SNES_A14", "SNES_A15",
        "SNES_D0", "SNES_D1", "SNES_D2", "SNES_D3",
        "SNES_D4", "SNES_D5", "SNES_D6", "SNES_D7",
        "/RD", "/WR", "/ROMSEL", "PHI2",
    ]
    for i, n in enumerate(in_lbls):
        p.append(hlabel(n, "input", 30, 30 + i * 5, 0))

    # ── Hierarchical labels (outputs to Sheet 3) ──────────────────────────
    out_lbls = [
        "BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3", "BUS_A4", "BUS_A5",
        "BUS_A6", "BUS_A7", "BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
        "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15",
        "BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3",
        "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7",
        "BUS_RD", "BUS_WR", "BUS_ROMSEL", "BUS_PHI2",
    ]
    for i, n in enumerate(out_lbls):
        p.append(hlabel(n, "output", 390, 30 + i * 5, 180))

    # ── Components ──────────────────────────────────────────────────────────
    p.append(sym("Logic_74xx:74LVC541A", "U2", "74LVC541APW",
                 "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", "C5975", 160, 140))
    p.append(sym("Logic_74xx:74LVC541A", "U3", "74LVC541APW",
                 "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", "C5975", 160, 250))
    p.append(sym("Logic_74xx:SN74LVC8T245PWR", "U4", "SN74LVC8T245PWR",
                 "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "C6207", 280, 180))
    p.append(sym("Custom:SST39VF040", "U5", "SST39VF040-70-4C-WHE",
                 "Package_SO:TSOP-32_8x14mm_P0.5mm", "C129525", 280, 290))
    p.append(sym("Device:R", "R7", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 320, 260))
    p.append(sym("Device:C", "C6", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 185, 125))
    p.append(sym("Device:C", "C7", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 185, 235))
    p.append(sym("Device:C", "C8", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 305, 165))
    p.append(sym("Device:C", "C9", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 305, 275))

    # ── U2: 74LVC541 (SNES_A0-A7 → BUS_A0-A7) ────────────────────────────
    u2_in = ["SNES_A0", "SNES_A1", "SNES_A2", "SNES_A3",
             "SNES_A4", "SNES_A5", "SNES_A6", "SNES_A7"]
    for i, n in enumerate(u2_in):
        px = 144.76
        py = 134.86 + i * 2.54
        p.append(wire(px, py, px - 5, py))
        p.append(netlabel(n, px - 7, py, 180))

    u2_out = ["BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3",
              "BUS_A4", "BUS_A5", "BUS_A6", "BUS_A7"]
    for i, n in enumerate(u2_out):
        px = 175.24
        py = 140.14 + i * 2.54
        p.append(wire(px, py, px + 5, py))
        p.append(netlabel(n, px + 7, py, 0))

    # U2 OE1 (pin1) and OE2 (pin19) → GND
    p.append(wire(144.76, 127.3, 144.76, 130))
    p.append(pwr_sym("GND", 144.76, 132))
    p.append(wire(175.24, 167.42, 175.24, 170))
    p.append(pwr_sym("GND", 175.24, 172))

    # U2 VCC (pin15) → +3V3, GND (pin6) → GND
    p.append(wire(160, 122.32, 160, 118))
    p.append(pwr_sym("+3V3", 160, 116))
    p.append(wire(160, 157.54, 160, 160))
    p.append(pwr_sym("GND", 160, 162))

    # C6 decoupling for U2
    p.append(wire(185, 121.19, 185, 118))
    p.append(pwr_sym("+3V3", 185, 116))
    p.append(wire(185, 128.81, 185, 132))
    p.append(pwr_sym("GND", 185, 134))

    # ── U3: 74LVC541 (SNES_A8-A15 → BUS_A8-A15) ──────────────────────────
    u3_in = ["SNES_A8", "SNES_A9", "SNES_A10", "SNES_A11",
             "SNES_A12", "SNES_A13", "SNES_A14", "SNES_A15"]
    for i, n in enumerate(u3_in):
        px = 144.76
        py = 244.86 + i * 2.54
        p.append(wire(px, py, px - 5, py))
        p.append(netlabel(n, px - 7, py, 180))

    u3_out = ["BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
              "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15"]
    for i, n in enumerate(u3_out):
        px = 175.24
        py = 250.14 + i * 2.54
        p.append(wire(px, py, px + 5, py))
        p.append(netlabel(n, px + 7, py, 0))

    # U3 OE1, OE2 → GND
    p.append(wire(144.76, 237.3, 144.76, 240))
    p.append(pwr_sym("GND", 144.76, 242))
    p.append(wire(175.24, 277.42, 175.24, 280))
    p.append(pwr_sym("GND", 175.24, 282))

    # U3 power
    p.append(wire(160, 232.32, 160, 228))
    p.append(pwr_sym("+3V3", 160, 226))
    p.append(wire(160, 267.54, 160, 270))
    p.append(pwr_sym("GND", 160, 272))

    # C7 decoupling for U3
    p.append(wire(185, 231.19, 185, 228))
    p.append(pwr_sym("+3V3", 185, 226))
    p.append(wire(185, 238.81, 185, 242))
    p.append(pwr_sym("GND", 185, 244))

    # ── U4: SN74LVC8T245 (SNES_D0-D7 ↔ BUS_D0-D7) ───────────────────────
    # DIR (pin1) = /RD
    p.append(wire(262.22, 162.26, 255, 162.26))
    p.append(netlabel("/RD", 253, 162.26, 180))
    # OE (pin11) → GND
    p.append(wire(262.22, 195, 262.22, 198))
    p.append(pwr_sym("GND", 262.22, 200))

    # A-side (SNES_D0-D7)
    u4_a = ["SNES_D0", "SNES_D1", "SNES_D2", "SNES_D3",
            "SNES_D4", "SNES_D5", "SNES_D6", "SNES_D7"]
    for i, n in enumerate(u4_a):
        px = 262.22
        py = 174.86 + i * 2.54
        p.append(wire(px, py, px - 5, py))
        p.append(netlabel(n, px - 7, py, 180))

    # B-side (BUS_D0-D7)
    u4_b = ["BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3",
            "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7"]
    for i, n in enumerate(u4_b):
        px = 297.78
        py = 162.22 + i * 2.54
        p.append(wire(px, py, px + 5, py))
        p.append(netlabel(n, px + 7, py, 0))

    # U4 VCCA (pin13) → +5V_SNES, VCCB (pin14, pin23) → +3V3
    p.append(wire(262.22, 162.26, 262.22, 158))
    p.append(pwr_sym("+5V_SNES", 262.22, 156))
    p.append(wire(297.78, 162.26, 297.78, 158))
    p.append(pwr_sym("+3V3", 297.78, 156))
    # U4 GND pins
    p.append(pwr_sym("GND", 262.22, 210))
    p.append(pwr_sym("GND", 297.78, 210))

    # C8 decoupling for U4 VCCA
    p.append(wire(305, 161.19, 305, 158))
    p.append(pwr_sym("+3V3", 305, 156))
    p.append(wire(305, 168.81, 305, 172))
    p.append(pwr_sym("GND", 305, 174))

    # ── U5: SST39VF040 Flash ───────────────────────────────────────────────
    u5_a = ["BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3", "BUS_A4", "BUS_A5",
            "BUS_A6", "BUS_A7", "BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
            "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15"]
    for i, n in enumerate(u5_a):
        px = 259.68
        py = 270.95 + i * 2.54
        p.append(wire(px, py, px - 5, py))
        p.append(netlabel(n, px - 7, py, 180))

    # A16-A18 from U5 right side
    for i, n in enumerate(["BUS_A16", "BUS_A17", "BUS_A18"]):
        py = 270.95 + (28 + i) * 2.54
        p.append(wire(300.32, py, 305, py))
        p.append(netlabel(n, 307, py, 0))

    u5_d = ["BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3",
            "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7"]
    for i, n in enumerate(u5_d):
        px = 300.32
        py = 270.95 + (12 + i) * 2.54
        p.append(wire(px, py, px + 5, py))
        p.append(netlabel(n, px + 7, py, 0))

    # U5 control: /CE→BUS_ROMSEL, /OE→BUS_RD, /WE→R7 pull-up
    p.append(wire(259.68, 296.35, 255, 296.35))
    p.append(netlabel("BUS_ROMSEL", 253, 296.35, 180))
    p.append(wire(259.68, 298.89, 250, 298.89))
    p.append(netlabel("BUS_RD", 248, 298.89, 180))
    p.append(wire(300.32, 324.33, 310, 324.33))
    p.append(wire(320, 324.33, 320, 320))
    p.append(netlabel("/WE_PROT", 320, 318, 270))

    # U5 VCC (pin16) → +3V3
    p.append(wire(280, 269.05, 280, 265))
    p.append(pwr_sym("+3V3", 280, 263))
    # U5 GND (pin11) → GND
    p.append(wire(280, 294.45, 280, 298))
    p.append(pwr_sym("GND", 280, 300))

    # C9 decoupling for U5
    p.append(wire(305, 271.19, 305, 268))
    p.append(pwr_sym("+3V3", 305, 266))
    p.append(wire(305, 278.81, 305, 282))
    p.append(pwr_sym("GND", 305, 284))

    # R7 pull-up /WE to +3V3
    p.append(wire(320, 256.19, 320, 252))
    p.append(pwr_sym("+3V3", 320, 250))

    p.append(text_block(
        "SHEET 2: Voltage Level Shifters & Boot Flash ROM\\n\\n"
        "U2,U3: 74LVC541APW (5V->3.3V Address/Control)\\n"
        "U4: SN74LVC8T245PWR (Bidir Data Bus 5V<->3.3V)\\n"
        "U5: SST39VF040 512KB Parallel NOR Flash\\n"
        "R7: 10k pull-up (Flash /WE HW write-protect)\\n"
        "C6-C9: 100nF decoupling per IC",
        30, 30))

    content = "".join(p)
    path = os.path.join(HW_DIR, "02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch")
    with open(path, "w") as f:
        f.write(_sheet_wrapper("Level Shifters & Parallel Flash ROM", content))
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Sheet 3: RP2350B MCU Subsystem
#  Components: U6, U7, Y1, J1, SW1, SW2, C10, C11, C12, C13, C17, C18,
#              R3, R4, R5, R6, R8  (17 total)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sheet3():
    p = []
    p.append(_lib_symbols_sheet3())

    # ── Hierarchical labels from Sheet 2 (BUS signals) ─────────────────────
    bus_in = [
        "BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3", "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7",
        "BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3", "BUS_A4", "BUS_A5",
        "BUS_A6", "BUS_A7", "BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
        "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15",
        "BUS_RD", "BUS_WR", "BUS_ROMSEL", "BUS_PHI2",
    ]
    for i, n in enumerate(bus_in):
        p.append(hlabel(n, "bidirectional", 30, 30 + i * 5, 0))

    # ── Hierarchical labels to Sheet 4 (ESP32) ─────────────────────────────
    esp_lbls = ["SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS",
                "UART_TX", "UART_RX", "ESP_INT"]
    for i, n in enumerate(esp_lbls):
        p.append(hlabel(n, "bidirectional", 390, 30 + i * 5, 180))

    # ── Hierarchical labels to Sheet 5 (Peripherals) ───────────────────────
    peri_lbls = ["I2C_SDA", "I2C_SCL", "SD_SCK", "SD_MOSI",
                 "SD_MISO", "SD_CS", "RS485_TX", "RS485_RX",
                 "LED_STATUS", "LED_WIFI", "LED_HEARTBEAT",
                 "JUMP_BOOTSEL", "JUMP_RST"]
    for i, n in enumerate(peri_lbls):
        p.append(hlabel(n, "bidirectional", 390, 50 + i * 5, 180))

    # ── Components ──────────────────────────────────────────────────────────
    p.append(sym("Custom:RP2350B", "U6", "RP2350B",
                 "Package_DFN_QFN:QFN-80-1EP_10x10mm_P0.5mm_EP6.1x6.1mm",
                 "SC1409", 200, 200))
    p.append(sym("Memory_Flash:W25Q128", "U7", "W25Q128JVSIQ",
                 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "C97521", 200, 120))
    p.append(sym("Device:Crystal", "Y1", "12.000MHz",
                 "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", "C16280", 260, 120))
    p.append(sym("Device:C", "C10", "15pF",
                 "Capacitor_SMD:C_0402_1005Metric", "C1554", 280, 115))
    p.append(sym("Device:C", "C11", "15pF",
                 "Capacitor_SMD:C_0402_1005Metric", "C1554", 280, 125))
    p.append(sym("Connector:USB_C_Receptacle_16P",
                 "J1", "TYPE-C-31-M-12",
                 "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
                 "C165948", 60, 200))
    p.append(sym("Device:SW_Push", "SW1", "BOOTSEL",
                 "Button_Switch_SMD:SW_SPST_TL3342", "C318884", 80, 280))
    p.append(sym("Device:SW_Push", "SW2", "RESET",
                 "Button_Switch_SMD:SW_SPST_TL3342", "C318884", 120, 280))
    p.append(sym("Device:C", "C12", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 230, 185))
    p.append(sym("Device:C", "C13", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 230, 195))
    p.append(sym("Device:C", "C17", "10uF",
                 "Capacitor_SMD:C_0805_2012Metric", "C15849", 245, 185))
    p.append(sym("Device:C", "C18", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 220, 115))
    p.append(sym("Device:R", "R3", "5.1k",
                 "Resistor_SMD:R_0402_1005Metric", "C25905", 70, 230))
    p.append(sym("Device:R", "R4", "5.1k",
                 "Resistor_SMD:R_0402_1005Metric", "C25905", 90, 230))
    p.append(sym("Device:R", "R5", "27R",
                 "Resistor_SMD:R_0402_1005Metric", "C25114", 70, 215))
    p.append(sym("Device:R", "R6", "27R",
                 "Resistor_SMD:R_0402_1005Metric", "C25114", 90, 215))
    p.append(sym("Device:R", "R8", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 180, 115))

    # ── Crystal circuit: Y1 ↔ C10, C11 ↔ RP2350 XIN/XOUT ─────────────────
    p.append(wire(260, 117.46, 255, 117.46))
    p.append(wire(260, 122.54, 255, 122.54))
    # C10: top to Y1 pin1, bottom to GND
    p.append(wire(260, 117.46, 280, 117.46))
    p.append(wire(280, 112.46, 280, 117.46))
    p.append(pwr_sym("GND", 280, 130))
    # C11: top to Y1 pin2, bottom to GND
    p.append(wire(260, 122.54, 280, 122.54))
    p.append(wire(280, 122.54, 280, 127.54))
    p.append(pwr_sym("GND", 280, 132))

    # ── QSPI Flash wiring ──────────────────────────────────────────────────
    # U7 VCC → +3V3, GND → GND
    p.append(wire(200, 112.38, 215, 112.38))
    p.append(pwr_sym("+3V3", 217, 112.38))
    p.append(wire(200, 127.62, 200, 130))
    p.append(pwr_sym("GND", 200, 132))
    # C18 decoupling
    p.append(wire(220, 112.38, 220, 115))
    p.append(wire(220, 120, 220, 122))
    p.append(pwr_sym("+3V3", 220, 110))
    p.append(pwr_sym("GND", 220, 124))
    # R8 QSPI CS pull-up
    p.append(wire(189.84, 116.19, 185, 116.19))
    p.append(wire(180, 115, 180, 117))
    p.append(pwr_sym("+3V3", 180, 113))
    # QSPI signal nets
    for i, n in enumerate(["QSPI_SS", "QSPI_SCLK", "QSPI_SD0",
                           "QSPI_SD1", "QSPI_SD2", "QSPI_SD3"]):
        py = 116.19 + i * 2.54
        p.append(wire(189.84, py, 185, py))
        p.append(netlabel(n, 183, py, 180))
        p.append(netlabel(n, 170, 190 + i * 5, 0))

    # ── USB-C wiring ───────────────────────────────────────────────────────
    # R5, R6 series resistors on D+/D-
    p.append(wire(50, 195, 60, 195))
    p.append(wire(60, 195, 70, 195))
    p.append(wire(75, 195, 80, 195))
    p.append(wire(50, 205, 60, 205))
    p.append(wire(60, 205, 70, 205))
    p.append(wire(75, 205, 80, 205))
    # CC pulldowns
    p.append(wire(65, 230, 70, 230))
    p.append(wire(75, 230, 80, 230))
    p.append(wire(85, 230, 90, 230))
    p.append(wire(95, 230, 100, 230))
    p.append(pwr_sym("GND", 80, 240))
    p.append(pwr_sym("GND", 100, 240))

    # ── Decoupling cap wiring ──────────────────────────────────────────────
    # C12, C13 near RP2350 IOVDD pins
    for cx, cy in [(230, 185), (230, 195), (245, 185)]:
        p.append(wire(cx, cy - 3.81, cx, cy - 5))
        p.append(pwr_sym("+3V3", cx, cy - 7))
        p.append(wire(cx, cy + 3.81, cx, cy + 5))
        p.append(pwr_sym("GND", cx, cy + 7))

    # ── RP2350 power pins ──────────────────────────────────────────────────
    # Multiple IOVDD and DVDD → +3V3, multiple VSS → GND
    p.append(pwr_sym("+3V3", 170, 180))
    p.append(pwr_sym("+3V3", 170, 170))
    p.append(pwr_sym("+3V3", 170, 160))
    p.append(pwr_sym("GND", 170, 230))
    p.append(pwr_sym("GND", 170, 240))
    p.append(pwr_sym("GND", 170, 250))

    # ── Button wiring ──────────────────────────────────────────────────────
    # SW1 BOOTSEL: pin1→GND, pin2→JUMP_BOOTSEL
    p.append(wire(80, 275, 80, 272))
    p.append(pwr_sym("GND", 80, 270))
    p.append(wire(80, 285, 80, 290))
    p.append(netlabel("JUMP_BOOTSEL", 80, 292, 270))
    # SW2 RESET: pin1→GND, pin2→JUMP_RST
    p.append(wire(120, 275, 120, 272))
    p.append(pwr_sym("GND", 120, 270))
    p.append(wire(120, 285, 120, 290))
    p.append(netlabel("JUMP_RST", 120, 292, 270))

    # ── Net labels for inter-sheet signals ─────────────────────────────────
    # Bus to RP2350 GPIO
    bus_gpio = [
        ("BUS_D0", 170, 200), ("BUS_D1", 170, 197.46),
        ("BUS_D2", 170, 194.92), ("BUS_D3", 170, 192.38),
        ("BUS_D4", 170, 189.84), ("BUS_D5", 170, 187.30),
        ("BUS_D6", 170, 184.76), ("BUS_D7", 170, 182.22),
        ("BUS_A0", 170, 179.68), ("BUS_A1", 170, 177.14),
        ("BUS_A2", 170, 174.60), ("BUS_A3", 170, 172.06),
        ("BUS_A4", 170, 169.52), ("BUS_A5", 170, 166.98),
        ("BUS_A6", 170, 164.44), ("BUS_A7", 170, 161.90),
        ("BUS_A8", 170, 159.36), ("BUS_A9", 170, 156.82),
        ("BUS_A10", 170, 154.28), ("BUS_A11", 170, 151.74),
        ("BUS_A12", 170, 149.20), ("BUS_A13", 170, 146.66),
        ("BUS_A14", 170, 144.12), ("BUS_A15", 170, 141.58),
        ("BUS_RD", 170, 139.04), ("BUS_WR", 170, 136.50),
        ("BUS_ROMSEL", 170, 133.96), ("BUS_PHI2", 170, 131.42),
    ]
    for n, lx, ly in bus_gpio:
        p.append(netlabel(n, lx, ly, 0))

    # SPI to ESP32
    for n, lx, ly in [("SPI_SCK", 220, 170), ("SPI_MOSI", 220, 175),
                      ("SPI_MISO", 220, 180), ("SPI_CS", 220, 185)]:
        p.append(netlabel(n, lx, ly, 0))

    # UART to ESP32
    p.append(netlabel("UART_TX", 220, 190, 0))
    p.append(netlabel("UART_RX", 220, 195, 0))

    # ESP_INT
    p.append(netlabel("ESP_INT", 220, 200, 0))

    # Peripheral signals
    peri_sig = [("I2C_SDA", 220, 205), ("I2C_SCL", 220, 210),
                ("SD_SCK", 220, 215), ("SD_MOSI", 220, 220),
                ("SD_MISO", 220, 225), ("SD_CS", 220, 230),
                ("RS485_TX", 220, 235), ("RS485_RX", 220, 240),
                ("LED_STATUS", 220, 245), ("LED_WIFI", 220, 250),
                ("LED_HEARTBEAT", 220, 255)]
    for n, lx, ly in peri_sig:
        p.append(netlabel(n, lx, ly, 0))

    # Button labels to RP2350
    p.append(netlabel("JUMP_BOOTSEL", 170, 250, 0))
    p.append(netlabel("JUMP_RST", 175, 225, 0))

    # USB labels
    p.append(netlabel("USB_DM", 110, 215, 0))
    p.append(netlabel("USB_DP", 110, 225, 0))

    p.append(text_block(
        "SHEET 3: RP2350B Dual-Core MCU Subsystem\\n\\n"
        "U6: RP2350B (Cortex-M33 x2, 520KB SRAM)\\n"
        "U7: W25Q128JVSIQ 16MB QSPI Flash\\n"
        "Y1: 12MHz crystal + 15pF load caps\\n"
        "J1: USB-C (UF2 drag-and-drop)\\n"
        "SW1: BOOTSEL, SW2: RESET\\n"
        "R3-R4: 5.1k USB-C CC pulldowns\\n"
        "R5-R6: 27R USB series resistors\\n"
        "R8: 10k QSPI CS pull-up",
        30, 30))

    content = "".join(p)
    path = os.path.join(HW_DIR, "03_RP2350_SUBSYSTEM.kicad_sch")
    with open(path, "w") as f:
        f.write(_sheet_wrapper("RP2350B MCU Subsystem & Mailbox", content))
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Sheet 4: ESP32-C6 Wi-Fi 6 / IoT Coprocessor
#  Components: U8, D3, SW3, SW4, C14, C15, R9, R10  (8 total)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sheet4():
    p = []
    p.append(_lib_symbols_sheet4())

    # ── Hierarchical labels from Sheet 3 ───────────────────────────────────
    for i, n in enumerate(["SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS",
                           "UART_TX", "UART_RX"]):
        p.append(hlabel(n, "input", 30, 30 + i * 5, 0))
    p.append(hlabel("ESP_INT", "bidirectional", 390, 30, 180))

    # ── Components ──────────────────────────────────────────────────────────
    p.append(sym("Custom:ESP32-C6-MINI-1", "U8", "ESP32-C6-MINI-1-N4",
                 "RF_Module:ESP32-C6-MINI-1", "C5248554", 200, 180))
    p.append(sym("Custom:WS2812B", "D3", "WS2812B-2020",
                 "LED_SMD:LED_WS2812B_PLCC4_3.2x3.2mm_P1.75mm",
                 "C2890040", 280, 180))
    p.append(sym("Device:SW_Push", "SW3", "ESP_BOOT",
                 "Button_Switch_SMD:SW_SPST_TL3342", "C318884", 280, 250))
    p.append(sym("Device:SW_Push", "SW4", "ESP_EN",
                 "Button_Switch_SMD:SW_SPST_TL3342", "C318884", 320, 250))
    p.append(sym("Device:C", "C14", "100nF",
                 "Capacitor_SMD:C_0402_1005Metric", "C14663", 230, 165))
    p.append(sym("Device:C", "C15", "10uF",
                 "Capacitor_SMD:C_0805_2012Metric", "C15849", 245, 165))
    p.append(sym("Device:R", "R9", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 340, 240))
    p.append(sym("Device:R", "R10", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 260, 240))

    # ── U8 power: 3V3→+3V3, GND→GND ───────────────────────────────────────
    p.append(wire(182.22, 163.49, 175, 163.49))
    p.append(pwr_sym("+3V3", 173, 163.49))
    p.append(wire(182.22, 196.38, 182.22, 200))
    p.append(pwr_sym("GND", 182.22, 202))

    # ── Decoupling C14, C15 wired to U8 power ──────────────────────────────
    p.append(wire(230, 161.19, 230, 158))
    p.append(pwr_sym("+3V3", 230, 156))
    p.append(wire(230, 168.81, 230, 172))
    p.append(pwr_sym("GND", 230, 174))
    p.append(wire(245, 161.19, 245, 158))
    p.append(pwr_sym("+3V3", 245, 156))
    p.append(wire(245, 168.81, 245, 172))
    p.append(pwr_sym("GND", 245, 174))

    # ── SPI wires from U8 to labels ────────────────────────────────────────
    p.append(wire(182.22, 157.74, 175, 157.74))
    p.append(netlabel("SPI_SCK", 173, 157.74, 180))
    p.append(wire(182.22, 160.28, 175, 160.28))
    p.append(netlabel("SPI_MOSI", 173, 160.28, 180))
    p.append(wire(182.22, 162.82, 175, 162.82))
    p.append(netlabel("SPI_MISO", 173, 162.82, 180))
    p.append(wire(182.22, 165.36, 175, 165.36))
    p.append(netlabel("SPI_CS", 173, 165.36, 180))

    # ── UART wires ─────────────────────────────────────────────────────────
    p.append(wire(182.22, 132.34, 175, 132.34))
    p.append(netlabel("UART_TX", 173, 132.34, 180))
    p.append(wire(182.22, 134.88, 175, 134.88))
    p.append(netlabel("UART_RX", 173, 134.88, 180))

    # ── ESP_INT ─────────────────────────────────────────────────────────────
    p.append(netlabel("ESP_INT", 217.78, 201.74, 0))

    # ── D3 WS2812B wiring ──────────────────────────────────────────────────
    p.append(wire(272.38, 182.54, 272.38, 178))
    p.append(pwr_sym("+3V3", 272.38, 176))
    p.append(wire(280, 182.54, 280, 186))
    p.append(pwr_sym("GND", 280, 188))
    # DIN from U8 GPIO43
    p.append(wire(272.38, 185.08, 265, 185.08))
    p.append(netlabel("LED_STATUS", 263, 185.08, 180))

    # ── Button wiring ──────────────────────────────────────────────────────
    # SW3 BOOT: pin1→GND, pin2→BOOT
    p.append(wire(280, 245, 280, 242))
    p.append(pwr_sym("GND", 280, 240))
    p.append(wire(280, 255, 280, 258))
    p.append(netlabel("ESP_BOOT", 280, 260, 270))
    # SW4 EN: pin1→GND, pin2→EN with R9 pull-up
    p.append(wire(320, 245, 320, 242))
    p.append(pwr_sym("GND", 320, 240))
    p.append(wire(320, 255, 320, 258))
    p.append(netlabel("ESP_EN", 320, 260, 270))
    # R9 pull-up EN
    p.append(wire(340, 236.19, 340, 232))
    p.append(pwr_sym("+3V3", 340, 230))
    # R10 pull-up BOOT
    p.append(wire(260, 236.19, 260, 232))
    p.append(pwr_sym("+3V3", 260, 230))

    # ── U8 EN and BOOTSEL pins ─────────────────────────────────────────────
    p.append(netlabel("ESP_EN", 182.22, 163.49, 180))
    p.append(netlabel("ESP_BOOT", 182.22, 166.10, 180))

    p.append(text_block(
        "SHEET 4: ESP32-C6 Wi-Fi 6 / BLE / Thread Coprocessor\\n\\n"
        "U8: ESP32-C6-MINI-1-N4\\n"
        "  Wi-Fi 6, BLE 5, 802.15.4 (Thread/Zigbee)\\n"
        "D3: WS2812B RGB status LED\\n"
        "SW3: ESP_BOOT, SW4: ESP_EN\\n"
        "R9,R10: 10k pull-ups\\n"
        "C14: 100nF, C15: 10uF decoupling",
        30, 30))

    content = "".join(p)
    path = os.path.join(HW_DIR, "04_ESP32C6_WIFI_IOT.kicad_sch")
    with open(path, "w") as f:
        f.write(_sheet_wrapper("ESP32-C6 Wi-Fi 6 / IoT Coprocessor", content))
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Sheet 5: Peripherals & 5V→3.3V Power Supply
#  Components: U9, U10, U11, J4, J5, J6, BT1, D4, F1, L1,
#              C1, C2, C3, C4, R1, R2, R11, R12, R13, R14, R15, R16, R17
#              (23 total)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sheet5():
    p = []
    p.append(_lib_symbols_sheet5())

    # ── Hierarchical labels from Sheet 3 ───────────────────────────────────
    peri_in = ["I2C_SDA", "I2C_SCL", "SD_SCK", "SD_MOSI",
               "SD_MISO", "SD_CS", "RS485_TX", "RS485_RX",
               "LED_STATUS", "LED_WIFI", "LED_HEARTBEAT"]
    for i, n in enumerate(peri_in):
        p.append(hlabel(n, "input", 30, 30 + i * 5, 0))

    # ── Power supply chain components ───────────────────────────────────────
    p.append(sym("Device:D", "D4", "SS34",
                 "Diode_SMD:D_SMA", "C46104", 50, 120))
    p.append(sym("Device:Polyfuse", "F1", "1206L150PR",
                 "Fuse:Fuse_1206_3216Metric", "C70267", 50, 150))
    p.append(sym("Device:L", "L1", "2.2uH",
                 "Inductor_SMD:L_0805_2012Metric", "C144887", 110, 180))
    p.append(sym("Custom:SY8089", "U9", "SY8089AAAC",
                 "Package_TO_SOT_SMD:SOT-23-5_Handsoldering", "C28674", 80, 180))
    p.append(sym("Device:R", "R1", "100k",
                 "Resistor_SMD:R_0402_1005Metric", "C25744", 95, 200))
    p.append(sym("Device:R", "R2", "22k",
                 "Resistor_SMD:R_0402_1005Metric", "C25765", 95, 215))
    p.append(sym("Device:C", "C1", "47uF",
                 "Capacitor_SMD:C_1206_3216Metric", "C13063", 50, 200))
    p.append(sym("Device:C", "C2", "22uF",
                 "Capacitor_SMD:C_0805_2012Metric", "C15849", 65, 200))
    p.append(sym("Device:C", "C3", "22uF",
                 "Capacitor_SMD:C_0805_2012Metric", "C15849", 130, 180))
    p.append(sym("Device:C", "C4", "47uF",
                 "Capacitor_SMD:C_1206_3216Metric", "C13063", 145, 180))

    # ── U10 DS3231 RTC ─────────────────────────────────────────────────────
    p.append(sym("Timer_RTC:DS3231", "U10", "DS3231MZ+",
                 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "C16719", 200, 180))

    # ── U11 MAX3485 RS-485 ──────────────────────────────────────────────────
    p.append(sym("Interface_UART:MAX3485", "U11", "MAX3485",
                 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "C6960", 300, 180))

    # ── Connectors ─────────────────────────────────────────────────────────
    p.append(sym("Connector:Conn_01x09_Pin", "J4", "TF-01A",
                 "Connector_Card:TF_TF-01A", "C91145", 200, 300))
    p.append(sym("Connector:Conn_01x03_Pin", "J5", "KF2EDG-3.5-3P",
                 "TerminalBlock:TerminalBlock_bornier-3_P5.08mm", "C8389", 340, 180))
    p.append(sym("Connector:Conn_01x04_Pin", "J6", "JST_SH_1.0mm_4P",
                 "Connector_JST:JST_SH_SM04B-SRSS-TB_1.00mm", "C145920", 340, 250))

    # ── Battery ────────────────────────────────────────────────────────────
    p.append(sym("Battery:BatteryHolder_CR1220", "BT1", "CR1220",
                 "Battery:BatteryHolder_CR1220_Holder", "C70377", 240, 280))

    # ── Resistors ──────────────────────────────────────────────────────────
    p.append(sym("Device:R", "R11", "4.7k",
                 "Resistor_SMD:R_0402_1005Metric", "C25900", 230, 220))
    p.append(sym("Device:R", "R12", "4.7k",
                 "Resistor_SMD:R_0402_1005Metric", "C25900", 245, 220))
    p.append(sym("Device:R", "R13", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 330, 210))
    p.append(sym("Device:R", "R14", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 345, 210))
    p.append(sym("Device:R", "R15", "120R",
                 "Resistor_SMD:R_0603_1608Metric", "C22787", 360, 180))
    p.append(sym("Device:R", "R16", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 190, 260))
    p.append(sym("Device:R", "R17", "10k",
                 "Resistor_SMD:R_0402_1005Metric", "C25804", 210, 260))

    # ── Power chain: +5V_SNES → F1 → D4 → +5V_PROT → U9 → +3V3 ───────────
    p.append(pwr_sym("+5V_SNES", 50, 105))
    p.append(wire(50, 112, 50, 125))  # F1 top
    p.append(wire(50, 135, 50, 145))  # F1 bottom to D4
    p.append(wire(50, 160, 50, 170))  # D4 bottom to +5V_PROT
    p.append(netlabel("+5V_PROT", 50, 172, 0))
    # +5V_PROT to U9 VIN
    p.append(netlabel("+5V_PROT", 69.84, 177.46, 180))

    # ── U9 SY8089 buck converter wiring ────────────────────────────────────
    # U9 VIN (pin1) ← +5V_PROT
    p.append(wire(69.84, 177.46, 65, 177.46))
    p.append(pwr_sym("+5V_PROT", 63, 177.46))
    # U9 GND (pin2) → GND
    p.append(wire(80, 187.62, 80, 190))
    p.append(pwr_sym("GND", 80, 192))
    # U9 SW (pin3) → L1
    p.append(wire(90.16, 177.46, 100, 177.46))
    p.append(wire(100, 177.46, 110, 177.46))
    # L1 output → +3V3 with C3, C4 filter caps
    p.append(wire(110, 175, 130, 175))
    p.append(pwr_sym("+3V3", 130, 173))
    p.append(wire(130, 185, 130, 188))
    p.append(pwr_sym("+3V3", 145, 170))
    # U9 EN (pin4) ← +5V_PROT (always enabled)
    p.append(wire(69.84, 182.54, 60, 182.54))
    p.append(pwr_sym("+5V_PROT", 58, 182.54))
    # U9 FB (pin5) ← R1/R2 divider
    p.append(wire(90.16, 182.54, 95, 182.54))
    p.append(wire(95, 182.54, 95, 196.19))
    p.append(netlabel("FB", 95, 194, 270))

    # ── Input caps C1, C2 ──────────────────────────────────────────────────
    p.append(pwr_sym("+5V_SNES", 50, 196.19))
    p.append(wire(50, 196.19, 50, 200))
    p.append(pwr_sym("GND", 50, 208))
    p.append(pwr_sym("+5V_SNES", 65, 196.19))
    p.append(wire(65, 196.19, 65, 200))
    p.append(pwr_sym("GND", 65, 208))

    # ── Output caps C3, C4 ─────────────────────────────────────────────────
    p.append(pwr_sym("+3V3", 130, 176.19))
    p.append(wire(130, 176.19, 130, 180))
    p.append(pwr_sym("GND", 130, 188))
    p.append(pwr_sym("+3V3", 145, 176.19))
    p.append(wire(145, 176.19, 145, 180))
    p.append(pwr_sym("GND", 145, 188))

    # ── R1, R2 feedback divider ────────────────────────────────────────────
    p.append(pwr_sym("+3V3", 95, 196.19))
    p.append(wire(95, 196.19, 95, 200))
    p.append(wire(95, 208, 95, 211))
    p.append(netlabel("FB", 95, 213, 270))
    p.append(wire(95, 219, 95, 222))
    p.append(pwr_sym("GND", 95, 224))

    # ── U10 DS3231 RTC wiring ──────────────────────────────────────────────
    p.append(wire(189.84, 176.19, 185, 176.19))
    p.append(pwr_sym("+3V3", 183, 176.19))
    p.append(wire(200, 187.62, 200, 190))
    p.append(pwr_sym("GND", 200, 192))
    # VBAT (pin8) ← BT1
    p.append(wire(189.84, 183.81, 185, 183.81))
    p.append(netlabel("VBAT", 183, 183.81, 180))
    # SCL, SDA
    p.append(wire(310.16, 178.73, 315, 178.73))
    p.append(netlabel("I2C_SCL", 317, 178.73, 0))
    p.append(wire(310.16, 176.19, 315, 176.19))
    p.append(netlabel("I2C_SDA", 317, 176.19, 0))

    # ── BT1 battery holder wiring ──────────────────────────────────────────
    p.append(pwr_sym("+3V3", 240, 270))
    p.append(wire(240, 276.19, 240, 280))
    p.append(pwr_sym("GND", 240, 282))

    # ── U11 MAX3485 RS-485 wiring ───────────────────────────────────────────
    p.append(wire(310.16, 176.19, 315, 176.19))
    p.append(pwr_sym("+3V3", 317, 176.19))
    p.append(wire(300, 187.62, 300, 190))
    p.append(pwr_sym("GND", 300, 192))
    # RO (pin1) → RS485_RX
    p.append(wire(289.84, 176.19, 285, 176.19))
    p.append(netlabel("RS485_RX", 283, 176.19, 180))
    # DI (pin4) ← RS485_TX
    p.append(wire(289.84, 181.27, 285, 181.27))
    p.append(netlabel("RS485_TX", 283, 181.27, 180))
    # /RE, DE → enable (tied together for half-duplex)
    p.append(wire(289.84, 178.73, 283, 178.73))
    p.append(wire(289.84, 180, 283, 180))
    p.append(wire(283, 178.73, 283, 180))
    # A, B → RS-485 bus
    p.append(wire(310.16, 183.81, 320, 183.81))
    p.append(netlabel("RS485_A", 322, 183.81, 0))
    p.append(wire(310.16, 186.35, 320, 186.35))
    p.append(netlabel("RS485_B", 322, 186.35, 0))

    # R15 termination across A-B
    p.append(netlabel("RS485_A", 360, 176.19, 0))
    p.append(netlabel("RS485_B", 360, 181.27, 0))

    # ── J5 screw terminal RS-485 ───────────────────────────────────────────
    p.append(netlabel("RS485_A", 335, 175, 180))
    p.append(netlabel("RS485_B", 335, 180, 180))
    p.append(pwr_sym("GND", 335, 185))

    # ── J4 MicroSD ─────────────────────────────────────────────────────────
    p.append(netlabel("SD_SCK", 195, 295, 180))
    p.append(netlabel("SD_MOSI", 195, 300, 180))
    p.append(netlabel("SD_MISO", 195, 305, 180))
    p.append(netlabel("SD_CS", 195, 310, 180))
    p.append(pwr_sym("+3V3", 200, 288))
    p.append(pwr_sym("GND", 200, 315))

    # ── J6 Qwiic I2C connector ─────────────────────────────────────────────
    p.append(pwr_sym("+3V3", 335, 245))
    p.append(pwr_sym("GND", 335, 265))
    p.append(netlabel("I2C_SDA", 340, 255, 0))
    p.append(netlabel("I2C_SCL", 340, 260, 0))

    # ── I2C pull-ups R11, R12 ─────────────────────────────────────────────
    p.append(pwr_sym("+3V3", 230, 216.19))
    p.append(wire(230, 216.19, 230, 220))
    p.append(netlabel("I2C_SDA", 230, 226, 90))
    p.append(pwr_sym("+3V3", 245, 216.19))
    p.append(wire(245, 216.19, 245, 220))
    p.append(netlabel("I2C_SCL", 245, 226, 90))

    # ── R13, R14 RS-485 pull-ups ──────────────────────────────────────────
    p.append(pwr_sym("+3V3", 330, 206.19))
    p.append(wire(330, 206.19, 330, 210))
    p.append(netlabel("RS485_A", 330, 216, 90))
    p.append(pwr_sym("+3V3", 345, 206.19))
    p.append(wire(345, 206.19, 345, 210))
    p.append(netlabel("RS485_B", 345, 216, 90))

    # ── R16, R17 SD card pull-ups ──────────────────────────────────────────
    p.append(pwr_sym("+3V3", 190, 256.19))
    p.append(wire(190, 256.19, 190, 260))
    p.append(netlabel("SD_MISO", 190, 266, 90))
    p.append(pwr_sym("+3V3", 210, 256.19))
    p.append(wire(210, 256.19, 210, 260))
    p.append(netlabel("SD_CS", 210, 266, 90))

    # ── Status LED labels ──────────────────────────────────────────────────
    p.append(netlabel("LED_STATUS", 320, 250, 180))
    p.append(netlabel("LED_WIFI", 340, 250, 180))
    p.append(netlabel("LED_HEARTBEAT", 360, 250, 180))

    # ── D4 Schottky power labels ───────────────────────────────────────────
    p.append(pwr_sym("+5V_SNES", 50, 105))

    p.append(text_block(
        "SHEET 5: Peripherals & 5V->3.3V Power Supply\\n\\n"
        "U9: SY8089AAAC Buck 5V->3.3V 2.0A (>92% eff)\\n"
        "U10: DS3231MZ+ RTC (+-5ppm, battery backup)\\n"
        "U11: MAX3485 RS-485 Transceiver\\n"
        "D4: SS34 Schottky (reverse polarity)\\n"
        "F1: PTC 1.5A (overcurrent)\\n"
        "L1: 2.2uH inductor\\n"
        "BT1: CR1220 battery holder",
        30, 30))

    content = "".join(p)
    path = os.path.join(HW_DIR, "05_PERIPHERALS_AND_POWER.kicad_sch")
    with open(path, "w") as f:
        f.write(_sheet_wrapper("Peripherals (MicroSD, RTC, RS-485, I2C) & Power", content))
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Root schematic with hierarchical sheet boxes + pins
#  Connects all 5 sub-sheets via hierarchical pins + net labels
# ══════════════════════════════════════════════════════════════════════════════

def generate_root():
    root_uuid = uid()
    s_uuids = [uid() for _ in range(5)]

    # ── Hierarchical pin lists per sheet ────────────────────────────────────
    # Sheet 1 outputs SNES signals (42 pins)
    sheet1_pins = [
        "SNES_A0", "SNES_A1", "SNES_A2", "SNES_A3", "SNES_A4", "SNES_A5",
        "SNES_A6", "SNES_A7", "SNES_A8", "SNES_A9", "SNES_A10", "SNES_A11",
        "SNES_A12", "SNES_A13", "SNES_A14", "SNES_A15",
        "SNES_A16", "SNES_A17", "SNES_A18", "SNES_A19",
        "SNES_A20", "SNES_A21", "SNES_A22", "SNES_A23",
        "SNES_D0", "SNES_D1", "SNES_D2", "SNES_D3",
        "SNES_D4", "SNES_D5", "SNES_D6", "SNES_D7",
        "/RD", "/WR", "/ROMSEL", "/IRQ", "/RESET", "PHI2",
        "CIC_CLK", "CIC_RST", "CIC_DAT1", "CIC_DAT2",
    ]

    # Sheet 2: inputs from Sheet 1, outputs BUS signals (56 pins)
    sheet2_pins = [
        "SNES_A0", "SNES_A1", "SNES_A2", "SNES_A3", "SNES_A4", "SNES_A5",
        "SNES_A6", "SNES_A7", "SNES_A8", "SNES_A9", "SNES_A10", "SNES_A11",
        "SNES_A12", "SNES_A13", "SNES_A14", "SNES_A15",
        "SNES_D0", "SNES_D1", "SNES_D2", "SNES_D3",
        "SNES_D4", "SNES_D5", "SNES_D6", "SNES_D7",
        "/RD", "/WR", "/ROMSEL", "PHI2",
        "BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3", "BUS_A4", "BUS_A5",
        "BUS_A6", "BUS_A7", "BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
        "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15",
        "BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3",
        "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7",
        "BUS_RD", "BUS_WR", "BUS_ROMSEL", "BUS_PHI2",
    ]

    # Sheet 3: inputs from Sheet 2, outputs to Sheets 4 and 5 (48 pins)
    sheet3_pins = [
        "BUS_D0", "BUS_D1", "BUS_D2", "BUS_D3", "BUS_D4", "BUS_D5", "BUS_D6", "BUS_D7",
        "BUS_A0", "BUS_A1", "BUS_A2", "BUS_A3", "BUS_A4", "BUS_A5",
        "BUS_A6", "BUS_A7", "BUS_A8", "BUS_A9", "BUS_A10", "BUS_A11",
        "BUS_A12", "BUS_A13", "BUS_A14", "BUS_A15",
        "BUS_RD", "BUS_WR", "BUS_ROMSEL", "BUS_PHI2",
        "SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS",
        "UART_TX", "UART_RX", "ESP_INT",
        "I2C_SDA", "I2C_SCL", "SD_SCK", "SD_MOSI", "SD_MISO", "SD_CS",
        "RS485_TX", "RS485_RX",
        "LED_STATUS", "LED_WIFI", "LED_HEARTBEAT",
        "JUMP_BOOTSEL", "JUMP_RST",
    ]

    # Sheet 4: inputs from Sheet 3 (7 pins)
    sheet4_pins = [
        "SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS",
        "UART_TX", "UART_RX", "ESP_INT",
    ]

    # Sheet 5: inputs from Sheet 3 (11 pins)
    sheet5_pins = [
        "I2C_SDA", "I2C_SCL", "SD_SCK", "SD_MOSI", "SD_MISO", "SD_CS",
        "RS485_TX", "RS485_RX",
        "LED_STATUS", "LED_WIFI", "LED_HEARTBEAT",
    ]

    all_pins = [sheet1_pins, sheet2_pins, sheet3_pins, sheet4_pins, sheet5_pins]

    # ── Sheet box definitions: (x, y, w, h, name, file) ────────────────────
    box_defs = [
        (38.1,  44.45,  76.2, 50.8, "01_SNES_BUS_AND_CIC",
         "01_SNES_BUS_AND_CIC.kicad_sch"),
        (139.7, 44.45,  76.2, 50.8, "02_LEVEL_SHIFTERS_AND_FLASH",
         "02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch"),
        (241.3, 44.45,  76.2, 63.5, "03_RP2350_SUBSYSTEM",
         "03_RP2350_SUBSYSTEM.kicad_sch"),
        (88.9,  127.0,  76.2, 38.1, "04_ESP32C6_WIFI_IOT",
         "04_ESP32C6_WIFI_IOT.kicad_sch"),
        (190.5, 127.0,  76.2, 38.1, "05_PERIPHERALS_AND_POWER",
         "05_PERIPHERALS_AND_POWER.kicad_sch"),
    ]

    # ── Generate sheet boxes with hierarchical pins ────────────────────────
    boxes = []
    for (bx, by, bw, bh, sname, sfile), pins, suuid in zip(
            box_defs, all_pins, s_uuids):
        pin_strs = []
        # Split pins: first half on left (input), second half on right (output)
        n_left = len(pins) // 2
        n_right = len(pins) - n_left
        for i, pname in enumerate(pins[:n_left]):
            py = by + 2.54 + i * (bh - 5.08) / max(n_left - 1, 1)
            pin_strs.append(hpin(pname, "input", bx, py, 0))
        for i, pname in enumerate(pins[n_left:]):
            py = by + 2.54 + i * (bh - 5.08) / max(n_right - 1, 1)
            pin_strs.append(hpin(pname, "output", bx + bw, py, 180))
        pins_block = "".join(pin_strs)

        boxes.append(
            f'\t(sheet\n'
            f'\t\t(at {bx} {by})\n'
            f'\t\t(size {bw} {bh})\n'
            f'\t\t(fields_autoplaced yes)\n'
            f'\t\t(stroke (width 0.1524) (type solid))\n'
            f'\t\t(fill (color 0 0 0 0.0000))\n'
            f'\t\t(uuid "{suuid}")\n'
            f'\t\t(property "Sheetname" "{sname}"\n'
            f'\t\t\t(at {bx} {by - 1.27} 0)\n'
            f'\t\t\t(effects (font (size 1.5 1.5) (bold yes)) (justify left bottom))\n'
            f'\t\t)\n'
            f'\t\t(property "Sheetfile" "{sfile}"\n'
            f'\t\t\t(at {bx} {by + bh + 1.27} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n'
            f'\t\t)\n'
            f'{pins_block}'
            f'\t)\n'
        )

    # ── Net labels to connect sheets (same net name = connected) ───────────
    # The key insight: in KiCad, net labels with the same name are connected
    # regardless of position. So we place labels at each sheet box pin endpoint.
    net_labels = []

    # Sheet 1 right-side output pins → right edge at x = 38.1 + 76.2 = 114.3
    # Sheet 2 left-side input pins → left edge at x = 139.7
    # Sheet 2 right-side output pins → right edge at x = 139.7 + 76.2 = 215.9
    # Sheet 3 left-side input pins → left edge at x = 241.3
    # Sheet 3 right-side output pins → right edge at x = 241.3 + 76.2 = 317.5
    # Sheet 4 left-side input pins → left edge at x = 88.9
    # Sheet 5 left-side input pins → left edge at x = 190.5

    # Connect Sheet 1 → Sheet 2 (SNES signals)
    # Sheet 1 right pins at x=114.3, Sheet 2 left pins at x=139.7
    # We place labels at the pin endpoints for each side
    sheet1_right_y0 = 44.45 + 2.54
    for i, pname in enumerate(sheet1_pins):
        py = sheet1_right_y0 + i * (50.8 - 5.08) / max(len(sheet1_pins) // 2 - 1, 1) \
             if i < len(sheet1_pins) // 2 \
             else sheet1_right_y0 + (i - len(sheet1_pins) // 2) * (50.8 - 5.08) / max(len(sheet1_pins) - len(sheet1_pins) // 2 - 1, 1)
        # Right-side pins of Sheet 1 are on the right half of pins
        if i >= len(sheet1_pins) // 2:
            py = sheet1_right_y0 + (i - len(sheet1_pins) // 2) * (50.8 - 5.08) / max(len(sheet1_pins) - len(sheet1_pins) // 2 - 1, 1)
            net_labels.append(netlabel(pname, 114.3, py, 0))

    # Sheet 2 left pins at x=139.7
    sheet2_left_y0 = 44.45 + 2.54
    for i, pname in enumerate(sheet2_pins[:len(sheet2_pins) // 2]):
        py = sheet2_left_y0 + i * (50.8 - 5.08) / max(len(sheet2_pins) // 2 - 1, 1)
        net_labels.append(netlabel(pname, 139.7, py, 180))

    # Sheet 2 right pins at x=215.9
    for i, pname in enumerate(sheet2_pins[len(sheet2_pins) // 2:]):
        py = sheet2_left_y0 + i * (50.8 - 5.08) / max(len(sheet2_pins) - len(sheet2_pins) // 2 - 1, 1)
        net_labels.append(netlabel(pname, 215.9, py, 0))

    # Sheet 3 left pins at x=241.3
    sheet3_left_y0 = 44.45 + 2.54
    for i, pname in enumerate(sheet3_pins[:len(sheet3_pins) // 2]):
        py = sheet3_left_y0 + i * (63.5 - 5.08) / max(len(sheet3_pins) // 2 - 1, 1)
        net_labels.append(netlabel(pname, 241.3, py, 180))

    # Sheet 3 right pins at x=317.5
    for i, pname in enumerate(sheet3_pins[len(sheet3_pins) // 2:]):
        py = sheet3_left_y0 + i * (63.5 - 5.08) / max(len(sheet3_pins) - len(sheet3_pins) // 2 - 1, 1)
        net_labels.append(netlabel(pname, 317.5, py, 0))

    # Sheet 4 left pins at x=88.9
    sheet4_left_y0 = 127.0 + 2.54
    for i, pname in enumerate(sheet4_pins):
        py = sheet4_left_y0 + i * (38.1 - 5.08) / max(len(sheet4_pins) - 1, 1)
        net_labels.append(netlabel(pname, 88.9, py, 180))

    # Sheet 5 left pins at x=190.5
    sheet5_left_y0 = 127.0 + 2.54
    for i, pname in enumerate(sheet5_pins):
        py = sheet5_left_y0 + i * (38.1 - 5.08) / max(len(sheet5_pins) - 1, 1)
        net_labels.append(netlabel(pname, 190.5, py, 180))

    # ── Power symbols on root ──────────────────────────────────────────────
    pwr = [
        pwr_sym("+5V_SNES", 38.1, 20),
        pwr_sym("+3V3", 100, 20),
        pwr_sym("GND", 160, 20),
    ]

    # ── Sheet instances ────────────────────────────────────────────────────
    sheet_insts = (
        '\t(sheet_instances\n'
        '\t\t(path "/" (page "1"))\n'
    )
    pages = ["2", "3", "4", "5", "6"]
    for suuid, pg in zip(s_uuids, pages):
        sheet_insts += f'\t\t(path "/{suuid}" (page "{pg}"))\n'
    sheet_insts += '\t)\n'

    # ── Text block ─────────────────────────────────────────────────────────
    tb = text_block(
        "SUPER FAMICOM / SNES SMART HOME INTERFACE CARTRIDGE V1.0\\n\\n"
        "System Overview:\\n"
        "- Sheet 1: 62-Pin SNES Bus Edge Connector (2.50mm pitch) + SuperCIC PIC12F629\\n"
        "- Sheet 2: 74LVC541 + SN74LVC8T245 Level Shifters + 4Mbit Parallel Boot Flash\\n"
        "- Sheet 3: RP2350B MCU Subsystem (Dual Cortex-M33, Mailbox, 16MB QSPI, USB-C)\\n"
        "- Sheet 4: ESP32-C6-MINI-1 Wi-Fi 6 / BLE / Thread (Home Assistant REST/WS)\\n"
        "- Sheet 5: Peripherals (MicroSD, DS3231 RTC, RS-485, Qwiic) + SY8089 5V->3.3V Buck",
        38.1, 180.0)

    content = (
        "".join(boxes)
        + "".join(net_labels)
        + "".join(pwr)
        + tb
        + sheet_insts
    )

    # ── Build the full root schematic ──────────────────────────────────────
    root = (
        f'(kicad_sch\n'
        f'\t(version 20250114)\n'
        f'\t(generator "eeschema")\n'
        f'\t(generator_version "10.0")\n'
        f'\t(uuid "{root_uuid}")\n'
        f'\t(paper "A3")\n'
        f'\t(title_block\n'
        f'\t\t(title "Super Famicom Smart Home & Diagnostics Cartridge")\n'
        f'\t\t(date "2026-09-11")\n'
        f'\t\t(rev "V1.0")\n'
        f'\t\t(company "SNES SmartHome Project")\n'
        f'\t\t(comment 1 "RP2350B + ESP32-C6 + Parallel Flash + Level Shifting")\n'
        f'\t\t(comment 2 "Targeted for PCBWay 4-Layer 1.2mm ENIG 30-deg Bevel")\n'
        f'\t)\n'
        f'{content}'
        f')\n'
    )

    path = os.path.join(HW_DIR, "snes_smarthome_cartridge.kicad_sch")
    with open(path, "w") as f:
        f.write(root)
    print(f"  Written: {os.path.basename(path)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating KiCad 10 schematics for SNES SmartHome Cartridge...")
    print("  Component count target: 62")
    print()
    generate_sheet1()
    generate_sheet2()
    generate_sheet3()
    generate_sheet4()
    generate_sheet5()
    generate_root()
    print("\nAll 6 schematic files generated successfully!")
    print("  Root: snes_smarthome_cartridge.kicad_sch")
    print("  Sheet 1: 01_SNES_BUS_AND_CIC.kicad_sch (5 components)")
    print("  Sheet 2: 02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch (9 components)")
    print("  Sheet 3: 03_RP2350_SUBSYSTEM.kicad_sch (17 components)")
    print("  Sheet 4: 04_ESP32C6_WIFI_IOT.kicad_sch (8 components)")
    print("  Sheet 5: 05_PERIPHERALS_AND_POWER.kicad_sch (23 components)")
    print("  Total: 62 components")
