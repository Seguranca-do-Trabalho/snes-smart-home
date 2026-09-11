# Cartucho ↔ Home Assistant protocol V1

A ROM não fala HTTP, JSON, TLS ou MQTT. O MCU do cartucho faz isso e entrega à ROM um snapshot compacto.

## Entity record

```text
u8  domain
u8  state_code
u8  features
u8  name_len
u16 numeric_value_x100   ; 0xFFFF = sem valor
u8  name[name_len]
```

Domains: 1 light, 2 switch, 3 cover, 4 lock, 5 fan, 6 climate, 7 sensor, 8 binary_sensor, 9 media_player, 255 other.

Feature bits: bit0 on/off, bit1 brightness, bit2 open/close, bit3 lock/unlock, bit4 set_value, bit5 temperature, bit6 percentage.

## Snapshot

`53 48 01 COUNT RECORDS CRC16` — CRC16/Modbus, little-endian.

## Commands

`01 SET_ON_OFF`, `02 SET_OPEN_CLOSE`, `03 SET_VALUE`, `04 REQUEST_REFRESH`.

A UI nunca assume que existe uma luz ou porta. A lista é a única fonte para renderização.
