#include <snes.h>
#include "ui.h"

int main(void) {
    ui_init();
    setMode(BG_MODE1, 0);
    bgSetDisable(1);
    bgSetDisable(2);
    setScreenOn();

    while (1) {
        ui_update();
        WaitForVBlank();
    }
    return 0;
}
