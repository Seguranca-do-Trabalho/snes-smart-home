#include "cartio.h"
#include <string.h>

Entity entities[MAX_ENTITIES];
u8 entity_count = 0;

#define CART_MAILBOX_BASE 0x700000

#ifdef SIMULATOR
static void sim_add(u8 domain, u8 state_code, const char *id, const char *name, const char *state, const char *value, u8 features, u16 num_val) {
    Entity *e;
    if (entity_count >= MAX_ENTITIES)
        return;
    e = &entities[entity_count++];
    memset(e, 0, sizeof(Entity));
    e->used = 1;
    e->domain = domain;
    e->state_code = state_code;
    e->features = features;
    e->numeric_value = num_val;
    strncpy(e->entity_id, id, sizeof(e->entity_id) - 1);
    strncpy(e->name, name, MAX_NAME_LEN);
    strncpy(e->state, state, MAX_STATE_LEN);
    strncpy(e->value, value, MAX_VALUE_LEN);
}
#endif

void cartio_init(void) {
    entity_count = 0;
    memset(entities, 0, sizeof(entities));
}

void cartio_refresh(void) {
    volatile u8 *mailbox = (volatile u8 *)CART_MAILBOX_BASE;

    /* Check if hardware mailbox has valid signature 'S', 'H', 0x01 */
    if (mailbox[0] == 'S' && mailbox[1] == 'H' && mailbox[2] == 0x01) {
        u8 count = mailbox[3];
        u16 offset = 4;
        u8 i;
        if (count > MAX_ENTITIES)
            count = MAX_ENTITIES;
        entity_count = 0;

        for (i = 0; i < count; i++) {
            Entity *e = &entities[i];
            u8 name_len;
            u16 num_val;

            memset(e, 0, sizeof(Entity));
            e->used = 1;
            e->domain = mailbox[offset++];
            e->state_code = mailbox[offset++];
            e->features = mailbox[offset++];
            name_len = mailbox[offset++];
            num_val = mailbox[offset] | (mailbox[offset + 1] << 8);
            offset += 2;
            e->numeric_value = num_val;

            if (name_len > MAX_NAME_LEN)
                name_len = MAX_NAME_LEN;
            memcpy(e->name, (const void *)&mailbox[offset], name_len);
            e->name[name_len] = '\0';
            offset += name_len;

            /* Derive state string */
            if (e->state_code == 1) {
                if (e->domain == ENTITY_COVER)
                    strcpy(e->state, "OPEN");
                else if (e->domain == ENTITY_LOCK)
                    strcpy(e->state, "UNLKD");
                else if (e->domain == ENTITY_MEDIA)
                    strcpy(e->state, "PLAY");
                else if (e->domain == ENTITY_BINARY_SENSOR)
                    strcpy(e->state, "DETECT");
                else
                    strcpy(e->state, "ON");
            } else if (e->state_code == 0) {
                if (e->domain == ENTITY_COVER)
                    strcpy(e->state, "CLSD");
                else if (e->domain == ENTITY_LOCK)
                    strcpy(e->state, "LOCKD");
                else if (e->domain == ENTITY_MEDIA)
                    strcpy(e->state, "PAUSE");
                else if (e->domain == ENTITY_BINARY_SENSOR)
                    strcpy(e->state, "CLEAR");
                else
                    strcpy(e->state, "OFF");
            } else {
                if (num_val != 0xFFFF) {
                    u16 int_part = num_val / 100;
                    u16 dec_part = (num_val % 100) / 10;
                    char buf[12];
                    sprintf(buf, "%d.%d", int_part, dec_part);
                    strncpy(e->state, buf, MAX_STATE_LEN);
                } else {
                    strcpy(e->state, "---");
                }
            }
            entity_count++;
        }
        return;
    }

#ifdef SIMULATOR
    if (entity_count == 0) {
        /* Populate rich simulated smart home environment */
        sim_add(ENTITY_LIGHT, 1, "light.sala", "Sala Light", "ON", "", 0x03, 0xFFFF);
        sim_add(ENTITY_COVER, 0, "cover.garagem", "Porta Garagem", "CLSD", "0", 0x45, 0);
        sim_add(ENTITY_CLIMATE, 1, "climate.ar_sala", "Ar Condic.", "21.5", "C", 0x20, 2150);
        sim_add(ENTITY_SENSOR, 2, "sensor.temp_ext", "Temp. Externa", "28.6", "C", 0x20, 2860);
        sim_add(ENTITY_SENSOR, 2, "sensor.quarto_bebe", "Quarto Bebe", "19.4", "C", 0x20, 1940);
        sim_add(ENTITY_SENSOR, 2, "sensor.umidade", "Umidade Sala", "62.0", "%", 0x20, 6200);
        sim_add(ENTITY_FAN, 1, "fan.teto", "Ventilador", "ON", "", 0x01, 0xFFFF);
        sim_add(ENTITY_LOCK, 0, "lock.porta_social", "Fechadura", "LOCKD", "", 0x08, 0xFFFF);
        sim_add(ENTITY_MEDIA, 1, "media_player.sala", "Spotify Sala", "PLAY", "", 0x01, 0xFFFF);
        sim_add(ENTITY_BINARY_SENSOR, 1, "binary_sensor.alarme", "Alarme Gar.", "DETECT", "", 0x01, 0xFFFF);
        sim_add(ENTITY_SWITCH, 0, "switch.cafeteira", "Cafeteira", "OFF", "", 0x01, 0xFFFF);
    }
#endif
}

u8 cartio_count(void) {
    return entity_count;
}

Entity *cartio_entity(u8 index) {
    if (index >= entity_count)
        return 0;
    return &entities[index];
}

u8 cartio_command(u8 index, u8 command) {
    volatile u8 *mailbox = (volatile u8 *)CART_MAILBOX_BASE;
    Entity *e = cartio_entity(index);
    if (!e)
        return 0;

    /* Hardware mailbox command write */
    if (mailbox[0] == 'S' && mailbox[1] == 'H') {
        mailbox[0x07F0] = command;
        mailbox[0x07F1] = index;
        mailbox[0x07F2] = (e->state_code == 1) ? 0 : 1;
        mailbox[0x07F3] = 0x01; /* Handshake flag for RP2350 */
        return 1;
    }

#ifdef SIMULATOR
    if (command == 1 && (e->domain == ENTITY_LIGHT || e->domain == ENTITY_SWITCH || e->domain == ENTITY_FAN)) {
        if (e->state_code == 1) {
            e->state_code = 0;
            strcpy(e->state, "OFF");
        } else {
            e->state_code = 1;
            strcpy(e->state, "ON");
        }
        return 1;
    }
    if (command == 2 && e->domain == ENTITY_COVER) {
        if (e->state_code == 1) {
            e->state_code = 0;
            strcpy(e->state, "CLSD");
            strcpy(e->value, "0");
        } else {
            e->state_code = 1;
            strcpy(e->state, "OPEN");
            strcpy(e->value, "100");
        }
        return 1;
    }
    if (command == 3 && e->domain == ENTITY_LOCK) {
        if (e->state_code == 1) {
            e->state_code = 0;
            strcpy(e->state, "LOCKD");
        } else {
            e->state_code = 1;
            strcpy(e->state, "UNLKD");
        }
        return 1;
    }
    if (command == 4 && e->domain == ENTITY_MEDIA) {
        if (e->state_code == 1) {
            e->state_code = 0;
            strcpy(e->state, "PAUSE");
        } else {
            e->state_code = 1;
            strcpy(e->state, "PLAY");
        }
        return 1;
    }
    if (command == 5 && e->domain == ENTITY_CLIMATE) {
        if (e->state_code == 1) {
            e->state_code = 0;
            strcpy(e->state, "OFF");
        } else {
            e->state_code = 1;
            strcpy(e->state, "21.5");
        }
        return 1;
    }
#endif

    return 0;
}
