# Cartridge ↔ Home Assistant protocol V1

The ROM does not speak HTTP, JSON, TLS, or MQTT. The cartridge MCU handles that and delivers a compact snapshot to the ROM.

## Entity record

```text
u8  domain
u8  state_code
u8  features
u8  name_len
u16 numeric_value_x100   ; 0xFFFF = no value
u8  name[name_len]
```

Domains: 1 light, 2 switch, 3 cover, 4 lock, 5 fan, 6 climate, 7 sensor, 8 binary_sensor, 9 media_player, 255 other.

Feature bits: bit0 on/off, bit1 brightness, bit2 open/close, bit3 lock/unlock, bit4 set_value, bit5 temperature, bit6 percentage.

## Snapshot

`53 48 01 COUNT RECORDS CRC16` — CRC16/Modbus, little-endian.

## Commands

`01 SET_ON_OFF`, `02 SET_OPEN_CLOSE`, `03 SET_VALUE`, `04 REQUEST_REFRESH`.

The UI never assumes that a light or door exists. The list is the sole source for rendering.
