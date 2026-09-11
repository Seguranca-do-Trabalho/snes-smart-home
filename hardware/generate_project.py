#!/usr/bin/env python3
import os, uuid, json

HW_DIR = os.path.dirname(os.path.abspath(__file__))

def uid():
    return str(uuid.uuid4())

# 1. Generate kicad.kicad_pro
pro_data = {
  "board": {
    "design_settings": {
      "defaults": {
        "board_thickness": 1.2
      },
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {},
      "track_widths": [0.15, 0.2, 0.25, 0.3, 0.5, 0.8, 1.0],
      "via_dimensions": [
        {"diameter": 0.6, "drill": 0.3},
        {"diameter": 0.8, "drill": 0.4}
      ]
    }
  },
  "boards": [],
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "snes_smarthome_cartridge.kicad_pro",
    "version": 1
  },
  "net_settings": {
    "classes": [
      {
        "clearance": 0.15,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.2,
        "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3,
        "wire_width": 0
      },
      {
        "clearance": 0.2,
        "name": "Power",
        "track_width": 0.5,
        "via_diameter": 0.8,
        "via_drill": 0.4,
        "wire_width": 0
      }
    ],
    "meta": {
      "version": 0
    }
  },
  "pcbnew": {
    "page_layout_descr_file": ""
  },
  "sheets": [],
  "text_variables": {
    "COMPANY": "SNES SmartHome Project",
    "REVISION": "V1.0",
    "TITLE": "Super Famicom Smart Home & Diagnostics Cartridge"
  }
}

with open(os.path.join(HW_DIR, "snes_smarthome_cartridge.kicad_pro"), "w") as f:
    json.dump(pro_data, f, indent=2)

print("Generated snes_smarthome_cartridge.kicad_pro")
