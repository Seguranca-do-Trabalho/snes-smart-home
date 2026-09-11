#ifndef CART_HW_H
#define CART_HW_H

#include <snes.h>

/**
 * Probes the hardware mailbox at $700000 for signature 'S', 'H', 0x01.
 * Implemented in pure 65816 Assembly (cart_hw.asm).
 * @return 1 if cartridge hardware is detected, 0 otherwise.
 */
u8 cart_hw_probe(void);

/**
 * Sends a command to the RP2350 coprocessor via memory-mapped I/O at $7007F0.
 * Implemented in pure 65816 Assembly (cart_hw.asm).
 * @param cmd   Command code (1: toggle ON/OFF, 2: cover, 3: lock, 4: media, 5: climate)
 * @param index Entity index
 * @param val   New state value / parameter
 */
void cart_hw_send_cmd(u8 cmd, u8 index, u8 val);

#endif /* CART_HW_H */
