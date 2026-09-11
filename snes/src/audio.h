#ifndef AUDIO_H
#define AUDIO_H

#include <snes.h>

void audio_init(void);
void audio_process(void);
void audio_play_nav(void);
void audio_play_toggle(u8 on);
void audio_play_action(void);
void audio_play_page(void);
void audio_play_refresh(void);

#endif
