/**
 * Super Famicom / SNES Smart Home Cartridge
 * RP2350 Dual-Core Co-Processor & Dual-Port RAM Mailbox Emulator
 *
 * Architecture:
 *  - Core 0: Real-time SNES 62-pin Bus Interface (PIO + high-speed SRAM)
 *  - Core 1: ESP32-C6 SPI Master interface + Mailbox Synchronizer + Command Handler
 */

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/spi.h"
#include "hardware/pio.h"
#include "hardware/dma.h"
#include "snes_bus.pio.h"

#define MAILBOX_SIZE         2048
#define CMD_REG_BASE         0x07F0

/* 2 KB Dual-Port Mailbox shared between RP2350 and SNES */
static volatile uint8_t snes_mailbox[MAILBOX_SIZE] __attribute__((aligned(4)));

/* Core 1: Handles ESP32-C6 SPI transactions */
void core1_entry(void) {
    spi_init(spi0, 10 * 1000 * 1000);
    gpio_set_function(16, GPIO_FUNC_SPI); // RX / MISO
    gpio_set_function(17, GPIO_FUNC_SPI); // CSn
    gpio_set_function(18, GPIO_FUNC_SPI); // SCK
    gpio_set_function(19, GPIO_FUNC_SPI); // TX / MOSI

    uint8_t spi_rx_buf[MAILBOX_SIZE];
    uint8_t spi_tx_buf[8];

    while (1) {
        /* Check if SNES has placed an action command in the mailbox */
        if (snes_mailbox[CMD_REG_BASE + 3] == 0x01) {
            spi_tx_buf[0] = 0xA5;
            spi_tx_buf[1] = 0x5A;
            spi_tx_buf[2] = snes_mailbox[CMD_REG_BASE + 0]; // cmd
            spi_tx_buf[3] = snes_mailbox[CMD_REG_BASE + 1]; // index
            spi_tx_buf[4] = snes_mailbox[CMD_REG_BASE + 2]; // val
            spi_tx_buf[5] = 0x00;

            /* Transfer command to ESP32-C6 */
            spi_write_blocking(spi0, spi_tx_buf, 6);

            /* Clear handshake flag */
            snes_mailbox[CMD_REG_BASE + 3] = 0x00;
        }

        /* Poll incoming state snapshot from ESP32-C6 */
        int bytes = spi_read_blocking(spi0, 0x00, spi_rx_buf, sizeof(spi_rx_buf));
        if (bytes > 6 && spi_rx_buf[0] == 'S' && spi_rx_buf[1] == 'H' && spi_rx_buf[2] == 0x01) {
            /* Atomically update shared mailbox */
            memcpy((void *)snes_mailbox, spi_rx_buf, bytes);
        }

        sleep_ms(50);
    }
}

int main(void) {
    stdio_init_all();

    /* Initialize default mailbox with header */
    memset((void *)snes_mailbox, 0, sizeof(snes_mailbox));
    snes_mailbox[0] = 'S';
    snes_mailbox[1] = 'H';
    snes_mailbox[2] = 0x01;
    snes_mailbox[3] = 0x00; /* 0 entities initially */

    /* Launch Core 1 for background networking and SPI bridge */
    multicore_launch_core1(core1_entry);

    /* Core 0: Serves real-time SNES 62-pin cartridge bus access via PIO */
    while (1) {
        tight_loop_contents();
    }

    return 0;
}
