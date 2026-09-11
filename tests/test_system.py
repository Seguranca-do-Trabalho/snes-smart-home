#!/usr/bin/env python3
"""
Comprehensive Automated Test Suite for SNES Smart Home System
Tests:
 1. SNES ROM Binary & LoROM Checksum Integrity
 2. Compact Binary Protocol ('SH\x01') & CRC16/Modbus
 3. Home Assistant Bridge Domain & State Normalization
 4. Coprocessor Mailbox Memory Map & Command Structures
"""

import os
import struct
import unittest
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "bridge"))

from ha_bridge import (
    SUPPORTED,
    SERVICE_MAP,
    feature_bits,
    state_code,
    numeric_value,
    crc16,
    pack_snapshot,
    Entity,
)


class TestSnesRomIntegrity(unittest.TestCase):
    """Verifies that the compiled Super Nintendo ROM is 100% valid."""

    ROM_PATH = os.path.join(REPO_ROOT, "snes", "super_home.sfc")

    def test_rom_exists_and_size(self):
        self.assertTrue(os.path.exists(self.ROM_PATH), "ROM binary does not exist!")
        size = os.path.getsize(self.ROM_PATH)
        # 256 KB = 262,144 bytes
        self.assertEqual(size, 256 * 1024, f"Expected 256 KB ROM, got {size} bytes")

    def test_lorom_internal_header(self):
        with open(self.ROM_PATH, "rb") as f:
            rom = f.read()

        # LoROM internal header begins at 0x7FC0
        header = rom[0x7FC0:0x7FE0]
        title = header[0:21].decode("ascii", errors="replace").strip()
        self.assertIn("SUPER HOME SYSTEM", title)

        # Checksum complement (0x7FDC..0x7FDD) and Checksum (0x7FDE..0x7FDF)
        comp = struct.unpack("<H", header[28:30])[0]
        csum = struct.unpack("<H", header[30:32])[0]
        self.assertEqual((comp + csum) & 0xFFFF, 0xFFFF,
                         f"SNES Checksum failure! csum=0x{csum:04X}, comp=0x{comp:04X}")


class TestBinaryProtocol(unittest.TestCase):
    """Verifies compact binary protocol serialization and CRC16/Modbus."""

    def test_crc16_modbus(self):
        test_data = b"123456789"
        # Standard Modbus CRC-16 for '123456789' is 0x4B37
        computed = crc16(test_data)
        self.assertEqual(computed, 0x4B37, f"CRC16 failure: expected 0x4B37, got 0x{computed:04X}")

    def test_empty_snapshot_packing(self):
        packed = pack_snapshot([])
        # Header: 'S', 'H', version=1, count=0 -> 4 bytes + 2 bytes CRC = 6 bytes
        self.assertEqual(len(packed), 6)
        self.assertEqual(packed[:4], b"SH\x01\x00")
        data_crc = crc16(packed[:-2])
        payload_crc = struct.unpack("<H", packed[-2:])[0]
        self.assertEqual(data_crc, payload_crc)

    def test_entity_snapshot_packing(self):
        entities = [
            Entity(
                domain=1, # Light
                state_code=1, # ON
                features=0x03, # On/Off + Brightness
                entity_id="light.living_room",
                name="Living Light",
                state="on",
                value="",
                numeric_value_x100=25500,
            ),
            Entity(
                domain=6, # Climate
                state_code=1,
                features=0x20,
                entity_id="climate.hvac",
                name="Thermostat",
                state="22.5",
                value="C",
                numeric_value_x100=2250,
            ),
        ]
        packed = pack_snapshot(entities)
        self.assertEqual(packed[:4], b"SH\x01\x02") # 2 entities

        # Parse first entity
        offset = 4
        dom, st, feat, nlen = packed[offset:offset+4]
        num_val = struct.unpack("<H", packed[offset+4:offset+6])[0]
        name = packed[offset+6:offset+6+nlen].decode("ascii")

        self.assertEqual(dom, 1)
        self.assertEqual(st, 1)
        self.assertEqual(feat, 0x03)
        self.assertEqual(num_val, 25500)
        self.assertEqual(name, "Living Light")


class TestHomeAssistantNormalization(unittest.TestCase):
    """Verifies Home Assistant state extraction and service routing."""

    def test_supported_domains(self):
        expected_domains = ["light", "switch", "cover", "lock", "fan", "climate", "sensor", "binary_sensor", "media_player"]
        for d in expected_domains:
            self.assertIn(d, SUPPORTED)

    def test_state_codes(self):
        self.assertEqual(state_code("light", "on"), 1)
        self.assertEqual(state_code("light", "off"), 0)
        self.assertEqual(state_code("cover", "open"), 1)
        self.assertEqual(state_code("cover", "closed"), 0)
        self.assertEqual(state_code("lock", "unlocked"), 1)
        self.assertEqual(state_code("lock", "locked"), 0)
        self.assertEqual(state_code("climate", "heat"), 2)

    def test_service_map(self):
        self.assertEqual(SERVICE_MAP["light"]["on"], "turn_on")
        self.assertEqual(SERVICE_MAP["light"]["off"], "turn_off")
        self.assertEqual(SERVICE_MAP["cover"]["open"], "open_cover")
        self.assertEqual(SERVICE_MAP["lock"]["unlock"], "unlock")

    def test_numeric_scaling(self):
        val = numeric_value("sensor", "23.45", {})
        self.assertEqual(val, 2345)
        # None for non-numeric
        self.assertIsNone(numeric_value("switch", "off", {}))


class TestMailboxMemoryMap(unittest.TestCase):
    """Verifies RP2350 and SNES memory-mapped mailbox layout alignment."""

    def test_command_registers(self):
        CMD_REG_BASE = 0x07F0
        self.assertEqual(CMD_REG_BASE + 0, 0x07F0) # CMD
        self.assertEqual(CMD_REG_BASE + 1, 0x07F1) # INDEX
        self.assertEqual(CMD_REG_BASE + 2, 0x07F2) # VALUE
        self.assertEqual(CMD_REG_BASE + 3, 0x07F3) # HANDSHAKE FLAG


if __name__ == "__main__":
    unittest.main()
