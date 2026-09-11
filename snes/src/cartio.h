#ifndef CARTIO_H
#define CARTIO_H
#include <snes.h>
#include "config.h"
typedef enum { ENTITY_LIGHT=1, ENTITY_SWITCH=2, ENTITY_COVER=3, ENTITY_LOCK=4, ENTITY_FAN=5, ENTITY_CLIMATE=6, ENTITY_SENSOR=7, ENTITY_BINARY_SENSOR=8, ENTITY_MEDIA=9, ENTITY_OTHER=255 } EntityDomain;
typedef struct { u8 used; u8 domain; u8 state_code; u8 features; u16 numeric_value; char entity_id[32]; char name[MAX_NAME_LEN+1]; char state[MAX_STATE_LEN+1]; char value[MAX_VALUE_LEN+1]; } Entity;
void cartio_init(void); void cartio_refresh(void); u8 cartio_count(void); Entity *cartio_entity(u8 index); u8 cartio_command(u8 index, u8 command);
#endif
