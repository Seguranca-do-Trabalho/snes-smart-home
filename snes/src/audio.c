#include "audio.h"
#include "soundbank.h"

extern char SOUNDBANK__;

void audio_init(void) {
    spcBoot();
    spcSetBank(&SOUNDBANK__);
    spcStop();
    spcLoadEffect(0); /* Tada / confirmation chime */
    spcLoadEffect(3); /* Marimba percussive click */
    spcLoadEffect(4); /* Cowbell / action tap */
    /* Play gentle startup sound */
    spcEffect(6, 0, 14 * 16 + 8);
}

void audio_process(void) {
    spcProcess();
}

void audio_play_nav(void) {
    /* Crisp marimba click when moving cursor */
    spcEffect(8, 3, 14 * 16 + 8);
}

void audio_play_toggle(u8 on) {
    if (on) {
        /* Cheerful upward chime on activation */
        spcEffect(7, 0, 15 * 16 + 8);
    } else {
        /* Deeper tone on turn off */
        spcEffect(3, 4, 14 * 16 + 8);
    }
}

void audio_play_action(void) {
    spcEffect(5, 4, 15 * 16 + 8);
}

void audio_play_page(void) {
    /* Page flip acoustic click */
    spcEffect(5, 3, 15 * 16 + 8);
}

void audio_play_refresh(void) {
    spcEffect(6, 0, 12 * 16 + 8);
}
