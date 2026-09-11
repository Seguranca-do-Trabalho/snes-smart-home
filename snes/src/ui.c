#include "ui.h"
#include "cartio.h"
#include "config.h"
#include "audio.h"
#include <snes.h>
#include <stdio.h>
#include <string.h>

extern char font_til, font_pal;
extern char icons_til, icons_pal, icons_tilend, icons_palend;

#define PAL_WHITE  0
#define PAL_GOLD   1
#define PAL_CYAN   2
#define PAL_ORANGE 3
#define PAL_GREEN  4
#define PAL_GRAY   5
#define PAL_PURPLE 6
#define PAL_AMBER  7

static u8 selected = 0;
static u8 page = 0;
static u8 last_count = 0xFF;
static u16 refresh_counter = 0;
static u16 anim_tick = 0;

static const u8 cursor_bounce[8] = { 0, 1, 2, 3, 2, 1, 0, 0 };

static const char *domain_tag(u8 d) {
    switch (d) {
        case ENTITY_LIGHT:         return "LIGHT";
        case ENTITY_SWITCH:        return "SWTCH";
        case ENTITY_COVER:         return "COVER";
        case ENTITY_LOCK:          return "LOCK ";
        case ENTITY_FAN:           return "FAN  ";
        case ENTITY_CLIMATE:       return "CLIM ";
        case ENTITY_SENSOR:        return "SENSR";
        case ENTITY_BINARY_SENSOR: return "ALERT";
        case ENTITY_MEDIA:         return "MEDIA";
        default:                   return "OTHER";
    }
}

static u8 domain_color(u8 d) {
    switch (d) {
        case ENTITY_LIGHT:         return PAL_GOLD;
        case ENTITY_SWITCH:        return PAL_WHITE;
        case ENTITY_COVER:         return PAL_AMBER;
        case ENTITY_LOCK:          return PAL_AMBER;
        case ENTITY_FAN:           return PAL_CYAN;
        case ENTITY_CLIMATE:       return PAL_ORANGE;
        case ENTITY_SENSOR:        return PAL_CYAN;
        case ENTITY_BINARY_SENSOR: return PAL_ORANGE;
        case ENTITY_MEDIA:         return PAL_PURPLE;
        default:                   return PAL_WHITE;
    }
}

/* Compute exact 16x16 sprite tile index with animation frames */
static u8 get_entity_sprite_tile(Entity *e, u16 tick) {
    switch (e->domain) {
        case ENTITY_LIGHT:
            /* Tile 2 = glowing bulb with rays, Tile 0 = dark bulb */
            return (e->state_code == 1) ? 2 : 0;

        case ENTITY_SWITCH:
            /* Tile 6 = rocker up green, Tile 4 = rocker down */
            return (e->state_code == 1) ? 6 : 4;

        case ENTITY_COVER:
            /* Tile 10 = open garage with retro car, Tile 8 = closed shutter */
            return (e->state_code == 1) ? 10 : 8;

        case ENTITY_LOCK:
            /* Tile 14 = open shackle, Tile 12 = closed padlock */
            return (e->state_code == 1) ? 14 : 12;

        case ENTITY_FAN:
            /* If running, rotate between 0 deg (tile 32) and 45 deg (tile 34) */
            if (e->state_code == 1)
                return ((tick >> 3) & 1) ? 34 : 32;
            return 32;

        case ENTITY_CLIMATE:
            /* If temp > 24.0 C: tile 38 (warm flame), else tile 36 (snowflake) */
            if (e->numeric_value != 0xFFFF && e->numeric_value > 2400)
                return 38;
            return 36;

        case ENTITY_SENSOR:
            /* If humidity: tile 40 (water drop), if energy: tile 42 (lightning) */
            if (e->value[0] == '%')
                return 40;
            if (e->value[0] == 'W' || e->value[0] == 'k' || e->value[0] == 'V')
                return 42;
            if (e->numeric_value != 0xFFFF && e->numeric_value > 2400)
                return 38; /* Warm temp */
            return 36;

        case ENTITY_BINARY_SENSOR:
            /* Tile 46 = alert triangle, Tile 44 = green shield */
            return (e->state_code == 1) ? 46 : 44;

        case ENTITY_MEDIA:
            /* Tile 66 = music notes, Tile 64 = speaker */
            return (e->state_code == 1) ? 66 : 64;

        default:
            return 0;
    }
}

static u8 get_state_color(Entity *e) {
    if (e->domain == ENTITY_CLIMATE || e->domain == ENTITY_SENSOR) {
        if (e->value[0] == '%')
            return PAL_CYAN; /* Humidity in cyan */
        if (e->numeric_value != 0xFFFF) {
            if (e->numeric_value > 2500)
                return PAL_ORANGE; /* Warm / Hot: red-orange */
            if (e->numeric_value < 2100)
                return PAL_CYAN;   /* Cold / Cool: electric cyan */
            return PAL_GREEN;      /* Comfortable: emerald green */
        }
    }

    if (e->state_code == 1)
        return (e->domain == ENTITY_MEDIA) ? PAL_PURPLE : PAL_GREEN;

    return PAL_GRAY;
}

static void draw_text(u8 x, u8 y, u8 pal, const char *text) {
    consoleDrawTextMap(x, y, (u8 *)scr_txt_font_map, (pal << 2), "%s", text);
}

static void clear_row(u8 row) {
    draw_text(0, row, PAL_WHITE, "                                ");
}

static void draw_header(void) {
    char live_tag[12];
    /* Animated pulsating live dot */
    if ((anim_tick >> 4) & 1)
        strcpy(live_tag, "● LIVE");
    else
        strcpy(live_tag, "○ LIVE");

    draw_text(1, 1, PAL_GOLD, "SUPER HOME SYSTEM");
    draw_text(24, 1, PAL_GREEN, live_tag);
    draw_text(0, 2, PAL_WHITE, "────────────────────────────────");
    draw_text(5, 3, PAL_WHITE, "Device");
    draw_text(18, 3, PAL_WHITE, "Type");
    draw_text(24, 3, PAL_WHITE, "State");
}

static void draw_entity_row(u8 visual_row, u8 index) {
    Entity *e = cartio_entity(index);
    char name_buf[14];
    char state_buf[10];
    u8 name_color, st_color, dom_color, sprite_tile;
    u16 spr_id;

    if (!e)
        return;

    clear_row(visual_row);

    /* Highlight selected item in gold */
    name_color = (selected == index) ? PAL_GOLD : PAL_WHITE;
    st_color   = get_state_color(e);
    dom_color  = domain_color(e->domain);

    /* Device name */
    strncpy(name_buf, e->name, 11);
    name_buf[11] = '\0';
    consoleDrawTextMap(5, visual_row, (u8 *)scr_txt_font_map, (name_color << 2), "%-11s", name_buf);

    /* Domain tag */
    consoleDrawTextMap(18, visual_row, (u8 *)scr_txt_font_map, (dom_color << 2), "%-5s", domain_tag(e->domain));

    /* State / Value */
    if (e->value[0])
        sprintf(state_buf, "%s%s", e->state, e->value);
    else
        sprintf(state_buf, "%s", e->state);

    consoleDrawTextMap(24, visual_row, (u8 *)scr_txt_font_map, (st_color << 2), "%-7s", state_buf);

    /* 16x16 Animated Domain Sprite placed at X=20, Y=visual_row*8 - 4 */
    spr_id = (u16)((visual_row - 3) * 4);
    sprite_tile = get_entity_sprite_tile(e, anim_tick);
    oamSet(spr_id, 20, (u16)(visual_row * 8 - 4), 3, 0, 0, sprite_tile, 0);
    oamSetEx(spr_id, OBJ_SMALL, OBJ_SHOW);
}

void ui_init(void) {
    consoleInit();
    consoleInitText(0, 16, (u8 *)&font_til, (u8 *)&font_pal);

    /* Background 1 Text Palettes (CGRAM 0..127) */
    /* Pal 0: White / Gray */
    setPaletteColor(0,  RGB5(1, 2, 6));    /* Background: Deep Navy */
    setPaletteColor(1,  RGB5(31, 31, 31)); /* Crisp Pure White */
    setPaletteColor(2,  RGB5(20, 21, 24)); /* Slate Silver */

    /* Pal 1: Gold / Yellow (Selection & Header) */
    setPaletteColor(16, RGB5(1, 2, 6));
    setPaletteColor(17, RGB5(31, 27, 4));  /* Bright Gold */
    setPaletteColor(18, RGB5(24, 18, 2));

    /* Pal 2: Cyan (Cold Temp <21C, Humidity) */
    setPaletteColor(32, RGB5(1, 2, 6));
    setPaletteColor(33, RGB5(6, 26, 31));  /* Electric Cyan */
    setPaletteColor(34, RGB5(2, 16, 22));

    /* Pal 3: Orange-Red (Warm Temp >25C, Hazard) */
    setPaletteColor(48, RGB5(1, 2, 6));
    setPaletteColor(49, RGB5(31, 8, 4));   /* Fiery Coral */
    setPaletteColor(50, RGB5(22, 4, 2));

    /* Pal 4: Bright Lime Green (ON, OPEN, Comfort 21-25C) */
    setPaletteColor(64, RGB5(1, 2, 6));
    setPaletteColor(65, RGB5(6, 31, 10));  /* Bright Emerald */
    setPaletteColor(66, RGB5(2, 20, 5));

    /* Pal 5: Charcoal Gray (OFF, CLOSED, LOCKED) */
    setPaletteColor(80, RGB5(1, 2, 6));
    setPaletteColor(81, RGB5(14, 15, 18)); /* Muted Gray */
    setPaletteColor(82, RGB5(8, 9, 11));

    /* Pal 6: Neon Purple (Media, Music) */
    setPaletteColor(96, RGB5(1, 2, 6));
    setPaletteColor(97, RGB5(27, 12, 31)); /* Electric Violet */
    setPaletteColor(98, RGB5(18, 6, 22));

    /* Pal 7: Amber Gold (Device badge, tags) */
    setPaletteColor(112, RGB5(1, 2, 6));
    setPaletteColor(113, RGB5(31, 18, 4)); /* Warm Amber */
    setPaletteColor(114, RGB5(22, 10, 2));

    /* Sprite OAM Init (OBJ_SIZE16_L32: small=16x16, large=32x32) */
    oamInitGfxSet((u8 *)&icons_til, (&icons_tilend - &icons_til),
                  (u8 *)&icons_pal, (&icons_palend - &icons_pal),
                  0, 0x0000, OBJ_SIZE16_L32);

    /* Initialize SPC700 Audio Engine */
    audio_init();

    cartio_init();
    cartio_refresh();
    ui_draw();
}

void ui_draw(void) {
    u8 count = cartio_count();
    u8 start = page * UI_ROWS_PER_PAGE;
    u8 end = start + UI_ROWS_PER_PAGE;
    u8 i, r;
    char ptxt[32];

    if (end > count)
        end = count;

    draw_header();

    if (!count) {
        for (r = 4; r < 20; r++)
            clear_row(r);
        draw_text(6, 9, PAL_AMBER, "NO ENTITIES RECEIVED");
        draw_text(3, 11, PAL_WHITE, "Waiting for Home Assistant...");
        for (i = 0; i <= UI_ROWS_PER_PAGE; i++)
            oamSetEx((u16)(i * 4), OBJ_SMALL, OBJ_HIDE);
    } else {
        for (i = start; i < end; i++) {
            draw_entity_row(5 + (i - start) * 2, i);
        }
        /* Hide unused sprites on this page */
        for (i = (end - start); i < UI_ROWS_PER_PAGE; i++) {
            clear_row(5 + i * 2);
            oamSetEx((u16)((i + 2) * 4), OBJ_SMALL, OBJ_HIDE);
        }
    }

    clear_row(20);
    clear_row(21);
    clear_row(22);
    clear_row(23);

    /* Footer: Page & Device badges */
    sprintf(ptxt, "PAGE %d/%d",
            count ? (page + 1) : 1,
            count ? ((count + UI_ROWS_PER_PAGE - 1) / UI_ROWS_PER_PAGE) : 1);
    draw_text(1, 21, PAL_GOLD, ptxt);

    sprintf(ptxt, "DEVICES: %d", count);
    draw_text(14, 21, PAL_AMBER, ptxt);

    draw_text(25, 21, PAL_GREEN, "OK-IOT");

    /* Controls line */
    draw_text(1, 23, PAL_WHITE, "A:Action  B:Poll  L/R:Page");
}

void ui_update(void) {
    u16 down = padsDown(0);
    u8 count = cartio_count();
    u8 cursor_x, cursor_tile;
    u16 cursor_y;

    anim_tick++;

    /* Service audio processor */
    audio_process();

    /* Animate selection pointer (Sprite ID 0) */
    if (count) {
        cursor_x = 4 + cursor_bounce[(anim_tick >> 2) & 7];
        cursor_y = (u16)((5 + (selected % UI_ROWS_PER_PAGE) * 2) * 8 - 4);
        cursor_tile = ((anim_tick >> 3) & 1) ? 68 : 70;
        oamSet(0, cursor_x, cursor_y, 3, 0, 0, cursor_tile, 0);
        oamSetEx(0, OBJ_SMALL, OBJ_SHOW);
    } else {
        oamSetEx(0, OBJ_SMALL, OBJ_HIDE);
    }

    /* Live animation updates for fan and pulsating indicators */
    if ((anim_tick & 7) == 0) {
        u8 start = page * UI_ROWS_PER_PAGE;
        u8 end = start + UI_ROWS_PER_PAGE;
        u8 i;
        if (end > count)
            end = count;
        for (i = start; i < end; i++) {
            Entity *e = cartio_entity(i);
            if (e && (e->domain == ENTITY_FAN || e->domain == ENTITY_LIGHT || e->domain == ENTITY_MEDIA)) {
                u8 visual_row = 5 + (i - start) * 2;
                u16 spr_id = (u16)((visual_row - 3) * 4);
                u8 sprite_tile = get_entity_sprite_tile(e, anim_tick);
                oamSet(spr_id, 20, (u16)(visual_row * 8 - 4), 3, 0, 0, sprite_tile, 0);
            }
        }
        /* Update pulsing header live dot */
        if ((anim_tick & 31) == 0)
            draw_header();
    }

    refresh_counter++;
    if (refresh_counter >= UI_REFRESH_FRAMES) {
        refresh_counter = 0;
        cartio_refresh();
        count = cartio_count();
        if (count != last_count) {
            last_count = count;
            if (selected >= count && count)
                selected = count - 1;
            page = count ? selected / UI_ROWS_PER_PAGE : 0;
            ui_draw();
        }
    }

    /* Directional navigation with sound effects */
    if (down & KEY_DOWN) {
        if (count) {
            selected = (selected + 1) % count;
            page = selected / UI_ROWS_PER_PAGE;
            audio_play_nav();
            ui_draw();
        }
    }
    if (down & KEY_UP) {
        if (count) {
            selected = (selected == 0 ? count - 1 : selected - 1);
            page = selected / UI_ROWS_PER_PAGE;
            audio_play_nav();
            ui_draw();
        }
    }
    if (down & KEY_LEFT) {
        if (page) {
            page--;
            selected = page * UI_ROWS_PER_PAGE;
            audio_play_page();
            ui_draw();
        }
    }
    if (down & KEY_RIGHT) {
        u8 pages = (count + UI_ROWS_PER_PAGE - 1) / UI_ROWS_PER_PAGE;
        if (page + 1 < pages) {
            page++;
            selected = page * UI_ROWS_PER_PAGE;
            audio_play_page();
            ui_draw();
        }
    }
    if (down & KEY_B) {
        audio_play_refresh();
        cartio_refresh();
        ui_draw();
    }
    if ((down & KEY_A) && count) {
        Entity *e = cartio_entity(selected);
        if (e) {
            u8 old_state = e->state_code;
            if (e->domain == ENTITY_LIGHT || e->domain == ENTITY_SWITCH || e->domain == ENTITY_FAN)
                cartio_command(selected, 1);
            else if (e->domain == ENTITY_COVER)
                cartio_command(selected, 2);
            else if (e->domain == ENTITY_LOCK)
                cartio_command(selected, 3);
            else if (e->domain == ENTITY_MEDIA)
                cartio_command(selected, 4);
            else if (e->domain == ENTITY_CLIMATE)
                cartio_command(selected, 5);

            /* Play audio feedback matching action */
            audio_play_toggle(old_state == 0);
            ui_draw();
        }
    }
}
