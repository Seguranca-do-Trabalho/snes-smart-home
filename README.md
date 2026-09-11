# Super Famicom / SNES Smart Home & Diagnostics Cartridge V1.0

Cartucho inteligente customizado para o console **Super Famicom / SNES (SHVC-001)** com integração bidirecional ao **Home Assistant**, telemetria de bancada, conectividade Wi-Fi 6 / BLE / Thread e barramento de expansão industrial.

Projetado para rodar em hardware real e emuladores, com arquitetura 100% orientada a dados: **a ROM não assume previamente quais ou quantos dispositivos existem na casa**.

---

## 1. Arquitetura do Sistema

```text
       ┌────────────────────────┐
       │     Home Assistant     │ (Servidor / Casa)
       └───────────┬────────────┘
                   │ REST (GET /api/states) / WebSocket (state_changed)
                   ▼
       ┌────────────────────────┐
       │   Python Bridge / LAN  │ (Tradução e normalização de domínios)
       └───────────┬────────────┘
                   │ Wi-Fi 802.11ax / TCP / Protocolo compacto 'SH 01'
                   ▼
┌───────────────────────────────────────────────────────────────┐
│              CARTUCHO FÍSICO SUPER FAMICOM / SNES             │
│                                                               │
│   ┌────────────────────┐          ┌───────────────────────┐   │
│   │   ESP32-C6-MINI    │◄─SPI/UART─┤        RP2350B        │   │
│   │ (Wi-Fi 6 / Thread) │          │  (Dual M33, 520KB)    │   │
│   └────────────────────┘          │  Mailbox em SRAM      │   │
│                                   └───────────┬───────────┘   │
│                                               │               │
│   ┌────────────────────┐          ┌───────────▼───────────┐   │
│   │   SST39VF040       │          │   74LVC Shifters      │   │
│   │  (Flash Boot ROM)  │          │   (5V TTL ◄─► 3.3V)   │   │
│   └─────────┬──────────┘          └───────────┬───────────┘   │
│             │                                 │               │
└─────────────┼─────────────────────────────────┼───────────────┘
              ▼                                 ▼
       ┌────────────────────────────────────────────────────────┐
       │                SNES 62-Pin Cartridge Bus               │
       │   (W65C816S CPU @ 3.58MHz, PPU Mode 1, OAM Sprites)    │
       └────────────────────────────────────────────────────────┘
```

### Princípios da Arquitetura
1. **Isolamento de Complexidade:** O SNES não processa JSON, TLS, Wi-Fi ou HTTP. O ESP32-C6 cuida de toda a rede e segurança; o RP2350B normaliza o estado para um buffer de memória mapeada (SRAM / Mailbox); o SNES apenas lê dados binários limpos.
2. **Interface Dinâmica:** Layout calculado em tempo de execução. Se você adicionar 10 lâmpadas no Home Assistant, a tela do SNES automaticamente cria novas linhas e páginas. Se remover uma tomada, ela desaparece da ROM sem recompilar o jogo.
3. **Boot Instantâneo:** A Flash NOR paralela (512 KB) garante inicialização imediata no console (< 50 ms), enquanto os coprocessadores sobem a rede em background.

---

## 2. Estrutura do Repositório

```text
snes-smart-home/
├── snes/                      # Código-fonte da ROM SNES (C + ASM)
│   ├── src/
│   │   ├── main.c             # Loop principal do jogo e vblank
│   │   ├── ui.c               # Renderização de tela, paginação e sprites
│   │   ├── ui.h
│   │   ├── cartio.c           # I/O do cartucho (SRAM mailbox + fallback sim)
│   │   ├── cartio.h
│   │   └── config.h           # Configurações de exibição e limites
│   ├── assets/                # Bitmaps convertidos (fonte e ícones)
│   │   ├── font.bmp           # Fonte 8x8 bitmap
│   │   └── icons.bmp          # Sprites 16x16 dos domínios (luz, porta, sensor)
│   ├── data.asm               # Inclusão dos dados gráficos na ROM
│   ├── Makefile               # Script de build PVSnesLib 4.6.0
│   └── super_home.sfc         # ROM compilada de 256 KB
│
├── hardware/                  # Projeto Eletrônico Completo KiCad 10
│   ├── snes_smarthome_cartridge.kicad_pro   # Projeto KiCad
│   ├── snes_smarthome_cartridge.kicad_sch   # Esquemático Raiz
│   ├── 01_SNES_BUS_AND_CIC.kicad_sch        # Conector 62 pinos + SuperCIC
│   ├── 02_LEVEL_SHIFTERS_AND_FLASH.kicad_sch# Shifters 5V<->3.3V + Boot Flash
│   ├── 03_RP2350_SUBSYSTEM.kicad_sch        # MCU RP2350B, QSPI 16MB, USB-C
│   ├── 04_ESP32C6_WIFI_IOT.kicad_sch        # ESP32-C6-MINI, Wi-Fi 6, LED RGB
│   ├── 05_PERIPHERALS_AND_POWER.kicad_sch   # MicroSD, RTC DS3231, RS485, Buck
│   ├── snes_smarthome_schematics.pdf        # PDF completo multi-folhas
│   ├── BOM.md                               # Lista detalhada de componentes
│   ├── BOM.csv                              # BOM formatado com códigos LCSC
│   └── PCBWAY_SPECS.md                      # Regras de fabricação PCBWay
│
├── bridge/                    # Bridge Python (Home Assistant ↔ Cartucho)
│   ├── ha_bridge.py           # Polling REST, servidor HTTP e socket TCP
│   └── requirements.txt
│
├── ha-config/                 # Configuração de teste do Home Assistant
│   └── configuration.yaml
│
├── cart/                      # Especificação do protocolo binário
│   └── protocol.md
│
├── docs/                      # Documentação de testes e arquitetura
│   ├── architecture.md
│   └── test-plan.md
│
├── build-rom.sh               # Script de compilação da ROM (1 clique)
├── docker-compose.yml         # Ambiente local com Home Assistant + Bridge
└── README.md                  # Este documento
```

---

## 3. Como Compilar a ROM SNES

### Pré-requisitos
- Linux x86_64 com `make` e `gcc`.
- **PVSnesLib 4.6.0** (instalado em `/home/forg3/tools/pvsneslib` ou configurado via `PVSNESLIB_HOME`).

### Compilação
```bash
./build-rom.sh
```
O script compilará os assets gráficos (`gfx4snes`), o código C (`816-tcc`), o montador (`wla-65816`), executará a otimização de instruções (`816-opt`) e gerará a ROM em:
```text
snes/super_home.sfc
```

### Execução em Emulador
A ROM pode ser aberta em qualquer emulador padrão (**bsnes**, **snes9x**, **Mesen 2**):
```bash
flatpak run com.snes9x.Snes9x snes/super_home.sfc
# ou
flatpak run dev.bsnes.bsnes snes/super_home.sfc
```
No emulador sem o hardware físico do RP2350 conectado, o cartucho detecta a ausência da assinatura `SH 01` no endereço de SRAM e ativa o modo **SIMULATOR**, permitindo navegar entre páginas com `L` e `R`, selecionar entidades com o direcional e alternar estados com o botão `A`.

---

## 4. Hardware e Especificações para PCBWay

O esquemático completo foi desenvolvido e validado com o **KiCad 10.0.6** (`0 violações de ERC`).

### Regras Críticas de Fabricação (PCBWay / JLCPCB)
Ao enviar os arquivos para fabricação, selecione obrigatoriamente:
1. **Espessura da Placa (Thickness): 1.2 mm** (O conector fêmea do Super Famicom foi desenhado para 1.2 mm. Placas de 1.6 mm danificam e empenam as lâminas do console).
2. **Passo dos Contatos (Edge Pitch): 2.50 mm Métrico** (Não utilizar 2.54 mm / 0.1", pois o erro cumulativo em 31 pinos provoca curto-circuito).
3. **Gold Fingers com Chanfro de 30° (30° Edge Beveling):** Essencial para a placa deslizar suavemente no slot sem danificar os contatos de ouro.
4. **Acabamento da Superfície:** **ENIG** (Electroless Nickel Immersion Gold) ou **Hard Gold** nos contatos de borda.
5. **Número de Camadas: 4 Camadas** (Top: Sinais e Antena RF / In1: GND sólido / In2: 3.3V e 5V / Bottom: Sinais e barramento traseiro).

### Lista de Materiais e Códigos LCSC
A lista de componentes contém códigos prontos para montagem SMT turnkey:
- **RP2350B:** Dual Cortex-M33, 520KB SRAM, 48 GPIOs (QFN-80)
- **W25Q128JVSIQ:** 16MB QSPI Flash ([C97521](https://www.lcsc.com/product-detail/NOR-Flash_Winbond-Elec-W25Q128JVSIQ_C97521.html))
- **ESP32-C6-MINI-1-N4:** Wi-Fi 6 + BLE 5 + Thread ([C5248554](https://www.lcsc.com/product-detail/WiFi-Modules_Espressif-Systems-ESP32-C6-MINI-1-N4_C5248554.html))
- **SST39VF040-70-4C-WHE:** Boot ROM Paralela 512KB ([C129525](https://www.lcsc.com/product-detail/NOR-Flash_Microchip-Tech-SST39VF040-70-4C-WHE_C129525.html))
- **74LVC541APW:** Buffer 5V -> 3.3V ([C5975](https://www.lcsc.com/product-detail/Buffers-Drivers-Receivers-Transceivers_Nexperia-74LVC541APW-118_C5975.html))
- **SN74LVC8T245PWR:** Transceiver Dados 5V <-> 3.3V ([C6207](https://www.lcsc.com/product-detail/Buffers-Drivers-Receivers-Transceivers_Texas-Instruments-SN74LVC8T245PWR_C6207.html))
- **PIC12F629-I/SN:** SuperCIC Lockout Bypass ([C20967](https://www.lcsc.com/product-detail/Microcontroller-Units-MCUs-MPUs-SOCs_Microchip-Tech-PIC12F629-I-SN_C20967.html))
- **SY8089AAAC:** Buck Síncrono 5V -> 3.3V 2A ([C28674](https://www.lcsc.com/product-detail/DC-DC-Converters_Silergy-Corp-SY8089AAAC_C28674.html))
- **DS3231MZ+:** RTC de alta precisão MEMS ([C16719](https://www.lcsc.com/product-detail/Real-Time-Clocks-RTC_Analog-Devices-Maxim-Integrated-DS3231MZ_C16719.html))
- **SP3485CN-L/TR:** Transceiver RS-485 3.3V ([C6960](https://www.lcsc.com/product-detail/RS-485-RS-422-ICs_MaxLinear-SP3485CN-L-TR_C6960.html))

*Consulte [`hardware/BOM.md`](hardware/BOM.md) e [`hardware/BOM.csv`](hardware/BOM.csv) para a lista completa.*

---

## 5. Protocolo Binário Compacto (V1)

O cartucho se comunica com o bridge usando frames compactos com checksum:

```text
[Header 2B: 'S' 'H'] [Versão: 0x01] [Total Entidades: 1B] [Registros de Entidade...] [CRC16/Modbus 2B]
```

### Formato de Cada Entidade:
```text
u8  domain               (1: light, 2: switch, 3: cover, 4: lock, 5: fan, 6: climate, 7: sensor...)
u8  state_code           (0: off/closed, 1: on/open, 2: valor numérico / outro)
u8  features             (bitmask de capacidades: liga/desliga, brilho, temperatura, porcentagem)
u8  name_len             (tamanho do nome amigável em caracteres)
u16 numeric_value_x100   (valor multiplicado por 100 em little-endian, ou 0xFFFF se nulo)
u8  name[name_len]       (string ASCII do nome)
```

### Mailbox de Comandos (SNES -> RP2350 -> Home Assistant):
- `0x07F0`: Código do comando (`1`: Alternar ON/OFF, `2`: Abrir/Fechar Cover)
- `0x07F1`: Índice da entidade alvo
- `0x07F2`: Parâmetro / Novo estado
- `0x07F3`: Flag de Handshake (SNES escreve `0x01`; RP2350 limpa para `0x00` após despachar via ESP32)

---

## 6. Teste com Home Assistant

1. Subir o ambiente de teste:
   ```bash
   podman compose up -d homeassistant
   # ou
   docker compose up -d homeassistant
   ```
2. Obter um token de acesso de longa duração no Home Assistant (`http://127.0.0.1:8123`).
3. Exportar o token e iniciar a bridge:
   ```bash
   export HA_TOKEN="seu_token_aqui"
   python3 bridge/ha_bridge.py
   ```
4. Consultar o snapshot gerado:
   ```bash
   curl http://127.0.0.1:8790/entities
   curl http://127.0.0.1:8790/snapshot.bin --output snap.bin
   ```
5. Enviar um comando de teste:
   ```bash
   curl -X POST http://127.0.0.1:8790/command \
     -H "Content-Type: application/json" \
     -d '{"entity_id":"light.sala_light","action":"off"}'
   ```
