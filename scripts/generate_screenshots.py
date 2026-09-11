#!/usr/bin/env python3
"""
Pixel-Perfect SNES Smart Home Screen Renderer
Renders full 256x224 (and 4x 1024x896 integer scaled + CRT simulation)
screenshots using the exact font, sprites, and CGRAM palettes.
"""

import os
import math
from PIL import Image, ImageDraw

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(REPO_ROOT, "snes", "assets", "font.bmp")
ICONS_PATH = os.path.join(REPO_ROOT, "snes", "assets", "icons.bmp")
OUT_DIR = os.path.join(REPO_ROOT, "docs", "screenshots")

# 15-bit SNES BGR555 -> 24-bit RGB converter
def rgb5(r, g, b):
    return (r * 255 // 31, g * 255 // 31, b * 255 // 31)

# Exact CGRAM Palettes defined in ui.c
BG_COLOR = rgb5(1, 2, 6) # Deep Midnight Navy

TEXT_PALETTES = {
    0: rgb5(31, 31, 31), # PAL_WHITE: Pure crisp white
    1: rgb5(31, 27, 4),  # PAL_GOLD: Bright warm gold
    2: rgb5(6, 26, 31),  # PAL_CYAN: Electric cyan
    3: rgb5(31, 8, 4),   # PAL_ORANGE: Fiery coral
    4: rgb5(6, 31, 10),  # PAL_GREEN: Bright emerald lime
    5: rgb5(14, 15, 18), # PAL_GRAY: Muted slate gray
    6: rgb5(27, 12, 31), # PAL_PURPLE: Electric violet
    7: rgb5(31, 18, 4),  # PAL_AMBER: Warm amber
}

def load_assets():
    font_raw = Image.open(FONT_PATH).convert("RGBA")
    icons_raw = Image.open(ICONS_PATH).convert("RGBA")
    return font_raw, icons_raw

def draw_char(fb, font_img, ch, tile_x, tile_y, color):
    ascii_code = ord(ch)
    # Font contains 96 glyphs starting at ASCII 32 (' ')
    glyph_idx = ascii_code - 32
    if glyph_idx < 0 or glyph_idx >= 96:
        return
    src_x = glyph_idx * 8
    glyph = font_img.crop((src_x, 0, src_x + 8, 8))
    
    px = tile_x * 8
    py = tile_y * 8
    
    for y in range(8):
        for x in range(8):
            r, g, b, a = glyph.getpixel((x, y))
            # Foreground pixels in font.bmp are non-black
            if r > 30 or g > 30 or b > 30:
                fb.putpixel((px + x, py + y), color)

def draw_string(fb, font_img, text, tile_x, tile_y, pal_id):
    color = TEXT_PALETTES[pal_id]
    for i, ch in enumerate(text):
        draw_char(fb, font_img, ch, tile_x + i, tile_y, color)

def draw_sprite(fb, icons_img, icon_idx, px, py):
    # icons_img is 16x320 containing 20 icons vertically (16x16 each)
    src_y = icon_idx * 16
    icon = icons_img.crop((0, src_y, 16, src_y + 16))
    
    for y in range(16):
        for x in range(16):
            r, g, b, a = icon.getpixel((x, y))
            # Color 0 in SNES sprite palette is transparent (pure black in icons.bmp)
            if (r, g, b) != (0, 0, 0):
                target_x = px + x
                target_y = py + y
                if 0 <= target_x < 256 and 0 <= target_y < 224:
                    fb.putpixel((target_x, target_y), (r, g, b))

def render_frame(page_num, cursor_idx):
    font_img, icons_img = load_assets()
    # 256x224 standard SNES NTSC screen
    fb = Image.new("RGB", (256, 224), BG_COLOR)

    # Header
    draw_string(fb, font_img, "SUPER HOME SYSTEM", 1, 1, 1) # PAL_GOLD
    draw_string(fb, font_img, "LIVE", 26, 1, 4)             # PAL_GREEN
    # Pulsating live circle (drawn at col 24)
    draw_char(fb, font_img, chr(32), 24, 1, TEXT_PALETTES[4])
    draw_circle_dot(fb, 24 * 8 + 4, 1 * 8 + 3, TEXT_PALETTES[4])

    draw_string(fb, font_img, "--------------------------------", 0, 2, 0)
    draw_string(fb, font_img, "Device", 5, 3, 0)
    draw_string(fb, font_img, "Type", 18, 3, 0)
    draw_string(fb, font_img, "State", 24, 3, 0)

    # Entity definitions
    entities_page1 = [
        # (name, dom_tag, state, val, dom_pal, st_pal, sprite_idx)
        ("Sala Light",  "LIGHT", "ON",    "",   1, 4, 1),   # Bulb ON (icon 1)
        ("Porta Garag", "COVER", "CLSD",  "0",  7, 5, 4),   # Garage Closed (icon 4)
        ("Ar Condic.",  "CLIM ", "21.5",  "C",  3, 4, 10),  # AC Cool (icon 10)
        ("Temp. Exter", "SENSR", "28.6",  "C",  2, 3, 11),  # Temp Flame Warm (icon 11)
        ("Quarto Bebe", "SENSR", "19.4",  "C",  2, 2, 10),  # Temp Cool (icon 10)
        ("Umidade Sal", "SENSR", "62.0",  "%",  2, 2, 12),  # Humidity Water Drop (icon 12)
        ("Ventilador",  "FAN  ", "ON",    "",   2, 4, 8),   # Fan Rotor (icon 8)
    ]

    entities_page2 = [
        ("Fechadura",   "LOCK ", "LOCKD", "",   7, 5, 6),   # Lock Closed (icon 6)
        ("Spotify Sala","MEDIA", "PLAY",  "",   6, 6, 17),  # Media Music Notes (icon 17)
        ("Alarme Gar.", "ALERT", "DETECT","",   3, 3, 15),  # Alarm Warning Triangle (icon 15)
        ("Cafeteira",   "SWTCH", "OFF",   "",   0, 5, 2),   # Switch OFF (icon 2)
    ]

    entities = entities_page1 if page_num == 1 else entities_page2

    for row_i, item in enumerate(entities):
        visual_row = 5 + row_i * 2
        name, dom_tag, state, val, dom_pal, st_pal, sprite_idx = item
        
        # Name color
        is_sel = (row_i == cursor_idx)
        name_pal = 1 if is_sel else 0
        
        # Draw text
        draw_string(fb, font_img, f"{name:<11}", 5, visual_row, name_pal)
        draw_string(fb, font_img, f"{dom_tag:<5}", 18, visual_row, dom_pal)
        full_st = f"{state}{val}"
        draw_string(fb, font_img, f"{full_st:<7}", 24, visual_row, st_pal)

        # Draw 16x16 domain sprite at X=20, Y=visual_row*8 - 4
        spr_x = 20
        spr_y = visual_row * 8 - 4
        draw_sprite(fb, icons_img, sprite_idx, spr_x, spr_y)

        # Draw animated pointer cursor if selected
        if is_sel:
            draw_sprite(fb, icons_img, 18, 5, spr_y) # Cursor Frame 1 (icon 18)

    # Footer
    page_txt = f"PAGE {page_num}/2"
    draw_string(fb, font_img, page_txt, 1, 21, 1) # PAL_GOLD
    draw_string(fb, font_img, "DEVICES: 11", 12, 21, 7) # PAL_AMBER
    draw_string(fb, font_img, "OK-IOT", 25, 21, 4) # PAL_GREEN

    draw_string(fb, font_img, "A:Action  B:Poll  L/R:Page", 1, 23, 0) # PAL_WHITE

    return fb

def draw_circle_dot(fb, cx, cy, color):
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx*dx + dy*dy <= 5:
                fb.putpixel((cx + dx, cy + dy), color)

def apply_crt_simulation(base_img):
    # Scale up 4x with scanlines and phosphor glow
    w, h = base_img.size
    scale = 4
    out_w, out_h = w * scale, h * scale
    
    # Crisp upscale
    scaled = base_img.resize((out_w, out_h), Image.NEAREST)
    draw = ImageDraw.Draw(scaled)
    
    # CRT scanlines
    for y in range(0, out_h, 4):
        draw.line([(0, y + 3), (out_w, y + 3)], fill=(0, 0, 0, 140))
        draw.line([(0, y + 2), (out_w, y + 2)], fill=(0, 0, 0, 70))
        
    return scaled

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 1. Page 1 (Native 256x224 & 4x Scaled)
    p1 = render_frame(page_num=1, cursor_idx=0)
    p1_scaled = p1.resize((256 * 4, 224 * 4), Image.NEAREST)
    p1_path = os.path.join(OUT_DIR, "snes_smarthome_page1.png")
    p1_scaled.save(p1_path)
    print(f"Generated: {p1_path}")

    # 2. Page 2 (Native 256x224 & 4x Scaled)
    p2 = render_frame(page_num=2, cursor_idx=1) # Spotify selected
    p2_scaled = p2.resize((256 * 4, 224 * 4), Image.NEAREST)
    p2_path = os.path.join(OUT_DIR, "snes_smarthome_page2.png")
    p2_scaled.save(p2_path)
    print(f"Generated: {p2_path}")

    # 3. CRT Retro Simulation View
    crt_img = apply_crt_simulation(p1)
    crt_path = os.path.join(OUT_DIR, "snes_smarthome_crt.png")
    crt_img.save(crt_path)
    print(f"Generated: {crt_path}")

if __name__ == "__main__":
    main()
