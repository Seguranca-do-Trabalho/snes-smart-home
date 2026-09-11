#include "cartio.h"
#include <string.h>

Entity entities[MAX_ENTITIES];
u8 entity_count = 0;

#define CART_MAILBOX_BASE 0x700000

#ifdef SIMULATOR
static void sim_add(u8 domain, const char *id, const char *name, const char *state, const char *value, u8 features) {
    Entity *e;
    if (entity_count >= MAX_ENTITIES)
        return;
    e = &entities[entity_count++];
    memset(e, 0, sizeof(Entity));
    e->used = 1;
    e->domain = domain;
    e->features = features;
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
                else
                    strcpy(e->state, "ON");
            } else if (e->state_code == 0) {
                if (e->domain == ENTITY_COVER)
                    strcpy(e->state, "CLSD");
                else if (e->domain == ENTITY_LOCK)
                    strcpy(e->state, "LOCKD");
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
    entity_count = 0;
    sim_add(ENTITY_LIGHT, "light.sala", "Sala Light", "ON", "", 0x03);
    sim_add(ENTITY_COVER, "cover.garagem", "Garagem Door", "CLSD", "0", 0x45);
    sim_add(ENTITY_SENSOR, "sensor.temperatura", "Temperatura", "23.8", "C", 0x20);
    sim_add(ENTITY_SENSOR, "sensor.umidade", "Umidade", "54.0", "%", 0x20);
    sim_add(ENTITY_SWITCH, "switch.cafeteira", "Cafeteira", "OFF", "", 0x01);
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
        if (strcmp(e->state, "ON") == 0)
            strcpy(e->state, "OFF");
        else
            strcpy(e->state, "ON");
        return 1;
    }
    if (command == 2 && e->domain == ENTITY_COVER) {
        if (strcmp(e->state, "CLSD") == 0) {
            strcpy(e->state, "OPEN");
            strcpy(e->value, "100");
        } else {
            strcpy(e->state, "CLSD");
            strcpy(e->value, "0");
        }
        return 1;
    }
#endif

    return 0;
}
