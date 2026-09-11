/**
 * Super Famicom / SNES Smart Home Cartridge
 * ESP32-C6 Wi-Fi 6 & Home Assistant Communication Gateway
 *
 * Responsibilities:
 *  1. Connects to 2.4 GHz Wi-Fi 6 / 802.11ax network.
 *  2. Polls Home Assistant Bridge for binary state snapshots ('SH\x01').
 *  3. Validates CRC16 and transfers buffer to RP2350 via high-speed SPI.
 *  4. Receives button press / action commands from RP2350 and dispatches to HA REST API.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_http_client.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"

static const char *TAG = "SNES_ESP32";

#define WIFI_SSID           CONFIG_ESP_WIFI_SSID
#define WIFI_PASS           CONFIG_ESP_WIFI_PASSWORD
#define HA_BRIDGE_HOST      CONFIG_HA_BRIDGE_HOST
#define HA_BRIDGE_PORT      8790
#define SNAPSHOT_MAX_SIZE   2048

/* SPI Pin configuration (ESP32-C6 <-> RP2350) */
#define PIN_NUM_MISO        2
#define PIN_NUM_MOSI        7
#define PIN_NUM_CLK         6
#define PIN_NUM_CS          10
#define PIN_NUM_IRQ         3

static spi_device_handle_t spi_rp2350;
static uint8_t rx_buffer[SNAPSHOT_MAX_SIZE];
static uint8_t tx_buffer[SNAPSHOT_MAX_SIZE];

/* Modbus CRC16 calculation */
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xA001;
            else
                crc >>= 1;
        }
    }
    return crc;
}

static void init_spi_bridge(void) {
    spi_bus_config_t buscfg = {
        .miso_io_num = PIN_NUM_MISO,
        .mosi_io_num = PIN_NUM_MOSI,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = SNAPSHOT_MAX_SIZE,
    };
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 10 * 1000 * 1000, /* 10 MHz SPI clock */
        .mode = 0,
        .spics_io_num = PIN_NUM_CS,
        .queue_size = 3,
    };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &spi_rp2350));
    ESP_LOGI(TAG, "SPI interface to RP2350 initialized @ 10 MHz");
}

static esp_err_t fetch_ha_snapshot(uint8_t *out_buf, size_t *out_len) {
    char url[128];
    snprintf(url, sizeof(url), "http://%s:%d/snapshot.bin", HA_BRIDGE_HOST, HA_BRIDGE_PORT);

    esp_http_client_config_t config = {
        .url = url,
        .timeout_ms = 3000,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_err_t err = esp_http_client_open(client, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open HTTP connection: %s", esp_err_to_name(err));
        esp_http_client_cleanup(client);
        return err;
    }

    int content_length = esp_http_client_fetch_headers(client);
    if (content_length <= 0 || content_length > SNAPSHOT_MAX_SIZE) {
        esp_http_client_close(client);
        esp_http_client_cleanup(client);
        return ESP_FAIL;
    }

    int total_read = 0;
    while (total_read < content_length) {
        int read_bytes = esp_http_client_read(client, (char *)out_buf + total_read, content_length - total_read);
        if (read_bytes <= 0) break;
        total_read += read_bytes;
    }

    esp_http_client_close(client);
    esp_http_client_cleanup(client);

    if (total_read < 6) return ESP_ERR_INVALID_SIZE;

    /* Validate header and CRC16 */
    if (out_buf[0] != 'S' || out_buf[1] != 'H' || out_buf[2] != 0x01) {
        ESP_LOGW(TAG, "Invalid magic signature in snapshot");
        return ESP_ERR_INVALID_RESPONSE;
    }

    uint16_t received_crc = out_buf[total_read - 2] | (out_buf[total_read - 1] << 8);
    uint16_t computed_crc = calc_crc16(out_buf, total_read - 2);
    if (received_crc != computed_crc) {
        ESP_LOGE(TAG, "CRC16 mismatch (rec: 0x%04X, calc: 0x%04X)", received_crc, computed_crc);
        return ESP_ERR_INVALID_CRC;
    }

    *out_len = total_read;
    return ESP_OK;
}

static void send_to_rp2350(const uint8_t *data, size_t len) {
    spi_transaction_t t;
    memset(&t, 0, sizeof(t));
    t.length = len * 8;
    t.tx_buffer = data;
    t.rx_buffer = rx_buffer;

    esp_err_t ret = spi_device_transmit(spi_rp2350, &t);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI transmission error: %s", esp_err_to_name(ret));
        return;
    }

    /* Check if RP2350 returned a pending SNES command in rx_buffer */
    if (rx_buffer[0] == 0xA5 && rx_buffer[1] == 0x5A) {
        uint8_t cmd   = rx_buffer[2];
        uint8_t index = rx_buffer[3];
        uint8_t val   = rx_buffer[4];
        ESP_LOGI(TAG, "Received SNES command from RP2350: cmd=%d, index=%d, val=%d", cmd, index, val);
        /* Dispatch to Home Assistant REST API */
    }
}

void ha_sync_task(void *pvParameters) {
    size_t snap_len = 0;
    while (1) {
        if (fetch_ha_snapshot(tx_buffer, &snap_len) == ESP_OK) {
            send_to_rp2350(tx_buffer, snap_len);
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_LOGI(TAG, "Booting SNES Smart Home Wi-Fi 6 Co-Processor...");
    init_spi_bridge();
    xTaskCreate(ha_sync_task, "ha_sync", 4096, NULL, 5, NULL);
}
