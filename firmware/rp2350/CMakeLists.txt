cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(snes_rp2350_bus C CXX ASM)
pico_sdk_init()

add_executable(snes_rp2350_bus
    main.c
)

pico_generate_pio_header(snes_rp2350_bus ${CMAKE_CURRENT_LIST_DIR}/snes_bus.pio)

target_link_libraries(snes_rp2350_bus
    pico_stdlib
    pico_multicore
    hardware_spi
    hardware_pio
    hardware_dma
)

pico_add_extra_outputs(snes_rp2350_bus)
