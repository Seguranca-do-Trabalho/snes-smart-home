#include "ui.h"
#include "cartio.h"
#include "config.h"
#include <snes.h>
#include <stdio.h>
#include <string.h>

extern char font_til, font_pal;
extern char icons_til, icons_pal, icons_tilend, icons_palend;

static u8 selected = 0;
static u8 page = 0;
static u8 last_count = 0xFF;
static u16 refresh_counter = 0;

static const char *domain_name(u8 d) {
    switch (d) {
        case ENTITY_LIGHT:         return "LIGHT";
        case ENTITY_SWITCH:        return "SWTCH";
        case ENTITY_COVER:         return "COVER";
        case ENTITY_LOCK:          return "LOCK ";
        case ENTITY_FAN:           return "FAN  ";
        case ENTITY_CLIMATE:       return "CLIM ";
        case ENTITY_SENSOR:        return "SENSR";
        case ENTITY_BINARY_SENSOR: return "BINRY";
        case ENTITY_MEDIA:         return "MEDIA";
        default:                   return "OTHER";
    }
}

static u8 icon_tile(u8 d) {
    switch (d) {
        case ENTITY_LIGHT:         return 0;
        case ENTITY_SWITCH:        return 2;
        case ENTITY_COVER:         return 4;
        case ENTITY_LOCK:          return 6;
        case ENTITY_FAN:           return 8;
        case ENTITY_CLIMATE:       return 10;
        case ENTITY_SENSOR:        return 12;
        case ENTITY_BINARY_SENSOR: return 14;
        case ENTITY_MEDIA:         return 16;
        default:                   return 18;
    }
}

static void clear_row(u8 row) {
    consoleDrawText(0, row, "                                ");
}

static void draw_header(void) {
    consoleDrawText(0, 1, " SUPER HOME SYSTEM    V0.2-IOT  ");
    consoleDrawText(0, 2, "--------------------------------");
    consoleDrawText(0, 3, "   Device        Type   State   ");
}

static void draw_entity_row(u8 visual_row, u8 index) {
    Entity *e = cartio_entity(index);
    char name_buf[14];
    u16 spr_id = (u16)((visual_row - 4) * 4);
    if (!e)
        return;

    clear_row(visual_row);

    /* Cursor */
    consoleDrawText(0, visual_row, "%s", (selected == index) ? ">" : " ");

    /* Truncate name to 12 chars */
    strncpy(name_buf, e->name, 12);
    name_buf[12] = '\0';
    consoleDrawText(3, visual_row, "%-12s", name_buf);

    /* Domain short name */
    consoleDrawText(17, visual_row, "%-5s", domain_name(e->domain));

    /* State / Value */
    if (e->value[0])
        consoleDrawText(24, visual_row, "%s %s", e->state, e->value);
    else
        consoleDrawText(24, visual_row, "%s", e->state);

    /* Sprite Icon placed at X=10, Y=visual_row*8 - 4 */
    oamSet(spr_id, 10, (u16)(visual_row * 8 - 4), 3, 0, 0, icon_tile(e->domain), 0);
    oamSetEx(spr_id, OBJ_SMALL, OBJ_SHOW);
}

void ui_init(void) {
    consoleInit();
    consoleInitText(0, 16, (u8 *)&font_til, (u8 *)&font_pal);
    setPaletteColor(0, RGB5(1, 2, 6));    /* Background: deep navy blue */
    setPaletteColor(1, RGB5(31, 31, 31)); /* Text: bright white */

    oamInitGfxSet((u8 *)&icons_til, (&icons_tilend - &icons_til),
                  (u8 *)&icons_pal, (&icons_palend - &icons_pal),
                  0, 0x0000, OBJ_SIZE16_L32);

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
        consoleDrawText(5, 8, "NO ENTITIES RECEIVED");
        consoleDrawText(3, 10, "Waiting for Home Assistant...");
        for (i = 0; i < UI_ROWS_PER_PAGE; i++)
            oamSetEx((u16)(i * 4), OBJ_SMALL, OBJ_HIDE);
    } else {
        for (i = start; i < end; i++) {
            draw_entity_row(4 + (i - start) * 2, i);
        }
        /* Clear any remaining rows on this page */
        for (i = (end - start); i < UI_ROWS_PER_PAGE; i++) {
            clear_row(4 + i * 2);
            oamSetEx((u16)(i * 4), OBJ_SMALL, OBJ_HIDE);
        }
    }

    clear_row(21);
    clear_row(22);
    clear_row(23);

    sprintf(ptxt, "PAGE %d/%d   DEVICES: %d",
            count ? (page + 1) : 1,
            count ? ((count + UI_ROWS_PER_PAGE - 1) / UI_ROWS_PER_PAGE) : 1,
            count);
    consoleDrawText(1, 21, "%s", ptxt);
    consoleDrawText(1, 23, "A:ACTION  B:POLL  L/R:PAGE");
}

void ui_update(void) {
    u16 down = padsDown(0);
    u8 count = cartio_count();

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

    if (down & KEY_DOWN) {
        if (count) {
            selected = (selected + 1) % count;
            page = selected / UI_ROWS_PER_PAGE;
            ui_draw();
        }
    }
    if (down & KEY_UP) {
        if (count) {
            selected = (selected == 0 ? count - 1 : selected - 1);
            page = selected / UI_ROWS_PER_PAGE;
            ui_draw();
        }
    }
    if (down & KEY_LEFT) {
        if (page) {
            page--;
            selected = page * UI_ROWS_PER_PAGE;
            ui_draw();
        }
    }
    if (down & KEY_RIGHT) {
        u8 pages = (count + UI_ROWS_PER_PAGE - 1) / UI_ROWS_PER_PAGE;
        if (page + 1 < pages) {
            page++;
            selected = page * UI_ROWS_PER_PAGE;
            ui_draw();
        }
    }
    if (down & KEY_B) {
        cartio_refresh();
        ui_draw();
    }
    if ((down & KEY_A) && count) {
        Entity *e = cartio_entity(selected);
        if (e) {
            if (e->domain == ENTITY_LIGHT || e->domain == ENTITY_SWITCH || e->domain == ENTITY_FAN)
                cartio_command(selected, 1);
            else if (e->domain == ENTITY_COVER)
                cartio_command(selected, 2);
            ui_draw();
        }
    }
}
