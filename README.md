# Super Famicom / SNES Smart Home & Diagnostics Cartridge V1.0

Cartucho inteligente customizado para o console **Super Famicom / SNES (SHVC-001)** com integração bidirecional ao **Home Assistant**, telemetria de bancada, conectividade Wi-Fi 6 / BLE / Thread e barramento de expansão industrial.

Projetado para rodar em hardware real e emuladores, com arquitetura 100% orientada a dados: **a ROM não assume previamente quais ou quantos dispositivos existem na casa**.

---

## 📷 Fotos e Telas da ROM no Super Nintendo

| Página 1: Iluminação, Garagem, Clima e Fan | Página 2: Fechadura, Spotify, Alarme e Switch |
|:---:|:---:|
| ![Página 1](docs/screenshots/snes_smarthome_page1.png) | ![Página 2](docs/screenshots/snes_smarthome_page2.png) |

### Simulação CRT Arcade Retrô (Scanlines & PVM Phosphor)
![Visão CRT](docs/screenshots/snes_smarthome_crt.png)

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
├── snes/                      # Código-fonte da ROM SNES (C + 65816 Assembly)
│   ├── src/
│   │   ├── main.c             # Loop principal do jogo e vblank (C)
│   │   ├── ui.c               # Renderização de tela, 8 paletas CGRAM, paginação e sprites (C)
│   │   ├── ui.h
│   │   ├── audio.c            # Driver de som SPC700 (C)
│   │   ├── audio.h
│   │   ├── cart_hw.asm        # Driver de baixo nível do barramento em 65816 Assembly Puro
│   │   ├── cart_hw.h          # Header C para chamadas de rotinas ASM
│   │   ├── cartio.c           # I/O do cartucho (SRAM mailbox + fallback sim) (C)
│   │   ├── cartio.h
│   │   └── config.h           # Configurações de exibição, limites e fallback SIMULATOR
│   ├── assets/                # Bitmaps convertidos (fonte e ícones)
│   │   ├── font.bmp           # Fonte 8x8 bitmap
│   │   ├── icons.bmp          # 20 Sprites 16x16 dos domínios (lâmpada, porta, fan, etc.)
│   │   └── make_icons.py      # Gerador procedural da folha de sprites 16x320
│   ├── res/                   # Recursos de áudio para smconv
│   │   └── soundbank.it       # Tracker ImpulseTracker com samples e SFX
│   ├── data.asm               # Inclusão dos dados gráficos na ROM (WLA-DX)
│   ├── Makefile               # Script de build PVSnesLib 4.6.0 com smconv
│   └── super_home.sfc         # ROM compilada de 256 KB (LoROM SlowROM)
│
├── firmware/                  # Firmware dos Coprocessadores do Cartucho
│   ├── esp32/                 # Gateway Wi-Fi 6 / Thread (C / ESP-IDF)
│   │   ├── main/main.c        # Cliente REST Home Assistant + Master SPI
│   │   └── CMakeLists.txt
│   └── rp2350/                # Emulador de Barramento SNES 62-pinos (C + PIO Assembly)
│       ├── main.c             # Gerenciamento Dual-Core M33 e Mailbox SRAM
│       ├── snes_bus.pio       # Máquina de estados PIO para ciclos /RD e /WR (<120ns)
│       └── CMakeLists.txt
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
├── tests/                     # Suite de Testes Automatizados (Python)
│   └── test_system.py         # Testes de integridade da ROM, protocolo e mailbox
│
├── docs/                      # Documentação de testes, capturas e arquitetura
│   ├── screenshots/           # Fotos e capturas da tela em alta resolução
│   ├── architecture.md
│   └── test-plan.md
│
├── scripts/                   # Utilitários de renderização e build
│   └── generate_screenshots.py# Gerador de screenshots pixel-perfect e CRT
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

### Recursos Audiovisuais da ROM

#### 1. Sprites e Animações Pixel Art (16×16 OAM)
A folha de sprites possui 20 ícones temáticos (`snes/assets/icons.bmp` gerados via `make_icons.py`):
- **Luz (`light`):** Lâmpada incandescente apagada vs. acesa com raios radiantes dourados.
- **Interruptor (`switch`):** Rocker switch industrial com LED indicador verde.
- **Garagem / Portão (`cover`):** Portão fechado vs. aberto com carro esportivo retrô estilizado.
- **Fechadura (`lock`):** Cadeado fechado (trancado) vs. manilha aberta (destrancado).
- **Ventilador (`fan`):** Hélice de 4 pás que **gira em tempo real** alternando entre 0° e 45° quando ligado.
- **Climatização (`climate`):** Floco de neve para refrigeração / frio vs. chama alaranjada para aquecimento (> 24°C).
- **Sensores (`sensor`):** Gota azul para umidade (%) vs. raio de energia para potência/volts vs. termômetro.
- **Segurança (`binary_sensor`):** Escudo verde em estado seguro vs. triângulo de advertência em alerta.
- **Mídia (`media_player`):** Alto-falante em pausa vs. equalizador com notas musicais quando em reprodução.
- **Cursor Dinâmico:** Seta indicadora com animação de 2 frames e efeito bounce senoidal à esquerda do dispositivo selecionado.

#### 2. Efeitos Sonoros SPC700 (Sony DSP)
O cartucho integra um soundbank Tracker (`snes/res/soundbank.it` compilado via `smconv` no banco de ROM 5):
- `UP` / `DOWN`: Marimba percussiva nítida ao mover o cursor.
- `L` / `R`: Clique acústico tátil ao mudar de página.
- `A` (Ligar): Chime melódico ascendente ao acionar/abrir um dispositivo.
- `A` (Desligar): Tap em tom grave ao desativar/fechar.
- `B` (Polling): Chime suave de sincronização com o Home Assistant.

#### 3. Paletas de Texto Coloridas (BG Mode 1 - 8 Paletas CGRAM)
Os textos dos dispositivos recebem cores semânticas conforme tipo e estado:
- **Ouro (`PAL_GOLD`):** Título principal, item selecionado e indicador de página.
- **Ciano Elétrico (`PAL_CYAN`):** Temperatura fria (< 21°C) e umidade (%).
- **Laranja Fogo (`PAL_ORANGE`):** Temperatura quente (> 25°C) e alertas de sensores.
- **Verde Esmeralda (`PAL_GREEN`):** Estados `"ON"`, `"OPEN"`, `"UNLKD"` e conforto térmico (21°C a 25°C).
- **Cinza Neutro (`PAL_GRAY`):** Estados desligados (`"OFF"`, `"CLSD"`, `"LOCKD"`).
- **Roxo Neon (`PAL_PURPLE`):** Dispositivos de mídia (`"PLAY"`).
- **Âmbar (`PAL_AMBER`):** Contadores de dispositivos e avisos.

### Arquitetura da ROM (C + 65816 Assembly Puro)
A ROM utiliza uma estrutura híbrida de alto e baixo nível:
- **C (`816-tcc`):** Gerenciamento de interface gráfica, paginação dinâmica, animações, renderização de fontes e máquinas de estados (`snes/src/main.c`, `snes/src/ui.c`, `snes/src/audio.c`).
- **65816 Assembly Puro (`wla-65816`):** O módulo [`snes/src/cart_hw.asm`](snes/src/cart_hw.asm) implementa rotinas de baixo nível com endereçamento longo de 24 bits (`$700000` a `$7007FF`):
  - `cart_hw_probe()`: Sonda atômica da assinatura `'S', 'H', 0x01` no barramento SRAM do cartucho.
  - `cart_hw_send_cmd()`: Escrita atômica nos registradores de comando do RP2350 (`0x07F0..0x07F3`) com barreira de memória e flag de handshake.
  - `data.asm`: Alocação dos bancos de dados gráficos em `.rodata1`.

### Firmwares dos Coprocessadores
Para garantir comunicação sem sobrecarregar a CPU do SNES, o cartucho conta com coprocessadores dedicados:
1. **ESP32-C6 (`firmware/esp32/` - C / ESP-IDF):**
   - Conecta-se à rede Wi-Fi 6 (802.11ax).
   - Realiza polling no Home Assistant Bridge (`/snapshot.bin`) ou assina streams TCP.
   - Valida integridade via CRC16 Modbus.
   - Envia snapshots e recebe comandos da SNES via barramento SPI a 10 MHz.
2. **RP2350B (`firmware/rp2350/` - C + PIO Assembly):**
   - **Core 0 + PIO (`snes_bus.pio`):** Emula SRAM de porta dupla respondendo aos ciclos `/RD` e `/WR` do barramento de 62 pinos do SNES em menos de 120 ns.
   - **Core 1:** Sincroniza buffers com o ESP32 via SPI e despacha comandos gerados pelo jogador.

### Testes Automatizados da ROM e Protocolo
O repositório inclui uma suite completa de testes automatizados em Python:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
Os testes cobrem:
- Integridade binária da ROM de 256 KB e cálculo de checksum complement do cabeçalho LoROM.
- Serialização e deserialização do protocolo binário compacto (`SH\x01`) e validação do algoritmo CRC16/Modbus (`0xA001`).
- Mapeamento e normalização de domínios e serviços do Home Assistant.
- Alinhamento dos offsets de registradores de comando na memória do cartucho.

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
